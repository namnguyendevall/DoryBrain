import json
import collections

results = collections.defaultdict(list)
with open('results/batch_0019B/evolution_log.jsonl', 'r') as f:
    for line in f:
        data = json.loads(line)
        results[data['branch']].append(data)

for branch, logs in results.items():
    print(f'\n--- {branch} ---')
    l0 = logs[0]
    l1 = logs[-1]
    print(f'Start Gen 0: Fit={l0.get("avg_fitness", 0):.4f}, Beta={l0.get("avg_beta", 0):.1f}, Decay={l0.get("avg_decay", 0):.3f}, Ent={l0.get("avg_entropy", 0):.2f}')
    print(f'End Gen 49:  Fit={l1.get("avg_fitness", 0):.4f}, Beta={l1.get("avg_beta", 0):.1f}, Decay={l1.get("avg_decay", 0):.3f}, Ent={l1.get("avg_entropy", 0):.2f}')
