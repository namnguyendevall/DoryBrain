import argparse
import json

def replay_log(log_path: str):
    print(f"Replaying log: {log_path}")
    with open(log_path, 'r') as f:
        for line in f:
            if not line.strip():
                continue
            event = json.loads(line)
            event_type = event.get("type")
            
            if event_type == "metadata":
                print(f"--- Metadata ---")
                print(f"Experiment: {event.get('experiment')}")
                print(f"Protocol: {event.get('protocol')}")
                print(f"Seed: {event.get('seed')}")
                print(f"Date: {event.get('date')}")
                print(f"----------------")
            elif event_type == "input":
                print(f"[{event['tick']}] Input:      {event['observation']}")
            elif event_type == "decision":
                print(f"[{event['tick']}] Decision:   {event['action']}")
            elif event_type == "constraint":
                print(f"[{event['tick']}] Constraint: REJECTED ({event.get('reason')})")
            elif event_type == "transition":
                print(f"[{event['tick']}] Transition: {event['new_state']}")
            elif event_type == "terminal":
                print(f"[{event['tick']}] TERMINAL STATE REACHED.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", type=str, required=True)
    args = parser.parse_args()
    
    replay_log(args.log)
