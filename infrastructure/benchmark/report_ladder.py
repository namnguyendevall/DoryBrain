import argparse
import json
import os
import glob

def generate_ladder_finding(ladder_name: str, out_base: str, finding_out: str, total_seeds: int = 100):
    stats_files = sorted(glob.glob(os.path.join(out_base, "*_stats.json")))
    
    experiments = set()
    results = {}
    for sf in stats_files:
        basename = os.path.basename(sf).replace("_stats.json", "")
        exp, c_id = basename.split("_", 1)
        experiments.add(exp)
        if c_id not in results:
            results[c_id] = {}
        with open(sf, 'r') as f:
            results[c_id][exp] = json.load(f)
            
    experiments = sorted(list(experiments))
            
    md = f"# Finding: {ladder_name.upper()}\n"
    
    md += "## Evidence Scope\n"
    md += "- **Protocol**: CSRP-0001 v0.1.0\n"
    md += "- **Batch**: 0002\n"
    md += f"- **Constraint Family**: {ladder_name}\n"
    md += "- **Policies**: " + ", ".join(experiments) + "\n"
    md += f"- **Replications**: {total_seeds}\n\n"
    
    md += "## Observed Pattern\n"
    md += "_To be filled after analysis_\n\n"
    
    md += "## Interpretation\n"
    md += "_To be filled after analysis_\n\n"
    
    md += "## Quantitative Data\n\n"
    
    for c_id in sorted(results.keys()):
        md += f"### Constraint: {c_id}\n"
        for exp in experiments:
            if exp not in results[c_id]: continue
            st = results[c_id][exp]
            completed = st.get('seeds_tested', 0)
            failed = total_seeds - completed
            
            md += f"#### {exp}\n"
            md += f"- **Sample Size**: Replications={total_seeds}, Completed={completed}, Failed={failed}\n"
            md += f"- **Survival**: Mean={st['survival']['mean']:.2f} (95% CI: [{st['survival']['ci95_lower']:.2f}, {st['survival']['ci95_upper']:.2f}], Var: {st['survival']['variance']:.2f})\n"
            rm = st.get('resource_margin', {})
            if rm:
                md += f"- **Resource Margin**: Mean={rm['mean_resource']:.2f}, Median={rm['median_resource']:.2f}, Min={rm['min_resource']:.2f}, Max={rm.get('max_resource', 0):.2f}, p05={rm['p05_resource']:.2f}, p95={rm['p95_resource']:.2f}\n"
            md += f"- **Entropy**: {st.get('decision_entropy', 0):.4f}\n"
            
            pw = st.get('productive_work', {})
            if pw:
                md += f"- **Total Productive Work**: Mean={pw['mean']:.2f} (95% CI: [{pw['ci95_lower']:.2f}, {pw['ci95_upper']:.2f}])\n"
            
            wr = st.get('work_rate', {})
            if wr:
                md += f"- **Work Rate**: Mean={wr['mean']:.4f}\n"
                
            comatose = st.get('comatose_fraction', 0.0)
            md += f"- **Comatose Fraction**: {comatose * 100:.1f}%\n\n"
            
    os.makedirs(os.path.dirname(finding_out), exist_ok=True)
    with open(finding_out, "w") as f:
        f.write(md)
    print(f"Finding written to {finding_out}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ladder_name", type=str, required=True)
    parser.add_argument("--out_base", type=str, required=True)
    parser.add_argument("--finding_out", type=str, required=True)
    args = parser.parse_args()
    
    generate_ladder_finding(args.ladder_name, args.out_base, args.finding_out)
