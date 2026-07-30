import json
import random
import os
import sys
import collections
import importlib
import numpy as np
import itertools
from concurrent.futures import ProcessPoolExecutor
from statsmodels.stats.multitest import multipletests
import scipy.stats as stats

sys.path.insert(0, os.getcwd())
from infrastructure.runner.loader import load_constraint_set
from infrastructure.runner.system import SystemPhysics
from infrastructure.evolution.genome import CognitiveGenome

def evaluate_resilience(args):
    seed, beta, decay, shock_type, intensity, env_file = args
    exp_module = importlib.import_module("experiments.E019C_Cognitive")
    
    constraints = load_constraint_set(env_file.replace(".json", ""))
    physics = SystemPhysics(constraints)
    
    genome = CognitiveGenome(alpha=0.5, gamma=0.99, beta=beta, memory_decay_rate=decay, replay_capacity=5000, replay_frequency=4)
    random.seed(seed)
    
    actor = exp_module.Actor(seed=seed, genome=genome)
    
    max_ticks = 4000
    shock_tick = random.randint(int(max_ticks * 0.3), int(max_ticks * 0.7))
    
    state = physics.get_initial_state()
    last_action = None
    last_action_successful = None
    
    work_reward = 10.0
    
    work_history = []
    fitness_history = []
    
    for tick in range(1, max_ticks + 1):
        if tick == shock_tick:
            if shock_type == "physics":
                physics.params["rest_gain"] *= intensity
            elif shock_type == "cost":
                physics.params["work_cost"] *= intensity
            elif shock_type == "resource":
                state["resource"] *= intensity
            elif shock_type == "opportunity":
                work_reward *= intensity

        state = physics.system_tick(state)
        if physics.is_terminal(state):
            # If dead, fitness is 0 for remainder
            work_history.extend([0] * (max_ticks - tick + 1))
            for _ in range(tick, max_ticks + 1):
                fitness_history.append(0.0)
            break
            
        obs = physics.system_observe(state, tick)
        if last_action is not None:
            obs["last_action"] = last_action
            obs["last_action_successful"] = last_action_successful
            
        decision = actor.choose(obs)
        
        is_valid, _ = physics.system_validate(state, decision)
        last_action = decision
        last_action_successful = is_valid
        
        if is_valid:
            state = physics.system_apply(state, decision)
            
        reward = 0.0
        if not is_valid:
            reward = -1.0
        elif decision == "work":
            reward = work_reward
            
        actor.update(str(obs), decision, reward, str(physics.system_observe(state, tick)))
        
        work_history.append(1 if (is_valid and decision == "work") else 0)
        
        # Calculate rolling fitness (work rate over last 200 ticks)
        if len(work_history) >= 200:
            fitness_history.append(sum(work_history[-200:]) / 200.0)
        else:
            fitness_history.append(sum(work_history) / len(work_history))
            
    # Calculate Resilience Metrics
    # Pre-shock fitness (mean of 200 ticks before shock)
    pre_shock_window = fitness_history[max(0, shock_tick-200):shock_tick]
    f_pre = np.mean(pre_shock_window) if pre_shock_window else 0.0
    
    # Post-shock window
    post_shock_window = fitness_history[shock_tick:]
    
    if len(post_shock_window) == 0 or f_pre < 0.05:
        # Agent didn't establish baseline fitness, cannot measure resilience
        return {
            "max_drop": None,
            "relative_drop": None,
            "recovery_time": None,
            "recovery_slope": None,
            "recovery_auc": None
        }
        
    f_min = min(post_shock_window)
    max_drop = f_pre - f_min
    relative_drop = max_drop / f_pre if f_pre > 0 else 0.0
    
    # Recovery Time (ticks until 95% of f_pre)
    recovery_time = max_ticks - shock_tick # Default to max if never recovers
    for i, f in enumerate(post_shock_window):
        if f >= 0.95 * f_pre:
            recovery_time = i
            break
            
    # Recovery Slope (dFitness / dt from f_min to recovery)
    min_idx = np.argmin(post_shock_window)
    if recovery_time > min_idx:
        recovery_slope = (post_shock_window[recovery_time] - f_min) / max(1, recovery_time - min_idx)
    else:
        recovery_slope = 0.0
        
    # Normalized Recovery AUC
    actual_auc = sum(post_shock_window)
    ideal_auc = f_pre * len(post_shock_window)
    norm_auc = actual_auc / ideal_auc if ideal_auc > 0 else 0.0
    
    return {
        "max_drop": max_drop,
        "relative_drop": relative_drop,
        "recovery_time": recovery_time,
        "recovery_slope": recovery_slope,
        "recovery_auc": norm_auc
    }

def run_resilience():
    betas = [0, 8, 20, 40, 100, 300, 500]
    decay = 0.99
    env_file = "ladder_gain/gain_06.json" # Using medium env
    
    shocks = [
        ("physics", 0.8), ("physics", 0.6), ("physics", 0.4),
        ("cost", 1.1), ("cost", 1.3), ("cost", 1.6),
        ("resource", 0.7), ("resource", 0.4), ("resource", 0.1),
        ("opportunity", 1.2), ("opportunity", 1.5)
    ]
    
    seeds = 30 # Fully crossed balanced factorial
    
    out_dir = "results/phase7E"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "resilience_data.jsonl")
    
    points = list(itertools.product(betas, shocks))
    
    completed_points = set()
    if os.path.exists(out_file):
        with open(out_file, "r") as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    completed_points.add((record["beta"], record["shock_type"], record["shock_intensity"], record["seed"]))
                    
    tasks = []
    for beta, (stype, sint) in points:
        for seed in range(seeds):
            if (beta, stype, sint, seed) not in completed_points:
                tasks.append((seed, beta, decay, stype, sint, env_file))
                
    print(f"Points to run: {len(tasks)} / {len(points) * seeds}")
    
    completed_count = 0
    with ProcessPoolExecutor(max_workers=14) as executor:
        futures = {executor.submit(evaluate_resilience, task): task for task in tasks}
        for future in importlib.import_module("concurrent.futures").as_completed(futures):
            task = futures[future]
            seed, beta, _, stype, sint, _ = task
            try:
                res = future.result()
                record = {
                    "seed": seed,
                    "beta": float(beta),
                    "shock_type": stype,
                    "shock_intensity": float(sint),
                    **res
                }
                with open(out_file, "a") as f:
                    f.write(json.dumps(record) + "\n")
                
                completed_count += 1
                if completed_count % 50 == 0:
                    print(f"Progress: {completed_count}/{len(tasks)}")
            except Exception as e:
                print(f"Error on task {task}: {e}")

if __name__ == "__main__":
    run_resilience()
