import json
import collections

configs = ['E019B_Behavior_Fixed', 'E019C_W_Equil', 'E019C_W_Work', 'E019C_W_Adapt', 'E019C_W_Discovery']
for config in configs:
    try:
        with open(f'results/batch_0019B/{config}/evolution_log.jsonl', 'r') as f:
            print(f'\n=== Trajectory for {config} ===')
            for line in f:
                d = json.loads(line)
                g = d['generation']
                if g in [0, 5, 10, 15, 20, 24]:
                    print(f"Gen {g}: Fit={d['avg_fitness']:.3f} | Beta={d['avg_beta']:.1f}±{d['std_beta']:.1f} | Decay={d['avg_decay']:.3f}±{d['std_decay']:.3f} | Rad={d['cluster_radius']:.3f} | Ent={d['genome_entropy']:.2f}")
    except Exception as e:
        pass
