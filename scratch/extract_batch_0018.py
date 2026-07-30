import os
import json

def extract_metrics(log_file):
    if not os.path.exists(log_file):
        return None
        
    metrics = {
        "survival_ticks": 0,
        "first_invest": -1,
        "max_resource": 0.0,
        "time_above_50": 0,
        "unique_causal_actions": 0
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
        metrics['unique_causal_actions'] = len(last_event.get("unique_causal_actions", []))
        
    return metrics

def main():
    base_dir = "logs/batch_0018/gain_06"
    if not os.path.exists(base_dir):
        print("No logs found.")
        return
        
    out_lines = []
    
    experiments = ["E018A_Fresh", "E018B_Semantic", "E018C_Full", "E018D_Adaptive"]
    
    out_lines.append(f"{'Experiment':<20} | {'Ep1_Inv':<7} | {'Ep10_Inv':<8} | {'Ep20_Inv':<8} | {'KTR(1->20)':<10} | {'MRE':<6} | {'T_half':<6} | {'Avg_IR':<6}")
    out_lines.append("-" * 90)
    
    # Pre-compute Fresh baseline performance for MT
    fresh_perf = {}
    exp_dir = os.path.join(base_dir, "E018A_Fresh")
    if os.path.exists(exp_dir):
        for ep in range(1, 21):
            ep_vals = []
            for seed in range(10):
                log = os.path.join(exp_dir, f"seed_{seed}_ep_{ep}.jsonl")
                m = extract_metrics(log)
                if m:
                    ep_vals.append(m['first_invest'] if m['first_invest'] != -1 else 10000)
            fresh_perf[ep] = sum(ep_vals) / len(ep_vals) if ep_vals else 10000

    for exp in experiments:
        exp_dir = os.path.join(base_dir, exp)
        if not os.path.exists(exp_dir):
            continue
            
        ep_first_inv = {ep: [] for ep in range(1, 21)}
        ep_uniq = {ep: [] for ep in range(1, 21)}
        
        for seed in range(10):
            for ep in range(1, 21):
                log_file = os.path.join(exp_dir, f"seed_{seed}_ep_{ep}.jsonl")
                metrics = extract_metrics(log_file)
                if metrics:
                    ep_first_inv[ep].append(metrics['first_invest'] if metrics['first_invest'] != -1 else 10000)
                    ep_uniq[ep].append(metrics['unique_causal_actions'])
                    
        avg_inv = {}
        avg_ir = {}
        for ep in range(1, 21):
            if ep_first_inv[ep]:
                avg_inv[ep] = sum(ep_first_inv[ep]) / len(ep_first_inv[ep])
                # IR approx: unique successful causal actions / 10000
                avg_ir[ep] = sum(ep_uniq[ep]) / len(ep_uniq[ep]) / 10000
            else:
                avg_inv[ep] = 10000
                avg_ir[ep] = 0
                
        ktr = (avg_inv[1] - avg_inv[20]) / avg_inv[1] * 100 if avg_inv[1] > 0 else 0
        
        # Capability Half-Life
        t_half = ">20"
        for ep in range(2, 21):
            mt = fresh_perf.get(ep, 10000) - avg_inv[ep]
            if mt < 0:
                t_half = str(ep)
                break
                
        # Memory Retention Efficiency (heuristic)
        # CapRet = KTR
        # MemRet = 0 for A, 0.33 for B, 1.0 for C, 0.66 for D (approx based on Q, N, Buffer)
        mem_ret = 1.0
        if "Fresh" in exp: mem_ret = 1e-9
        elif "Semantic" in exp: mem_ret = 0.33
        elif "Adaptive" in exp: mem_ret = 0.66
        
        mre = (ktr / 100) / mem_ret if mem_ret > 0 else 0
        if "Fresh" in exp: mre = 0
        
        mean_ir = sum(avg_ir.values()) / 20 * 1000  # scaled for readability
        
        out_lines.append(f"{exp:<20} | {avg_inv[1]:<7.1f} | {avg_inv.get(10, 0):<8.1f} | {avg_inv.get(20, 0):<8.1f} | {ktr:>9.1f}% | {mre:>6.2f} | {t_half:>6} | {mean_ir:>6.2f}")

    os.makedirs("results/batch_0018", exist_ok=True)
    with open("results/batch_0018/summary.txt", "w") as f:
        f.write("\n".join(out_lines) + "\n")
        
    print("Statistics written to results/batch_0018/summary.txt")
    print("\n".join(out_lines))

if __name__ == "__main__":
    main()
