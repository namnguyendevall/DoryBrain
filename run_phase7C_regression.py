import json
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

def run_regression():
    data = []
    with open("results/phase7A/landscape.jsonl", "r") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
                
    if not data:
        print("No data found.")
        return
        
    df = pd.DataFrame(data)
    
    # 1. Standardize Beta and Decay
    beta_mean = df["beta"].mean()
    beta_std = df["beta"].std()
    
    decay_mean = df["decay"].mean()
    decay_std = df["decay"].std()
    
    df["beta_std"] = (df["beta"] - beta_mean) / beta_std
    df["decay_std"] = (df["decay"] - decay_mean) / decay_std
    
    # 2. Create Polynomial and Interaction terms
    df["beta_sq"] = df["beta_std"] ** 2
    df["decay_sq"] = df["decay_std"] ** 2
    df["beta_x_decay"] = df["beta_std"] * df["decay_std"]
    
    # 3. Define target and features
    y = df["fitness_mean"]
    X = df[["beta_std", "decay_std", "beta_sq", "decay_sq", "beta_x_decay"]]
    
    # Add constant for intercept
    X = sm.add_constant(X)
    
    # 4. Run OLS Regression
    model = sm.OLS(y, X).fit()
    
    print("=== Interaction Regression Summary ===")
    print(model.summary())
    print("\n")
    
    # 5. Calculate VIF
    print("=== Variance Inflation Factors (VIF) ===")
    vif_data = pd.DataFrame()
    vif_data["feature"] = X.columns
    vif_data["VIF"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
    
    for _, row in vif_data.iterrows():
        print(f"{row['feature']:<12}: {row['VIF']:.4f}")
        
    # Write to artifact json
    out_res = {
        "rsquared_adj": float(model.rsquared_adj),
        "f_pvalue": float(model.f_pvalue),
        "params": {k: float(v) for k, v in model.params.items()},
        "pvalues": {k: float(v) for k, v in model.pvalues.items()},
        "conf_int": {k: [float(v1), float(v2)] for k, (v1, v2) in model.conf_int().iterrows()},
        "vif": {row['feature']: float(row['VIF']) for _, row in vif_data.iterrows()}
    }
    
    with open("results/phase7C_regression.json", "w") as f:
        json.dump(out_res, f, indent=2)

if __name__ == "__main__":
    run_regression()
