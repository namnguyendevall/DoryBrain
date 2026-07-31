import subprocess
import os
import sys
from concurrent.futures import ThreadPoolExecutor

def run_single(exp, c_file, seed, ticks, out_file):
    cmd = [
        sys.executable, "infrastructure/runner/runner.py",
        "--experiment", exp,
        "--constraint_set", c_file.replace(".json", ""),
        "--seed", str(seed),
        "--ticks", str(ticks),
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
    
    seeds = 5
    ticks = 10000
    
    constraints = [
        "ladder_gain/gain_05.json"
    ]
    
    tasks = []
    
    for c in constraints:
        c_name = c.split("/")[-1].replace(".json", "")
        
        for exp in experiments:
            out_dir = f"logs/batch_0014/{c_name}/{exp}"
            os.makedirs(out_dir, exist_ok=True)
            
            for seed in range(seeds):
                out_file = f"{out_dir}/seed_{seed}.jsonl"
                tasks.append((exp, c, seed, ticks, out_file))
                
    print(f"Total tasks: {len(tasks)}")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for t in tasks:
            futures.append(executor.submit(run_single, *t))
            
        for i, f in enumerate(futures):
            f.result()
            if (i+1) % 10 == 0:
                print(f"Completed {i+1}/{len(tasks)} tasks")
                
    print("All tasks completed.")

if __name__ == "__main__":
    main()
