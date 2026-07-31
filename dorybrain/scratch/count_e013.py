import glob, json
files = glob.glob('logs/batch_0013/gain_04/E013/seed_*.jsonl')
invs = []
for f in files:
    with open(f) as fh:
        inv = sum(1 for line in fh if '"action": "invest_' in line and '"type": "transition"' in line)
        invs.append(inv)
print(f'E013: {sum(invs)/len(invs) if invs else 0}')
