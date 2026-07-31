import os
import json
import numpy as np

def extract():
    base_dir = "dataset/batch_0013A/raw"
    if not os.path.exists(base_dir):
        print("No raw data found.")
        return

    out_lines = []
    
    envs = [
        "cost_01", "cost_02", "cost_03", "cost_04", "cost_05", "cost_06",
        "gain_01", "gain_02", "gain_03", "gain_04", "gain_05", "gain_06",
        "decay_01", "decay_02", "decay_03", "decay_04", "decay_05", "decay_06",
    ]
    
    out_lines.append("E013A: Physics-Constrained Exploration Protocol")
    out_lines.append("=" * 80)
    out_lines.append(f"{'Environment':<12} | {'Survival':<10} | {'SS Work':<10} | {'Invest Q':<10} | {'Mask Rate':<10} | {'Eff Exp':<10} | {'Control Surv':<12}")
    out_lines.append("-" * 80)
    
    for env in envs:
        # Load E013A
        stats_file = os.path.join(base_dir, f"E013A_{env}_stats.json")
        surv = "N/A"
        ss_work = "N/A"
        invest_q = "N/A"
        mask = "N/A"
        eff_exp = "N/A"
        
        if os.path.exists(stats_file):
            with open(stats_file, 'r') as f:
                d = json.load(f)
                surv = f"{d['survival']['mean']:.1f}"
                ss_work = f"{d['steady_state_work_rate']['mean']:.3f}"
                invest_q = f"{d['avg_invest_q']['mean']:.3f}"
                mask = f"{d['mask_rate']['mean']:.3f}"
                eff_exp = f"{d['effective_exploration_rate']['mean']:.3f}"
                
        # Load Control
        c_stats_file = os.path.join(base_dir, f"E013A_Control_{env}_stats.json")
        c_surv = "N/A"
        if os.path.exists(c_stats_file):
            with open(c_stats_file, 'r') as f:
                d = json.load(f)
                c_surv = f"{d['survival']['mean']:.1f}"
                
        out_lines.append(f"{env:<12} | {surv:<10} | {ss_work:<10} | {invest_q:<10} | {mask:<10} | {eff_exp:<10} | {c_surv:<12}")
        
    out_text = "\n".join(out_lines)
    print(out_text)
    
    out_dir = "/Users/binbi/.gemini/antigravity/brain/eaf99689-7248-4954-9f00-53ae82d82563/scratch"
    if os.path.exists(out_dir):
        with open(os.path.join(out_dir, "batch_0013A_summary.txt"), "w") as f:
            f.write(out_text)
            
if __name__ == "__main__":
    extract()
