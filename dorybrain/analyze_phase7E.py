import json
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.weightstats import ttost_ind
from statsmodels.stats.multitest import multipletests

def calc_stats(data):
    n = len(data)
    mean = np.mean(data)
    std = np.std(data, ddof=1) if n > 1 else 0
    sem = std / np.sqrt(n) if n > 0 else 0
    ci_low, ci_high = stats.t.interval(0.95, df=max(1, n-1), loc=mean, scale=sem) if n > 1 else (mean, mean)
    return mean, std, sem, ci_low, ci_high

def perform_tost(data1, data2, margin):
    # Perform Two One-Sided Tests (TOST) for equivalence
    # Null hypothesis: difference <= -margin OR difference >= margin
    # Alternative: -margin < difference < margin
    # returns p-value of equivalence (max of the two one-sided p-values)
    p_val, t1_res, t2_res = ttost_ind(data1, data2, -margin, margin, usevar='unequal')
    return p_val

def main():
    data = []
    with open("results/phase7E/resilience_data.jsonl", "r") as f:
        for line in f:
            if line.strip():
                d = json.loads(line)
                # Filter out ones that didn't establish baseline fitness
                if d["max_drop"] is not None:
                    data.append(d)
                    
    df = pd.DataFrame(data)
    
    metrics = {
        "relative_drop": 0.05,
        "recovery_time": 50,
        "recovery_slope": 0.05,
        "recovery_auc": 0.02
    }
    
    # 1. Summary Statistics Table
    summary = []
    for beta in sorted(df["beta"].unique()):
        beta_data = df[df["beta"] == beta]
        
        row = {"Beta": beta, "N": len(beta_data)}
        for m in metrics:
            mean, std, sem, ci_l, ci_h = calc_stats(beta_data[m])
            row[f"{m}_Mean"] = round(mean, 4)
            row[f"{m}_SD"] = round(std, 4)
            row[f"{m}_SEM"] = round(sem, 4)
            row[f"{m}_95CI"] = f"[{round(ci_l,4)}, {round(ci_h,4)}]"
        summary.append(row)
        
    summary_df = pd.DataFrame(summary)
    print("--- Summary Statistics ---")
    print(summary_df.to_string(index=False))
    summary_df.to_csv("results/phase7E/resilience_summary.csv", index=False)
    
    # 2. Global Test (Kruskal-Wallis) on Plateau Group (Beta >= 20)
    plateau_df = df[df["beta"] >= 20]
    print("\n--- Global Tests (Kruskal-Wallis) for Plateau (Beta >= 20) ---")
    plateau_betas = sorted(plateau_df["beta"].unique())
    
    for m in metrics:
        groups = [plateau_df[plateau_df["beta"] == b][m].values for b in plateau_betas]
        stat, p = stats.kruskal(*groups)
        print(f"{m}: H={stat:.2f}, p={p:.4f}")
        
    # 3. TOST Equivalence Testing
    # Compare 20 vs 100, and 20 vs 500
    print("\n--- TOST Equivalence Testing ---")
    pairs = [(20, 100), (20, 300), (20, 500)]
    tost_results = []
    
    for m, margin in metrics.items():
        p_values = []
        for b1, b2 in pairs:
            d1 = df[df["beta"] == b1][m].dropna().values
            d2 = df[df["beta"] == b2][m].dropna().values
            p = perform_tost(d1, d2, margin)
            p_values.append(p)
            
        # Holm-Bonferroni correction
        reject, p_adjusted, _, _ = multipletests(p_values, alpha=0.05, method='holm')
        
        for i, (b1, b2) in enumerate(pairs):
            tost_results.append({
                "Metric": m,
                "Pair": f"{b1} vs {b2}",
                "Margin": margin,
                "p_raw": p_values[i],
                "p_adj": p_adjusted[i],
                "Equivalent": reject[i]
            })
            
    tost_df = pd.DataFrame(tost_results)
    print(tost_df.to_string(index=False))
    tost_df.to_csv("results/phase7E/tost_results.csv", index=False)
    
    # 4. Check Interpretation Rules
    print("\n--- Pre-registered Interpretation ---")
    for b1, b2 in pairs:
        pair_data = tost_df[tost_df["Pair"] == f"{b1} vs {b2}"]
        eq_count = pair_data["Equivalent"].sum()
        if eq_count == 4:
            conclusion = "Supported"
        elif eq_count == 3:
            conclusion = "Partially Supported"
        else:
            conclusion = "Not Supported"
        print(f"{b1} vs {b2}: {eq_count}/4 metrics equivalent -> {conclusion}")

if __name__ == "__main__":
    main()
