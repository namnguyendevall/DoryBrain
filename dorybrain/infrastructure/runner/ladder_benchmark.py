import argparse
import os
import subprocess
import json
import glob
from concurrent.futures import ThreadPoolExecutor

def run_ladder(ladder_dir: str, experiments: list[str], seeds: int, out_base: str):
    # E.g. ladder_dir = "infrastructure/constraint_sets/ladder_work"
    # Find all json files in ladder_dir
    constraints = sorted(glob.glob(os.path.join(ladder_dir, "*.json")))
    
    os.makedirs(out_base, exist_ok=True)
    
    
    commands = []
    
    for c_file in constraints:
        c_id = os.path.basename(c_file).replace(".json", "")
        ladder_name = os.path.basename(ladder_dir)
        full_id = f"{ladder_name}/{c_id}"
        
        for exp in experiments:
            out_dir = os.path.join(out_base, exp, c_id)
            os.makedirs(out_dir, exist_ok=True)
            
            for seed in range(1, seeds + 1):
                log_file = os.path.join(out_dir, f"{exp}_{c_id}_seed{seed}.jsonl")
                cmd = [
                    "python", "infrastructure/runner/runner.py",
                    "--experiment", exp,
                    "--constraint_set", full_id,
                    "--seed", str(seed),
                    "--ticks", "10000",
                    "--out", log_file
                ]
                commands.append(cmd)
                
    def run_cmd(c):
        subprocess.run(c, check=True)
        
    print(f"Running {len(commands)} jobs...")
    with ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(run_cmd, commands)
        
    for c_file in constraints:
        c_id = os.path.basename(c_file).replace(".json", "")
        for exp in experiments:
            out_dir = os.path.join(out_base, exp, c_id)
            stats_out = os.path.join(out_base, f"{exp}_{c_id}_stats.json")
            subprocess.run([
                "python", "infrastructure/benchmark/compute_stats.py",
                "--log_dir", out_dir,
                "--out", stats_out
            ], check=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ladder_dir", type=str, required=True)
    parser.add_argument("--seeds", type=int, default=3)
    parser.add_argument("--out_base", type=str, required=True)
    parser.add_argument("--experiments", nargs="+", default=["E000", "Control"])
    args = parser.parse_args()
    
    run_ladder(args.ladder_dir, args.experiments, args.seeds, args.out_base)
