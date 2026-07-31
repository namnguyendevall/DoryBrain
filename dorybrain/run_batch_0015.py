import subprocess
import os
import sys
from concurrent.futures import ThreadPoolExecutor

def create_experiment_files():
    sweep = [0, 2, 4, 8, 16, 32, 64, 128]
    for b in sweep:
        # Replay
        with open(f"experiments/E015_Replay_b{b:03d}.py", "w") as f:
            f.write(f"from .E015_Replay import Actor as BaseActor\n")
            f.write(f"class Actor(BaseActor):\n")
            f.write(f"    def __init__(self, seed: int):\n")
            f.write(f"        super().__init__(seed=seed, batch_size={b})\n")
        # Online
        with open(f"experiments/E015_Online_b{b:03d}.py", "w") as f:
            f.write(f"from .E015_Online import Actor as BaseActor\n")
            f.write(f"class Actor(BaseActor):\n")
            f.write(f"    def __init__(self, seed: int):\n")
            f.write(f"        super().__init__(seed=seed, batch_size={b})\n")
    return sweep

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
    sweep = create_experiment_files()
    
    experiments = []
    for b in sweep:
        experiments.append(f"E015_Replay_b{b:03d}")
        experiments.append(f"E015_Online_b{b:03d}")
    
    seeds = 5
    ticks = 10000
    
    constraints = [
        "ladder_gain/gain_04.json",
        "ladder_gain/gain_05.json",
        "ladder_gain/gain_06.json"
    ]
    
    tasks = []
    
    for c in constraints:
        c_name = c.split("/")[-1].replace(".json", "")
        
        for exp in experiments:
            out_dir = f"logs/batch_0015/{c_name}/{exp}"
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
