import os
import json

def extract_metrics(log_file):
    if not os.path.exists(log_file):
        return None
        
    metrics = {
        "survival_ticks": 0,
        "first_invest": -1,
        "max_resource": 0.0,
        "time_above_50": 0
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
        metrics['first_invest'] = last_event.get("first_investment_tick", -1)
        metrics['max_resource'] = last_event.get("max_resource_reached", 0.0)
        metrics['time_above_50'] = last_event.get("time_above_50_resource", 0)
        
    return metrics

def main():
    base_dir = "logs/batch_0017/gain_06"
    if not os.path.exists(base_dir):
        print("No logs found.")
        return
        
    out_lines = []
    
    experiments = ["E017A_Fresh", "E017B_PersistentSemantic", "E017C_PersistentFull"]
    
    out_lines.append(f"{'Experiment':<25} | {'Ep 1':<7} | {'Ep 2':<7} | {'Ep 3':<7} | {'Ep 4':<7} | {'KTR (Ep1->4)':<12}")
    out_lines.append("-" * 75)
    
    for exp in experiments:
        exp_dir = os.path.join(base_dir, exp)
        if not os.path.exists(exp_dir):
            continue
            
        ep_first_inv = {1: [], 2: [], 3: [], 4: []}
        ep_max_res = {1: [], 2: [], 3: [], 4: []}
        
        for seed in range(10):
            for ep in range(1, 5):
                log_file = os.path.join(exp_dir, f"seed_{seed}_ep_{ep}.jsonl")
                metrics = extract_metrics(log_file)
                if metrics:
                    ep_first_inv[ep].append(metrics['first_invest'] if metrics['first_invest'] != -1 else 10000)
                    ep_max_res[ep].append(metrics['max_resource'])
                    
        avg_inv = {}
        for ep in range(1, 5):
            if ep_first_inv[ep]:
                avg_inv[ep] = sum(ep_first_inv[ep]) / len(ep_first_inv[ep])
            else:
                avg_inv[ep] = -1
                
        if avg_inv[1] > 0 and avg_inv[4] >= 0:
            ktr = (avg_inv[1] - avg_inv[4]) / avg_inv[1] * 100
        else:
            ktr = 0.0
            
        out_lines.append(f"{exp:<25} | {avg_inv[1]:<7.1f} | {avg_inv[2]:<7.1f} | {avg_inv[3]:<7.1f} | {avg_inv[4]:<7.1f} | {ktr:>6.1f}%")

    os.makedirs("results/batch_0017", exist_ok=True)
    with open("results/batch_0017/summary.txt", "w") as f:
        f.write("\n".join(out_lines) + "\n")
        
    print("Statistics written to results/batch_0017/summary.txt")
    print("\n".join(out_lines))

if __name__ == "__main__":
    main()
