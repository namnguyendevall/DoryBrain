import glob, json
for exp in ['E014_Control', 'E014_b04', 'E014_b16', 'E014', 'E014_b64']:
    files = glob.glob(f'logs/batch_0014/gain_05/{exp}/seed_*.jsonl')
    invs = []
    for f in files:
        with open(f) as fh:
            inv = sum(1 for line in fh if '"action": "invest_' in line and '"type": "transition"' in line)
            invs.append(inv)
    print(f'{exp}: {sum(invs)/len(invs) if invs else 0}')
