import os
import glob
import subprocess

for d in glob.glob('dataset/batch_0013A/raw/*/*'):
    if not os.path.isdir(d):
        continue
    
    parts = d.replace('\\', '/').split('/')
    exp = parts[-2]
    env = parts[-1]
    
    out_file = f"dataset/batch_0013A/raw/{exp}_{env}_stats.json"
    
    print(f"Computing stats for {d} -> {out_file}")
    subprocess.run([
        'python', 'infrastructure/benchmark/compute_stats.py',
        '--log_dir', d,
        '--out', out_file
    ], check=True)

subprocess.run(['python', 'infrastructure/benchmark/extract_batch_0013A.py'], check=True)
