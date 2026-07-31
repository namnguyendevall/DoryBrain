import subprocess
import os
import sys
import json

import os
import glob
import statistics

def extract_stats():
    experiments = []
    for b in [0, 2, 4, 8, 16, 32, 64, 128]:
        experiments.append(f"E015_Replay_b{b:03d}")
        experiments.append(f"E015_Online_b{b:03d}")
        
    constraints = [
        "gain_04",
        "gain_05",
        "gain_06"
    ]
    
    os.makedirs("results/batch_0015", exist_ok=True)
    summary_lines = []
    summary_lines.append("Batch 0015 (Offline Replay Capacity Sweep) Summary")
    summary_lines.append("================================================")
    
    for c in constraints:
        summary_lines.append(f"\n--- Constraint Set: {c} ---")
        header = f"{'Experiment':<18} | {'Surv(Mean)':<10} | {'InvRate/1k':<10} | {'1st_Inv':<8} | {'Lat(Mean)':<9} | {'Q(inv)':<8} | {'Q(rest)':<8} | {'dQ':<8} | {'Inv(Std)':<8} | {'Inv(Med)':<8} | {'Inv(IQR)':<8} | {'ReplayRatio':<11}"
        summary_lines.append(header)
        summary_lines.append("-" * len(header))
        
        for exp in experiments:
            log_dir = f"logs/batch_0015/{c}/{exp}"
            files = glob.glob(f"{log_dir}/seed_*.jsonl")
            
            if not files:
                continue
                
            survival_ticks = []
            invest_rates = []
            first_invs = []
            latencies = []
            q_invests = []
            q_rests = []
            unique_ratios = []
            
            for f in files:
                with open(f, 'r') as fh:
                    lines = fh.readlines()
                    if not lines: continue
                    
                    last_line = json.loads(lines[-1])
                    
                    if last_line['type'] == 'terminal':
                        surv = last_line.get('tick', 10000)
                        # Find the last decision for actor state
                        actor_state = {}
                        for line in reversed(lines):
                            data = json.loads(line)
                            if data['type'] == 'decision':
                                actor_state = data['actor_state']
                                break
                    else:
                        surv = last_line.get('tick', 10000)
                        actor_state = last_line.get('actor_state', {})
                        
                    survival_ticks.append(surv)
                    
                    # Count total investments
                    inv_count = 0
                    for line in lines:
                        data = json.loads(line)
                        if data['type'] == 'transition' and data['action'] in ['invest_gain', 'invest_decay']:
                            inv_count += 1
                            
                    invest_rates.append((inv_count / surv) * 1000 if surv > 0 else 0)
                    
                    first_inv = actor_state.get('first_investment_tick', -1)
                    first_invs.append(first_inv if first_inv != -1 else 0)
                    
                    lat = actor_state.get('investment_latency', -1)
                    latencies.append(lat if lat != -1 else 0)
                    
                    q_invests.append(actor_state.get('q_invest_start', 0.0))
                    q_rests.append(actor_state.get('q_rest_start', 0.0))
                    unique_ratios.append(actor_state.get('effective_unique_replay_ratio', 0.0))
                    
            if not survival_ticks:
                continue
                
            surv_mean = sum(survival_ticks) / len(survival_ticks)
            inv_rate_mean = sum(invest_rates) / len(invest_rates)
            first_inv_mean = sum(first_invs) / len(first_invs)
            lat_mean = sum(latencies) / len(latencies)
            q_inv_mean = sum(q_invests) / len(q_invests)
            q_rest_mean = sum(q_rests) / len(q_rests)
            dq_mean = q_inv_mean - q_rest_mean
            ur_mean = sum(unique_ratios) / len(unique_ratios)
            
            if len(invest_rates) >= 2:
                inv_std = statistics.stdev(invest_rates)
                inv_med = statistics.median(invest_rates)
                sorted_rates = sorted(invest_rates)
                mid = len(sorted_rates) // 2
                q1 = statistics.median(sorted_rates[:mid]) if mid > 0 else sorted_rates[0]
                q3 = statistics.median(sorted_rates[mid + (len(sorted_rates)%2):]) if mid > 0 else sorted_rates[-1]
                inv_iqr = q3 - q1
            else:
                inv_std = 0
                inv_med = invest_rates[0] if invest_rates else 0
                inv_iqr = 0
                
            summary_lines.append(
                f"{exp:<18} | {surv_mean:<10.1f} | {inv_rate_mean:<10.1f} | {first_inv_mean:<8.1f} | {lat_mean:<9.1f} | {q_inv_mean:<8.2f} | {q_rest_mean:<8.2f} | {dq_mean:<8.2f} | {inv_std:<8.1f} | {inv_med:<8.1f} | {inv_iqr:<8.1f} | {ur_mean:<11.3f}"
            )
            
    with open("results/batch_0015/summary.txt", "w") as f:
        f.write("\n".join(summary_lines))
        
    print("Statistics written to results/batch_0015/summary.txt")

if __name__ == "__main__":
    extract_stats()
