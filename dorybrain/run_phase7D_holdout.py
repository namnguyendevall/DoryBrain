import json
import random
import os
import sys
import collections
import importlib
import numpy as np
import itertools
from concurrent.futures import ProcessPoolExecutor
from scipy.optimize import curve_fit

sys.path.insert(0, os.getcwd())
from infrastructure.runner.loader import load_constraint_set
from infrastructure.runner.system import SystemPhysics
from infrastructure.evolution.genome import CognitiveGenome

def evaluate_point_seed(args):
    seed, beta, decay, constraint_file, max_ticks = args
    exp_module = importlib.import_module("experiments.E019C_Cognitive")
    
    constraints = load_constraint_set(constraint_file.replace(".json", ""))
    physics = SystemPhysics(constraints)
    
    genome = CognitiveGenome(alpha=0.5, gamma=0.99, beta=beta, memory_decay_rate=decay, replay_capacity=5000, replay_frequency=4)
    random.seed(seed)
    
    actor = exp_module.Actor(seed=seed, genome=genome)
    
    ep4_latency = -1
    work_rate = 0.0
    
    for ep in range(1, 5):
        if ep > 1:
            actor.reset()
            
        state = physics.get_initial_state()
        last_action = None
        last_action_successful = None
        
        invest_tick = -1
        
        for tick in range(1, max_ticks + 1):
            state = physics.system_tick(state)
            if physics.is_terminal(state):
                break
                
            obs = physics.system_observe(state, tick)
            if last_action is not None:
                obs["last_action"] = last_action
                obs["last_action_successful"] = last_action_successful
                
            decision = actor.choose(obs)
            
            if decision == "invest" and invest_tick == -1:
                is_valid, _ = physics.system_validate(state, decision)
                if is_valid:
                    invest_tick = tick
            
            is_valid, _ = physics.system_validate(state, decision)
            last_action = decision
            last_action_successful = is_valid
            
            if is_valid:
                state = physics.system_apply(state, decision)
                
            reward = 0.0
            if not is_valid:
                reward = -1.0
            elif decision == "work":
                reward = 10.0
            
            actor.update(str(obs), decision, reward, str(physics.system_observe(state, tick)))
                
            if physics.is_terminal(state):
                break
                
        actor_state = actor.get_state()
        if ep == 4:
            ep4_latency = actor_state.get("first_investment_tick", -1)
            work_rate = actor_state.get("time_above_50", 0) / float(max_ticks)
            
    norm_adapt = max(0.0, 1.0 - (ep4_latency / max_ticks)) if ep4_latency != -1 else 0.0
    
    return {
        "work_rate": work_rate,
        "adaptation": norm_adapt,
        "discovery": 1.0 if ep4_latency != -1 else 0.0,
        "memory": 1.0 if ep4_latency != -1 and ep4_latency < 500 else 0.0
    }

def logistic(x, L, k, x0):
    return L / (1 + np.exp(-k * (x - x0)))

def calculate_fitness_stats(metrics, weights):
    scores = []
    prob_discovery = 0
    prob_work = 0
    
    for m in metrics:
        s = (m["work_rate"] * weights[0] +
             m["discovery"] * weights[1] +
             m["adaptation"] * weights[2] +
             m["memory"] * weights[3])
        scores.append(s)
        
        if m["discovery"] > 0:
            prob_discovery += 1
        if m["work_rate"] > 0:
            prob_work += 1
            
    scores = np.array(scores)
    mean = float(np.mean(scores)) if len(scores) > 0 else 0.0
    
    return {
        "fitness_mean": mean,
        "p_discovery": prob_discovery / len(metrics),
        "p_work": prob_work / len(metrics),
        "seed_count": len(metrics)
    }

def run_holdout():
    betas = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 40, 100, 300]
    decays = [0.90, 0.95, 0.99]
    envs = ["ladder_gain/gain_05.json", "ladder_gain/gain_06.json", "ladder_gain/gain_07.json"]
    
    seeds = 30
    max_ticks = 2000
    weights = [0.25, 0.25, 0.25, 0.25]
    
    out_dir = "results/phase7D"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "holdout_data.jsonl")
    
    points = list(itertools.product(envs, betas, decays))
    
    # Check what is already completed
    completed_points = set()
    if os.path.exists(out_file):
        with open(out_file, "r") as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    completed_points.add((record["env"], round(record["beta"], 4), round(record["decay"], 4)))
                    
    points_to_run = [(e, b, d) for (e, b, d) in points if (e, round(b, 4), round(d, 4)) not in completed_points]
    print(f"Points to run: {len(points_to_run)} / {len(points)}")
    
    completed_count = len(completed_points)
    
    for env, beta, decay in points_to_run:
        all_tasks = []
        for seed in range(seeds):
            all_tasks.append((seed, beta, decay, env, max_ticks))
            
        metrics = []
        with ProcessPoolExecutor(max_workers=14) as executor:
            for res in executor.map(evaluate_point_seed, all_tasks):
                metrics.append(res)
                
        stats = calculate_fitness_stats(metrics, weights)
        record = {
            "env": env,
            "beta": float(beta),
            "decay": float(decay),
            **stats
        }
        
        with open(out_file, "a") as f:
            f.write(json.dumps(record) + "\n")
            
        completed_count += 1
        print(f"Progress: {completed_count}/{len(points)} points computed. (Env: {env}, Beta: {beta}, Decay: {decay})")

if __name__ == "__main__":
    run_holdout()
