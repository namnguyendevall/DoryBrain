import subprocess
import os
import sys
from concurrent.futures import ThreadPoolExecutor

def create_experiment_files():
    experiments = []
    
    # Baseline
    with open("experiments/E015_Replay_b032.py", "w") as f:
        f.write("from .E015_Replay import Actor as BaseActor\n")
        f.write("class Actor(BaseActor):\n")
        f.write("    def __init__(self, seed: int):\n")
        f.write("        super().__init__(seed=seed, batch_size=32)\n")
    experiments.append("E015_Replay_b032")
    
    # E016A
    with open("experiments/E016A_wrapper.py", "w") as f:
        f.write("from .E016A_Optimistic import Actor as BaseActor\n")
        f.write("class Actor(BaseActor):\n")
        f.write("    def __init__(self, seed: int):\n")
        f.write("        super().__init__(seed=seed, batch_size=32)\n")
    experiments.append("E016A_wrapper")
    
    # E016B
    for beta in [1, 10, 50, 100]:
        exp_name = f"E016B_b{beta}"
        with open(f"experiments/{exp_name}.py", "w") as f:
            f.write("from .E016B_CountBonus import Actor as BaseActor\n")
            f.write("class Actor(BaseActor):\n")
            f.write("    def __init__(self, seed: int):\n")
            f.write(f"        super().__init__(seed=seed, batch_size=32, beta={float(beta)})\n")
        experiments.append(exp_name)
        
    # E016C
    for c in [1, 2, 5]:
        exp_name = f"E016C_c{c}"
        with open(f"experiments/{exp_name}.py", "w") as f:
            f.write("from .E016C_UCB import Actor as BaseActor\n")
            f.write("class Actor(BaseActor):\n")
            f.write("    def __init__(self, seed: int):\n")
            f.write(f"        super().__init__(seed=seed, batch_size=32, c={float(c)})\n")
        experiments.append(exp_name)
        
    return experiments

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
    experiments = create_experiment_files()
    
    seeds = 10
    ticks = 10000
    
    constraints = [
        "ladder_gain/gain_05.json",
        "ladder_gain/gain_06.json"
    ]
    
    tasks = []
    
    for c in constraints:
        c_name = c.split("/")[-1].replace(".json", "")
        
        for exp in experiments:
            out_dir = f"logs/batch_0016/{c_name}/{exp}"
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
