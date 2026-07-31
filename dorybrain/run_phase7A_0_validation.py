import json
import random
import os
import sys
import collections
import importlib
import numpy as np
import itertools
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.getcwd())
from infrastructure.runner.loader import load_constraint_set
from infrastructure.runner.system import SystemPhysics
from infrastructure.evolution.genome import CognitiveGenome

def evaluate_point_seed(args):
    seed, beta, decay, constraint_file, max_ticks = args
    exp_module = importlib.import_module("experiments.E019C_Cognitive")
    
    constraints = load_constraint_set(constraint_file.replace(".json", ""))
    physics = SystemPhysics(constraints)
    
    # Reference parameters
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

def calculate_fitness_stats(metrics, weights):
    scores = []
    for m in metrics:
        s = (m["work_rate"] * weights[0] +
             m["discovery"] * weights[1] +
             m["adaptation"] * weights[2] +
             m["memory"] * weights[3])
        scores.append(s)
    
    scores = np.array(scores)
    mean = float(np.mean(scores)) if len(scores) > 0 else 0.0
    std = float(np.std(scores)) if len(scores) > 0 else 0.0
    var = float(np.var(scores)) if len(scores) > 0 else 0.0
    cv = float(std / mean) if mean > 0 else 0.0
    
    # 95% CI
    ci_half = 1.96 * std / np.sqrt(len(scores)) if len(scores) > 0 else 0.0
    ci_low = float(mean - ci_half)
    ci_high = float(mean + ci_half)
    
    return {
        "fitness_mean": mean,
        "fitness_std": std,
        "fitness_var": var,
        "fitness_cv": cv,
        "fitness_ci_low": ci_low,
        "fitness_ci_high": ci_high,
        "work_rate": float(np.mean([m["work_rate"] for m in metrics])),
        "adaptation": float(np.mean([m["adaptation"] for m in metrics])),
        "discovery": float(np.mean([m["discovery"] for m in metrics])),
        "memory": float(np.mean([m["memory"] for m in metrics])),
        "seed_count": len(metrics)
    }

def extract_connected_components(grid_stats, threshold, b_step, d_step):
    # grid_stats is dict (beta, decay) -> data dict
    # Return mapping from (beta, decay) -> component_id
    
    # Filter points above threshold
    valid_points = set()
    for (b, d), stats in grid_stats.items():
        if stats["fitness_mean"] >= threshold:
            valid_points.add((b, d))
            
    # Simple BFS to find components
    components = {}
    current_id = 1
    
    visited = set()
    
    for start_node in valid_points:
        if start_node in visited:
            continue
            
        queue = [start_node]
        visited.add(start_node)
        components[start_node] = current_id
        
        while queue:
            node = queue.pop(0)
            b, d = node
            
            # 4-way connectedness
            neighbors = [
                (round(b + b_step, 4), d),
                (round(b - b_step, 4), d),
                (b, round(d + d_step, 4)),
                (b, round(d - d_step, 4))
            ]
            
            for nb, nd in neighbors:
                # Due to float precision, we check proximity
                matched = None
                for vp in valid_points:
                    if abs(vp[0] - nb) < 1e-5 and abs(vp[1] - nd) < 1e-5:
                        matched = vp
                        break
                
                if matched and matched not in visited:
                    visited.add(matched)
                    components[matched] = current_id
                    queue.append(matched)
                    
        current_id += 1
        
    return components

def run_phase7A_validation():
    # 4x4 Grid for validation
    b_step = 100
    d_step = 0.03
    betas = np.arange(100, 500, b_step)
    decays = np.arange(0.90, 1.02, d_step)
    seeds = 5
    constraint_file = "ladder_gain/gain_06.json"
    max_ticks = 2000
    
    points = list(itertools.product(betas, decays))
    print(f"Total Validation Grid Points: {len(points)}")
    
    # We will use W_Equil for validation
    weights = [0.25, 0.25, 0.25, 0.25]
    out_dir = "results/phase7A"
    os.makedirs(out_dir, exist_ok=True)
    
    all_tasks = []
    for beta, decay in points:
        for seed in range(seeds):
            all_tasks.append((seed, beta, decay, constraint_file, max_ticks))
            
    print(f"Total evaluations: {len(all_tasks)}")
    
    results_map = collections.defaultdict(list)
    with ProcessPoolExecutor(max_workers=14) as executor:
        for task, res in zip(all_tasks, executor.map(evaluate_point_seed, all_tasks)):
            _, beta, decay, _, _ = task
            results_map[(beta, decay)].append(res)
            
    # Calculate stats
    grid_stats = {}
    max_fitness = 0.0
    for (beta, decay), metrics in results_map.items():
        stats = calculate_fitness_stats(metrics, weights)
        grid_stats[(beta, decay)] = stats
        if stats["fitness_mean"] > max_fitness:
            max_fitness = stats["fitness_mean"]
            
    print(f"Max Validation Fitness: {max_fitness:.4f}")
    
    # Extract Plateau 95 components
    threshold95 = max_fitness * 0.95
    components = extract_connected_components(grid_stats, threshold95, b_step, d_step)
    
    out_file = os.path.join(out_dir, "landscape_validation.jsonl")
    print(f"Writing {out_file}...")
    with open(out_file, "w") as f:
        for (beta, decay), stats in grid_stats.items():
            f_mean = stats["fitness_mean"]
            plateau95 = f_mean >= max_fitness * 0.95
            plateau99 = f_mean >= max_fitness * 0.99
            
            comp_id = None
            # Find matching component ID
            for (cb, cd), cid in components.items():
                if abs(cb - beta) < 1e-5 and abs(cd - decay) < 1e-5:
                    comp_id = cid
                    break
                    
            record = {
                "beta": float(beta),
                "decay": float(decay),
                **stats,
                "plateau95": plateau95,
                "plateau99": plateau99,
                "component_id": comp_id
            }
            f.write(json.dumps(record) + "\n")
            
    print("Measurement Validation Complete.")

if __name__ == "__main__":
    run_phase7A_validation()
