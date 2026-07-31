import argparse
import subprocess
import os

def run_replications(experiment: str, constraint_id: str, total_seeds: int, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    print(f"Starting {total_seeds} replications for {experiment} on {constraint_id}...")
    
    for seed in range(1, total_seeds + 1):
        log_file = os.path.join(out_dir, f"{experiment}_{constraint_id}_seed{seed}.jsonl")
        cmd = [
            "python", "infrastructure/runner/runner.py",
            "--experiment", experiment,
            "--constraint_set", constraint_id,
            "--seed", str(seed),
            "--ticks", "100",
            "--out", log_file
        ]
        subprocess.run(cmd, check=True)
    
    print(f"Finished {total_seeds} replications. Data stored in {out_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", type=str, required=True)
    parser.add_argument("--constraint_set", type=str, required=True)
    parser.add_argument("--seeds", type=int, default=100)
    parser.add_argument("--out_dir", type=str, required=True)
    args = parser.parse_args()
    
    run_replications(args.experiment, args.constraint_set, args.seeds, args.out_dir)
