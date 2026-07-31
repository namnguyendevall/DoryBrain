import json
import random
import os
import sys
import importlib
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.getcwd())
from infrastructure.runner.loader import load_constraint_set
from infrastructure.runner.system import SystemPhysics
from infrastructure.evolution.genome import CognitiveGenome

def run_evaluation(args):
    seed, genome_dict, constraint_file, max_ticks, exp_name = args
    exp_module = importlib.import_module(f"experiments.{exp_name}")
    
    constraints = load_constraint_set(constraint_file.replace(".json", ""))
    physics = SystemPhysics(constraints)
    
    genome = CognitiveGenome(**genome_dict)
    
    # We must seed properly
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
                
            if exp_name != "E019B_Behavior":
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
            
    return {
        "ep4_latency": ep4_latency,
        "work_rate": work_rate
    }

def evaluate_hold_out():
    constraints = ["ladder_gain/gain_05.json", "ladder_gain/gain_07.json"]
    branches = {
        "E019B_Behavior": "results/batch_0019B/E019B_Behavior_Fixed/top_genomes.jsonl",
        "E019C_Cognitive": "results/batch_0019B/E019C_W_Equil/top_genomes.jsonl"
    }
    
    # Load top genomes from gen 24
    top_genomes = {}
    for branch, filepath in branches.items():
        if not os.path.exists(filepath):
            print(f"Skipping {branch}, no top_genomes file.")
            return
            
        with open(filepath, 'r') as f:
            lines = f.readlines()
            last_line = json.loads(lines[-1])
            top_genomes[branch] = last_line["top_10"] # List of {"genome": ..., "fitness": ...}
            
    for env in constraints:
        print(f"\n=== Hold-out Evaluation on {env} ===")
        for branch, genomes_data in top_genomes.items():
            exp_name = "E019B_Behavior" if "Behavior" in branch else "E019C_Cognitive"
            tasks = []
            for i, g_data in enumerate(genomes_data):
                # evaluate each top genome across 5 random seeds to get average performance
                for seed in range(5):
                    tasks.append((seed, g_data["genome"], env, 2000, exp_name))
            
            with ProcessPoolExecutor(max_workers=10) as executor:
                results = list(executor.map(run_evaluation, tasks))
                
            avg_work = sum(r["work_rate"] for r in results) / len(results)
            success_latency = [r["ep4_latency"] for r in results if r["ep4_latency"] != -1]
            avg_lat = sum(success_latency) / len(success_latency) if success_latency else -1
            success_rate = len(success_latency) / len(results)
            
            print(f"[{branch}] Work Rate: {avg_work:.3f} | Success Rate: {success_rate*100:.1f}% | Avg Ep4 Latency: {avg_lat:.1f}")

if __name__ == "__main__":
    evaluate_hold_out()
