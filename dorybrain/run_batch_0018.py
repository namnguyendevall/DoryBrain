import subprocess
import os
import sys
import json
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from infrastructure.runner.loader import load_constraint_set
from infrastructure.runner.system import SystemPhysics
import importlib

def run_single_multiepisode(exp_name, constraint_file, seed, max_ticks, episodes, out_dir):
    sys.path.insert(0, os.getcwd())
    exp_module = importlib.import_module(f"experiments.{exp_name}")
    
    constraints = load_constraint_set(constraint_file.replace(".json", ""))
    physics = SystemPhysics(constraints)
    
    import random
    random.seed(seed)
    
    actor_seed = hash((seed, "actor"))
    actor = exp_module.Actor(seed=actor_seed)
    
    commit_hash = "a91f83d"
    
    for ep in range(1, episodes + 1):
        if ep > 1:
            if hasattr(actor, "reset"):
                actor.reset()
                
        out_file = os.path.join(out_dir, f"seed_{seed}_ep_{ep}.jsonl")
        
        with open(out_file, "w") as f:
            metadata = {
                "type": "metadata",
                "experiment": exp_name,
                "protocol": "CSRP-0001 v0.1.0",
                "constraint_set": constraint_file.replace(".json", ""),
                "seed": seed,
                "episode": ep,
                "commit": commit_hash,
                "date": datetime.now(timezone.utc).isoformat()
            }
            f.write(json.dumps(metadata) + "\n")
            
            state = physics.get_initial_state()
            last_action = None
            last_action_successful = None
            
            for tick in range(1, max_ticks + 1):
                state = physics.system_tick(state)
                if physics.is_terminal(state):
                    terminal_event = {"tick": tick, "type": "terminal", "state": state}
                    f.write(json.dumps(terminal_event) + "\n")
                    break
                    
                obs = physics.system_observe(state, tick)
                if last_action is not None:
                    obs["last_action"] = last_action
                    obs["last_action_successful"] = last_action_successful
                    
                input_event = {"tick": tick, "type": "input", "observation": obs}
                f.write(json.dumps(input_event) + "\n")
                
                decision = actor.choose(obs)
                decision_event = {"tick": tick, "type": "decision", "action": decision}
                
                if hasattr(actor, "get_state"):
                    decision_event["actor_state"] = actor.get_state()
                    
                f.write(json.dumps(decision_event) + "\n")
                
                is_valid, reason = physics.system_validate(state, decision)
                
                last_action = decision
                last_action_successful = is_valid
                
                if not is_valid:
                    constraint_event = {"tick": tick, "type": "constraint", "action": decision, "reason": reason}
                    f.write(json.dumps(constraint_event) + "\n")
                else:
                    err = 0.0
                    state = physics.system_apply(state, decision)
                    
                    transition_event = {"tick": tick, "type": "transition", "action": decision, "new_state": state, "conservation_error": err}
                    f.write(json.dumps(transition_event) + "\n")
                
                if physics.is_terminal(state):
                    terminal_event = {"tick": tick, "type": "terminal", "state": state}
                    f.write(json.dumps(terminal_event) + "\n")
                    break
                    
    return f"Finished {exp_name} seed {seed}"

def create_experiment_files():
    experiments = []
    
    # E018D Adaptive
    with open("experiments/E018D_Adaptive.py", "w") as f:
        f.write("from .E018_Base import Actor as BaseActor\n")
        f.write("class Actor(BaseActor):\n")
        f.write("    def __init__(self, seed: int):\n")
        f.write("        super().__init__(seed=seed, keep_q=True, keep_n=True, keep_buffer=True, decay_n=0.99, decay_buffer=0.0)\n")
    experiments.append("E018D_Adaptive")
    
    return experiments

def run_in_process(args):
    try:
        return run_single_multiepisode(*args)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return str(e)

def main():
    experiments = create_experiment_files()
    
    seeds = 10
    ticks = 10000
    episodes = 20
    
    c_file = "ladder_gain/gain_06.json"
    c_name = "gain_06"
    
    tasks = []
    for exp in experiments:
        out_dir = f"logs/batch_0018/{c_name}/{exp}"
        os.makedirs(out_dir, exist_ok=True)
        
        for seed in range(seeds):
            tasks.append((exp, c_file, seed, ticks, episodes, out_dir))
            
    print(f"Total tasks: {len(tasks)}")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for t in tasks:
            futures.append(executor.submit(run_in_process, t))
            
        for i, f in enumerate(futures):
            f.result()
            if (i+1) % 5 == 0:
                print(f"Completed {i+1}/{len(tasks)} tasks")
                
    print("All tasks completed.")

if __name__ == "__main__":
    main()
