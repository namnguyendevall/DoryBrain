import os
import json
import numpy as np

def extract_metrics(log_file):
    if not os.path.exists(log_file):
        return None
        
    metrics = {
        "survival_ticks": 0,
        "invest_count": 0,
        "first_invest": -1,
        "latency": [],
        "q_invest": 0.0,
        "max_resource_reached": 0.0,
        "time_above_50": 0,
        "unique_sa": 0,
        "ReplayRatio": []
    }
    
    last_event = None
    with open(log_file, 'r') as f:
        for line in f:
            if not line.strip():
                continue
            event = json.loads(line)
            if event['type'] == 'terminal':
                metrics['survival_ticks'] = event['tick']
            elif event['type'] == 'decision':
                last_event = event.get('actor_state', {})
                
    if metrics['survival_ticks'] == 0:
        metrics['survival_ticks'] = 10000
        
    if last_event:
        metrics['invest_count'] = last_event.get("unique_causal_actions_explored", 0)
        metrics['first_invest'] = last_event.get("first_investment_tick", -1)
        lat = last_event.get("investment_latency", -1)
        if lat > -1:
            metrics['latency'].append(lat)
        metrics['q_invest'] = last_event.get("q_invest_start", 0.0)
        metrics['max_resource_reached'] = last_event.get("max_resource_reached", 0.0)
        metrics['time_above_50'] = last_event.get("time_above_50_resource", 0)
        metrics['unique_sa'] = last_event.get("unique_state_action_pairs", 0)
        metrics['ReplayRatio'].append(last_event.get("effective_unique_replay_ratio", 0.0))
        
    return metrics

def main():
    base_dir = "logs/batch_0016"
    if not os.path.exists(base_dir):
        print("No logs found.")
        return
        
    out_lines = []
    
    for constraint in ["gain_05", "gain_06"]:
        constraint_dir = os.path.join(base_dir, constraint)
        if not os.path.exists(constraint_dir):
            continue
            
        out_lines.append(f"\n--- Constraint Set: {constraint} ---")
        out_lines.append(f"Experiment           | Surv(M) | InvR/1k  | 1st_Inv | Lat(M)  | Q(inv) | MaxRes  | T(>50)   | Uniq(SA) | ReplayRat")
        out_lines.append("-" * 125)
        
        experiments = [
            "E015_Replay_b032",
            "E016A_wrapper",
            "E016B_b1", "E016B_b10", "E016B_b50", "E016B_b100",
            "E016C_c1", "E016C_c2", "E016C_c5"
        ]
        
        for exp in experiments:
            exp_dir = os.path.join(constraint_dir, exp)
            if not os.path.exists(exp_dir):
                continue
                
            exp_data = {
                "survival_ticks": [],
                "invest_count": [],
                "first_invest": [],
                "latency": [],
                "q_invest": [],
                "max_resource_reached": [],
                "time_above_50": [],
                "unique_sa": [],
                "ReplayRatio": []
            }
            
            for seed in range(10):
                log_file = os.path.join(exp_dir, f"seed_{seed}.jsonl")
                metrics = extract_metrics(log_file)
                if metrics:
                    for k in exp_data:
                        if k == "latency":
                            exp_data[k].extend(metrics[k])
                        elif k == "ReplayRatio":
                            exp_data[k].extend(metrics[k])
                        else:
                            exp_data[k].append(metrics[k])
                            
            if not exp_data["survival_ticks"]:
                continue
                
            avg_surv = sum(exp_data["survival_ticks"]) / len(exp_data["survival_ticks"])
            
            # Normalize investment count to per 1k ticks based on survival
            inv_rates = [(inv / surv) * 1000 for inv, surv in zip(exp_data["invest_count"], exp_data["survival_ticks"])]
            avg_inv_rate = sum(inv_rates) / len(inv_rates)
            
            first_invs = [x for x in exp_data["first_invest"] if x != -1]
            first_inv = sum(first_invs) / len(first_invs) if first_invs else -1.0
            
            lats = exp_data["latency"]
            avg_lat = sum(lats) / len(lats) if lats else 0.0
            
            avg_q_inv = sum(exp_data["q_invest"]) / len(exp_data["q_invest"])
            avg_max_res = sum(exp_data["max_resource_reached"]) / len(exp_data["max_resource_reached"])
            avg_t50 = sum(exp_data["time_above_50"]) / len(exp_data["time_above_50"])
            avg_usa = sum(exp_data["unique_sa"]) / len(exp_data["unique_sa"])
            avg_replay_ratio = sum(exp_data["ReplayRatio"]) / len(exp_data["ReplayRatio"]) if exp_data["ReplayRatio"] else 0.0
            
            out_lines.append(f"{exp:<20} | {avg_surv:<7.1f} | {avg_inv_rate:<8.1f} | {first_inv:<7.1f} | {avg_lat:<7.1f} | {avg_q_inv:<6.2f} | {avg_max_res:<7.1f} | {avg_t50:<8.1f} | {avg_usa:<8.1f} | {avg_replay_ratio:<9.3f}")

    os.makedirs("results/batch_0016", exist_ok=True)
    with open("results/batch_0016/summary.txt", "w") as f:
        f.write("\n".join(out_lines) + "\n")
        
    print("Statistics written to results/batch_0016/summary.txt")
    print("\n".join(out_lines))

if __name__ == "__main__":
    main()
