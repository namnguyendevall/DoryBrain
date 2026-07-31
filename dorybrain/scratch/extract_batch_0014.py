import subprocess
import os
import sys
import json

def run_stats(log_dir, out_file):
    cmd = [
        sys.executable, "infrastructure/benchmark/compute_stats.py",
        "--log_dir", log_dir,
        "--out", out_file
    ]
    subprocess.run(cmd, check=True)

def main():
    experiments = [
        "E014_Control",
        "E014_b04",
        "E014_b16",
        "E014",       # Batch 32
        "E014_b64"
    ]
    
    constraints = [
        "gain_05"
    ]
    
    os.makedirs("results/batch_0014", exist_ok=True)
    
    for c in constraints:
        for exp in experiments:
            log_dir = f"logs/batch_0014/{c}/{exp}"
            out_file = f"results/batch_0014/{c}_{exp}.json"
            run_stats(log_dir, out_file)
            
    # Compile summary
    with open("results/batch_0014/summary.txt", "w") as f:
        f.write("Batch 0014 (Experience Replay Ablation) Summary\n")
        f.write("================================================\n\n")
        
        for c in constraints:
            f.write(f"--- Constraint Set: {c} ---\n")
            
            # Print a neat table
            f.write(f"{'Experiment':<15} | {'Surv(Mean)':<10} | {'Inv(Mean)':<10} | {'1st_Replay':<10} | {'Lat(Mean)':<10} | {'ReplayAge':<10}\n")
            f.write("-" * 75 + "\n")
            
            for exp in experiments:
                res_file = f"results/batch_0014/{c}_{exp}.json"
                if not os.path.exists(res_file):
                    continue
                with open(res_file, "r") as jf:
                    data = json.load(jf)
                    
                surv = f"{data['survival']['mean']:.1f}"
                inv_ticks = f"{data['e013_first_investment_tick']['mean']:.1f}"
                first_rep = f"{data['first_successful_replay_tick']['mean']:.1f}"
                latency = f"{data['investment_latency']['mean']:.1f}"
                age = f"{data['avg_replay_age']['mean']:.1f}"
                
                f.write(f"{exp:<15} | {surv:<10} | {inv_ticks:<10} | {first_rep:<10} | {latency:<10} | {age:<10}\n")
            
            f.write("\n")

if __name__ == "__main__":
    main()
