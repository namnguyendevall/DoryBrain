import os
import sys
import json
import random
from concurrent.futures import ThreadPoolExecutor
from infrastructure.runner.loader import load_constraint_set
from infrastructure.runner.system import SystemPhysics
from infrastructure.evolution.genome import CognitiveGenome
from infrastructure.evolution.population import PopulationManager
import importlib

def evaluate_organism(args):
    # Runs 4 episodes for a single organism
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
            
            # Record first invest tick for causal discovery latency
            if decision == "invest" and invest_tick == -1:
                # Check validity
                is_valid, _ = physics.system_validate(state, decision)
                if is_valid:
                    invest_tick = tick
            
            is_valid, _ = physics.system_validate(state, decision)
            last_action = decision
            last_action_successful = is_valid
            
            if is_valid:
                state = physics.system_apply(state, decision)
                
            if physics.is_terminal(state):
                break
                
        # Extract metrics from actor state
        actor_state = actor.get_state()
        if ep == 1:
            ep1_latency = actor_state.get("first_investment_tick", -1)
        if ep == 4:
            ep4_latency = actor_state.get("first_investment_tick", -1)
            # Use time_above_50 as the proxy for steady state work rate
            # Max possible is basically max_ticks
            work_rate = actor_state.get("time_above_50", 0) / float(max_ticks)
            
    return {
        "ep1_latency": ep1_latency,
        "ep4_latency": ep4_latency,
        "work_rate": work_rate,
        "max_work_rate": 1.0, # normalized in calculation
        "replay_capacity": genome.replay_capacity
    }


def main():
    exp_name = "E019C_Cognitive"
    constraint_file = "ladder_gain/gain_06.json"
    
    pop_size = 100
    generations = 10
    max_ticks = 2000
    
    # E019C is the test: selection + mutation enabled
    pop_manager = PopulationManager(size=pop_size, mutation_enabled=True, selection_enabled=True)
    
    genomes = [CognitiveGenome() for _ in range(pop_size)]
    
    out_dir = "results/batch_0019A"
    os.makedirs(out_dir, exist_ok=True)
    
    log_file = os.path.join(out_dir, "evolution_log.jsonl")
    
    with open(log_file, "w") as f_out:
        for gen in range(generations):
            print(f"Generation {gen} started...")
            
            tasks = []
            for i, genome in enumerate(genomes):
                seed = hash((gen, i, "evo"))
                tasks.append((seed, genome.to_dict(), constraint_file, max_ticks, exp_name))
                
            metrics_list = []
            with ThreadPoolExecutor(max_workers=10) as executor:
                results = list(executor.map(evaluate_organism, tasks))
                metrics_list = results
                
            fitness_scores = pop_manager.evaluate_fitness(metrics_list)
            
            avg_fitness = sum(fitness_scores) / len(fitness_scores)
            max_fitness = max(fitness_scores)
            
            avg_alpha = sum(g.alpha for g in genomes) / len(genomes)
            avg_beta = sum(g.beta for g in genomes) / len(genomes)
            avg_decay = sum(g.memory_decay_rate for g in genomes) / len(genomes)
            
            entropy = pop_manager.calculate_entropy(genomes)
            
            log_obj = {
                "generation": gen,
                "avg_fitness": avg_fitness,
                "max_fitness": max_fitness,
                "avg_alpha": avg_alpha,
                "avg_beta": avg_beta,
                "avg_decay": avg_decay,
                "genome_entropy": entropy
            }
            
            print(f"Gen {gen} | Avg Fit: {avg_fitness:.4f} | Max Fit: {max_fitness:.4f} | Avg Beta: {avg_beta:.1f} | Avg Decay: {avg_decay:.3f} | Entropy: {entropy:.2f}")
            
            f_out.write(json.dumps(log_obj) + "\n")
            f_out.flush()
            
            genomes = pop_manager.next_generation(genomes, fitness_scores)
            
if __name__ == "__main__":
    main()
