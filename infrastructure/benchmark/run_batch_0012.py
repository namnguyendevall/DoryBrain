import os
import time
import json
import subprocess
from datetime import datetime

def run_batch(seeds: int = 10):
    batch_name = "batch_0012"
    batch_dir = os.path.join("dataset", batch_name)
    raw_dir = os.path.join(batch_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)
    
    start_time = time.time()
    manifest = {
        "batch": "0012",
        "protocol": "CSRP-0001 v0.1.0",
        "experiment": "E013: Q-Lambda Agent (Temporal Credit Assignment)",
        "start_time": datetime.now().isoformat(),
        "replications": seeds,
        "constraint_family": [
            "ladder_work",
            "ladder_gain",
            "ladder_decay"
        ]
    }
    manifest_path = os.path.join(batch_dir, "manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
        
    ladders = ["ladder_work", "ladder_gain", "ladder_decay"]
    
    for ladder in ladders:
        print(f"Running {ladder}...")
        subprocess.run([
            "python", "infrastructure/runner/ladder_benchmark.py",
            "--ladder_dir", f"infrastructure/constraint_sets/{ladder}",
            "--seeds", str(seeds),
            "--out_base", raw_dir,
            "--experiments", "E000", "E013", "E013_Control"
        ], check=True)
        
    end_time = time.time()
    elapsed = end_time - start_time
    
    manifest["end_time"] = datetime.now().isoformat()
    manifest["elapsed_seconds"] = elapsed
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
        
    print(f"Batch 0012 completed in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=100)
    args = parser.parse_args()
    run_batch(seeds=args.seeds)
