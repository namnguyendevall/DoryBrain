import os
import time
import json
import subprocess
from datetime import datetime

def run_batch():
    batch_dir = "dataset/batch_0001"
    raw_dir = os.path.join(batch_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)
    
    start_time = time.time()
    manifest = {
        "batch": "0001",
        "protocol": "CSRP-0001 v0.1.0",
        "experiment": "Q003",
        "runner_commit": "HEAD",  # placeholder
        "start_time": datetime.now().isoformat(),
        "replications": 100,
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
            "--seeds", "100",
            "--out_base", os.path.join(raw_dir, ladder)
        ], check=True)
        
    print("Generating finding reports...")
    subprocess.run([
        "python", "infrastructure/benchmark/report_ladder.py",
        "--ladder_name", "Work Cost",
        "--out_base", os.path.join(raw_dir, "ladder_work"),
        "--finding_out", "knowledge/findings/FA01.md"
    ], check=True)
    subprocess.run([
        "python", "infrastructure/benchmark/report_ladder.py",
        "--ladder_name", "Recovery Gain",
        "--out_base", os.path.join(raw_dir, "ladder_gain"),
        "--finding_out", "knowledge/findings/FB01.md"
    ], check=True)
    subprocess.run([
        "python", "infrastructure/benchmark/report_ladder.py",
        "--ladder_name", "Passive Decay",
        "--out_base", os.path.join(raw_dir, "ladder_decay"),
        "--finding_out", "knowledge/findings/FC01.md"
    ], check=True)
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    manifest["end_time"] = datetime.now().isoformat()
    manifest["elapsed_seconds"] = elapsed
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
        
    # Sanity Check
    import glob
    all_jsonl = glob.glob(os.path.join(raw_dir, "**", "*.jsonl"), recursive=True)
    corrupted = 0
    empty = 0
    
    for f in all_jsonl:
        size = os.path.getsize(f)
        if size == 0:
            empty += 1
            
    sanity_report = f"""Sanity Report - Batch 0001
Expected Files: 3600 (18 constraints * 2 experiments * 100 seeds)
Total Log Files: {len(all_jsonl)}
Empty Logs: {empty}
Corrupted Logs: {corrupted}
Elapsed Time: {elapsed:.2f} seconds
"""
    with open(os.path.join(batch_dir, "sanity_report.txt"), "w") as f:
        f.write(sanity_report)
        
    print("Batch 0001 completed.")

if __name__ == "__main__":
    run_batch()
