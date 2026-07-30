import argparse
import json
import os

def generate_report(e000_stats_path: str, control_stats_path: str, constraint_id: str, out_path: str):
    with open(e000_stats_path, 'r') as f:
        e000_stats = json.load(f)
    with open(control_stats_path, 'r') as f:
        control_stats = json.load(f)
        
    finding = f"""# F002: Decision Policies under Scarcity
**Date**: 2026-07-28
**Protocol**: CSRP-0001 v0.1.0
**Constraint Set**: {constraint_id}

## Observation Data (100 Seeds)

### E000 (Threshold Policy)
- **Survival Ticks**: {e000_stats['survival']['mean']:.2f} (95% CI: [{e000_stats['survival']['ci95_lower']:.2f}, {e000_stats['survival']['ci95_upper']:.2f}])
- **Survival Variance**: {e000_stats['survival']['variance']:.2f}
- **Constraint Violations**: {e000_stats['violations']['mean']:.2f} (95% CI: [{e000_stats['violations']['ci95_lower']:.2f}, {e000_stats['violations']['ci95_upper']:.2f}])

### Control Group (Uniform Random Policy)
- **Survival Ticks**: {control_stats['survival']['mean']:.2f} (95% CI: [{control_stats['survival']['ci95_lower']:.2f}, {control_stats['survival']['ci95_upper']:.2f}])
- **Survival Variance**: {control_stats['survival']['variance']:.2f}
- **Constraint Violations**: {control_stats['violations']['mean']:.2f} (95% CI: [{control_stats['violations']['ci95_lower']:.2f}, {control_stats['violations']['ci95_upper']:.2f}])
"""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(finding)
    print(f"Report written to {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--e000_stats", type=str, required=True)
    parser.add_argument("--control_stats", type=str, required=True)
    parser.add_argument("--constraint_set", type=str, required=True)
    parser.add_argument("--out", type=str, required=True)
    args = parser.parse_args()
    
    generate_report(args.e000_stats, args.control_stats, args.constraint_set, args.out)
