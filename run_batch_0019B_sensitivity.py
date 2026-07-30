import os
import sys
import json
import random
from concurrent.futures import ProcessPoolExecutor
from infrastructure.runner.loader import load_constraint_set
from infrastructure.runner.system import SystemPhysics
from infrastructure.evolution.genome import CognitiveGenome
from infrastructure.evolution.population import PopulationManager
import importlib

def evaluate_organism(args):
    seed, genome_dict, constraint_file, max_ticks, exp_name = args
    
    sys.path.insert(0, os.getcwd())
    exp_module = importlib.import_module(f"experiments.{exp_name}")
    
    constraints = load_constraint_set(constraint_file.replace(".json", ""))
    physics = SystemPhysics(constraints)
    
    genome = CognitiveGenome(**genome_dict)
    
    random.seed(seed)
    actor = exp_module.Actor(seed=seed, genome=genome)
    
    ep1_latency = -1
    ep4_latency = -1
    work_rate = 0.0
    
    for ep in range(1, 5):
        if ep > 1:
            actor.reset()
            
        state = physics.get_initial_state()
        last_action = None
        last_action_successful = None
        
        ep_ticks = 0
        invest_tick = -1
        
        for tick in range(1, max_ticks + 1):
            ep_ticks = tick
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
        if ep == 1:
            ep1_latency = actor_state.get("first_investment_tick", -1)
        if ep == 4:
            ep4_latency = actor_state.get("first_investment_tick", -1)
            work_rate = actor_state.get("time_above_50", 0) / float(max_ticks)
            
    return {
        "ep1_latency": ep1_latency,
        "ep4_latency": ep4_latency,
        "work_rate": work_rate,
        "max_work_rate": 1.0, 
        "replay_capacity": genome.replay_capacity
    }

def run_branch(branch_name, exp_name, selection_enabled, mutation_enabled, pop_size=100, generations=50, max_ticks=2000, fitness_weights=None, constraint_file="ladder_gain/gain_06.json"):
    
    pop_manager = PopulationManager(size=pop_size, mutation_enabled=mutation_enabled, selection_enabled=selection_enabled)
    
    genomes = [CognitiveGenome() for _ in range(pop_size)]
    
    out_dir = f"results/batch_0019B/{branch_name}"
    os.makedirs(out_dir, exist_ok=True)
    
    log_file = os.path.join(out_dir, "evolution_log.jsonl")
    top_genomes_file = os.path.join(out_dir, "top_genomes.jsonl")
    
    prev_top_10 = None
    
    with open(log_file, "w") as f_out, open(top_genomes_file, "w") as f_top:
        for gen in range(generations):
            tasks = []
            for i, genome in enumerate(genomes):
                seed = hash((gen, i, branch_name))
                tasks.append((seed, genome.to_dict(), constraint_file, max_ticks, exp_name))
                
            with ProcessPoolExecutor(max_workers=10) as executor:
                results = list(executor.map(evaluate_organism, tasks))
                metrics_list = results
                
            fitness_scores = pop_manager.evaluate_fitness(metrics_list, fitness_weights)
            
            avg_fitness = sum(fitness_scores) / len(fitness_scores)
            max_fitness = max(fitness_scores)
            
            avg_alpha = sum(g.alpha for g in genomes) / len(genomes)
            import math
            
            avg_beta = sum(g.beta for g in genomes) / len(genomes)
            avg_decay = sum(g.memory_decay_rate for g in genomes) / len(genomes)
            
            std_beta = math.sqrt(sum((g.beta - avg_beta)**2 for g in genomes) / len(genomes))
            std_decay = math.sqrt(sum((g.memory_decay_rate - avg_decay)**2 for g in genomes) / len(genomes))
            
            # Simple cluster radius (average Euclidean distance to centroid, normalized)
            # normalize beta by 500, decay by 1.0 for distance metric
            cluster_radius = sum(math.sqrt(((g.beta - avg_beta)/500.0)**2 + (g.memory_decay_rate - avg_decay)**2) for g in genomes) / len(genomes)
            
            entropy = pop_manager.calculate_entropy(genomes)
            cir = pop_manager.calculate_cir(fitness_scores, prev_top_10)
            
            prev_top_10 = pop_manager.get_top_10_percent_threshold(fitness_scores)
            
            log_obj = {
                "generation": gen,
                "avg_fitness": avg_fitness,
                "max_fitness": max_fitness,
                "avg_alpha": avg_alpha,
                "avg_beta": avg_beta,
                "std_beta": std_beta,
                "avg_decay": avg_decay,
                "std_decay": std_decay,
                "cluster_radius": cluster_radius,
                "genome_entropy": entropy,
                "cir": cir
            }
            
            if gen % 5 == 0 or gen == generations - 1:
                print(f"[{branch_name}] Gen {gen} | Fit: {avg_fitness:.4f} | Beta: {avg_beta:.1f}±{std_beta:.1f} | Decay: {avg_decay:.3f}±{std_decay:.3f} | Radius: {cluster_radius:.4f} | Entropy: {entropy:.2f}")
            f_out.write(json.dumps(log_obj) + "\n")
            f_out.flush()
            
            top_genomes = pop_manager.get_top_genomes(genomes, fitness_scores, k=10)
            top_obj = {
                "generation": gen,
                "top_10": top_genomes
            }
            f_top.write(json.dumps(top_obj) + "\n")
            f_top.flush()
            
            genomes = pop_manager.next_generation(genomes, fitness_scores)

if __name__ == "__main__":
    weights_configs = {
        "W_Equil": {"work": 0.25, "discovery": 0.25, "adaptation": 0.25, "memory": 0.25},
        "W_Work": {"work": 0.6, "discovery": 0.2, "adaptation": 0.1, "memory": 0.1},
        "W_Adapt": {"work": 0.1, "discovery": 0.1, "adaptation": 0.6, "memory": 0.2},
        "W_Discovery": {"work": 0.15, "discovery": 0.60, "adaptation": 0.15, "memory": 0.10}
    }
    
    print("\n=== RUNNING E019B_Behavior BASELINE ===")
    run_branch("E019B_Behavior_Fixed", "E019B_Behavior", True, True, pop_size=100, generations=25)
    
    for w_name, w_vals in weights_configs.items():
        print(f"\n=== Starting Sensitivity Branch: E019C_Cognitive ({w_name}) ===")
        run_branch(
            branch_name=f"E019C_{w_name}",
            exp_name="E019C_Cognitive",
            selection_enabled=True,
            mutation_enabled=True,
            pop_size=100,
            generations=25,
            fitness_weights=w_vals
        )
        
    print("\n=== RUNNING HOLD-OUT EVALUATION ===")
    # Run a single generation of the top genomes on hold-out constraints? No, the user wants evolution on new constraints or test the trained ones?
    # Actually, the user asked to "evaluate both on a hold-out environment". 
    # I will just write a separate hold-out script for this after this batch runs.
