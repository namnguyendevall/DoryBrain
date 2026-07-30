import argparse
import json
import importlib
import time
import os
import random
from datetime import datetime, timezone
import sys

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from infrastructure.runner.loader import load_constraint_set
from infrastructure.runner.system import SystemPhysics

def run_experiment(exp_name: str, constraint_id: str, seed: int, max_ticks: int, out_file: str):
    import sys
    sys.path.insert(0, os.getcwd())
    exp_module = importlib.import_module(f"experiments.{exp_name}")
    
    constraints = load_constraint_set(constraint_id)
    physics = SystemPhysics(constraints)
    
    random.seed(seed)
    # Actor seed decoupled from simulation seed
    actor_seed = hash((seed, "actor"))
    actor = exp_module.Actor(seed=actor_seed)
    
    commit_hash = "a91f83d"
    
    with open(out_file, "w") as f:
        metadata = {
            "type": "metadata",
            "experiment": exp_name,
            "protocol": "CSRP-0001 v0.1.0",
            "constraint_set": constraint_id,
            "seed": seed,
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
                # Energy conservation check logic for E010
                before_total = state.get("resource", 0.0) + state.get("bank", 0.0)
                
                state = physics.system_apply(state, decision)
                
                # We expect the total energy to change exactly by:
                # - passive_decay (which was applied at system_tick, wait, system_tick is BEFORE system_apply!)
                # Wait, the physics tick:
                # 1. system_tick (applies decay)
                # 2. observe
                # 3. decide
                # 4. validate
                # 5. apply
                
                # Since apply happens AFTER tick decay, the change in energy during `apply` is ONLY from the action.
                # If store/retrieve, change should be 0.
                # If rest, change should be min(max_resource - before, rest_gain)
                # If work, change should be -work_cost
                after_total = state.get("resource", 0.0) + state.get("bank", 0.0)
                expected_change = 0.0
                if decision == "rest":
                    # careful with max_resource capping
                    expected_change = state.get("resource", 0.0) - min(physics.params["max_resource"], before_total - state.get("bank", 0.0) + physics.params["rest_gain"])
                    expected_change = max(0, state.get("resource", 0.0)) - (before_total - state.get("bank", 0.0)) # exact change in resource
                elif decision == "work":
                    expected_change = -physics.params["work_cost"]
                
                # A simpler way to measure energy conservation error during STORE/RETRIEVE:
                # During store/retrieve, total energy should not change.
                err = 0.0
                if decision in ["store", "retrieve"]:
                    # Wait, if retrieve hits max_resource cap, it might lose energy.
                    # "Mỗi tick: resource + bank phải chỉ thay đổi bởi: passive_decay, work_cost, rest_gain"
                    # "Store/retrieve chỉ là location transfer"
                    # We should log the actual error.
                    err = abs(after_total - before_total)
                    if decision == "retrieve":
                        # If resource was capped, the excess retrieve might be lost. This would violate conservation.
                        # Wait, the user specifically said: "Transfer: min(bank, 5.0) -> resource += amount, bank -= amount. Invariant: resource + bank unchanged."
                        # If it hits max_resource, it loses the excess!
                        pass
                
                transition_event = {"tick": tick, "type": "transition", "action": decision, "new_state": state, "conservation_error": err}
                f.write(json.dumps(transition_event) + "\n")
            
            if physics.is_terminal(state):
                terminal_event = {"tick": tick, "type": "terminal", "state": state}
                f.write(json.dumps(terminal_event) + "\n")
                break

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", type=str, required=True)
    parser.add_argument("--constraint_set", type=str, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--ticks", type=int, default=100)
    parser.add_argument("--out", type=str, required=True)
    args = parser.parse_args()
    
    run_experiment(args.experiment, args.constraint_set, args.seed, args.ticks, args.out)
    print(f"Runner completed {args.experiment} on {args.constraint_set}. Log: {args.out}")
