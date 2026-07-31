import os
import time
import numpy as np
from experiments.E019C_Cognitive import Actor as E019C_CognitiveActor
from experiments.E019_Base import Actor as E019_BaselineActor
from infrastructure.runner.loader import load_constraint_set
from infrastructure.runner.system import SystemPhysics
from infrastructure.evolution.genome import CognitiveGenome

def run_single_agent(agent_class, name, episodes=1000, beta=0.0):
    """Chay mo phong nhe cho 1 Agent tren 1 core CPU."""
    print(f"\n[{name}] Dang khoi dong huan luyen...")
    
    # Moi truong nhe
    config = load_constraint_set("default-v1")
    system = SystemPhysics(config)
    
    # Khoi tao tac tu
    genome = CognitiveGenome()
    genome.beta = beta
    genome.memory_decay_rate = 0.99
    
    actor = agent_class(seed=42, genome=genome)
        
    start_time = time.time()
    
    # Huan luyen
    fitness_history = []
    for ep in range(episodes):
        state = system.get_initial_state()
        last_action = None
        last_action_successful = None
        work_reward = 10.0
        
        actor.reset()
        
        work_history = []
        
        for tick in range(1, 1000 + 1):
            state = system.system_tick(state)
            if system.is_terminal(state):
                work_history.extend([0] * (1000 - tick + 1))
                break
                
            obs = system.system_observe(state, tick)
            if last_action is not None:
                obs["last_action"] = last_action
                obs["last_action_successful"] = last_action_successful
                
            decision = actor.choose(obs)
            
            is_valid, _ = system.system_validate(state, decision)
            last_action = decision
            last_action_successful = is_valid
            
            if is_valid:
                state = system.system_apply(state, decision)
                
            reward = 0.0
            if not is_valid:
                reward = -1.0
            elif decision == "work":
                reward = work_reward
                
            actor.update(str(obs), decision, reward, str(system.system_observe(state, tick)))
            
            work_history.append(1 if (is_valid and decision == "work") else 0)
            
        episode_fitness = sum(work_history)
        fitness_history.append(episode_fitness)
        
        # In tien do cho may yeu
        if (ep + 1) % 50 == 0:
            avg_fit = np.mean(fitness_history[-50:])
            print(f"   - Episode {ep+1}/{episodes} | Avg Fitness: {avg_fit:.1f}")

    runtime = time.time() - start_time
    final_fitness = np.mean(fitness_history[-100:])
    print(f"[{name}] Hoan thanh trong {runtime:.2f}s | Fitness cuoi: {final_fitness:.1f}")
    return final_fitness

if __name__ == "__main__":
    print("==================================================")
    print(" DORYBRAIN - LITE MODE (Danh cho Core i3, 4GB RAM)")
    print("==================================================")
    
    episodes = 1000
    
    # 1. Chay Baseline (Khong co Tri nho)
    fit_base = run_single_agent(
        E019_BaselineActor, 
        "Baseline (Khong Tri nho)", 
        episodes=episodes,
        beta=0.0
    )
    
    # 2. Chay Cognitive (Tri nho thich ung)
    fit_cog = run_single_agent(
        E019C_CognitiveActor, 
        "Cognitive Brain (Beta=64)", 
        episodes=episodes, 
        beta=64.0
    )
    
    print("\n==================================================")
    print(" KET QUA SO SANH")
    print("==================================================")
    print(f" - Baseline Fitness : {fit_base:.1f}")
    print(f" - Cognitive Fitness: {fit_cog:.1f}")
    
    if fit_cog > fit_base:
        print(f"\n=> BO NAO COGNITIVE VUOT TROI HON {(fit_cog - fit_base):.1f} DIEM!")
        print("=> (Mac du may yeu va chay it tap, hieu ung Tri nho van the hien ro!)")
    else:
        print("\n=> Chenh lech chua ro o 1000 tap.")
    print("==================================================\n")
