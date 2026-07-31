import json
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import warnings
warnings.filterwarnings('ignore')

def step_func(x, p_base, c):
    # Step function: if x < c return p_base, else 1.0
    return np.where(x < c, p_base, 1.0)

def logistic_func(x, p_base, c, k):
    z = np.clip(-k * (x - c), -500, 500)
    return p_base + (1.0 - p_base) / (1.0 + np.exp(z))

def gompertz_func(x, p_base, a, b):
    # a sets the displacement along x, b sets the growth rate
    return p_base + (1.0 - p_base) * np.exp(-a * np.exp(-b * x))

def hill_func(x, p_base, k, n):
    # Hill function: x^n / (k^n + x^n)
    # add small epsilon to avoid div by zero if x=0 and n<1
    x_safe = np.maximum(x, 1e-9)
    # compute log to avoid overflow with large n
    # (x/k)^n = exp(n * log(x/k))
    ratio = np.exp(np.clip(n * np.log(x_safe / max(k, 1e-9)), -500, 500))
    return p_base + (1.0 - p_base) * ratio / (1.0 + ratio)

def calculate_aic_bic(n, rss, k):
    # n: number of observations
    # rss: residual sum of squares
    # k: number of parameters
    if rss <= 0:
        rss = 1e-10
    aic = n * np.log(rss / n) + 2 * k
    bic = n * np.log(rss / n) + k * np.log(n)
    return aic, bic

def main():
    data = []
    with open("results/phase7D/holdout_data.jsonl", "r") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
                
    envs = sorted(list(set(d["env"] for d in data)))
    
    models = {
        "Step": {"func": step_func, "p0": [0.5, 10.0], "bounds": ([0.0, 0.0], [1.0, 100.0]), "k": 2},
        "Logistic": {"func": logistic_func, "p0": [0.5, 8.0, 0.5], "bounds": ([0.0, 0.0, 0.0], [1.0, 100.0, 10.0]), "k": 3},
        "Gompertz": {"func": gompertz_func, "p0": [0.5, 2.0, 0.1], "bounds": ([0.0, 0.0, 0.0], [1.0, 50.0, 10.0]), "k": 3},
        "Hill": {"func": hill_func, "p0": [0.5, 10.0, 2.0], "bounds": ([0.0, 0.0, 0.0], [1.0, 100.0, 20.0]), "k": 3}
    }
    
    results = []
    
    for env in envs:
        env_data = [d for d in data if d["env"] == env]
        xdata = np.array([d["beta"] for d in env_data])
        ydata = np.array([d["p_discovery"] for d in env_data])
        n = len(ydata)
        
        for name, config in models.items():
            try:
                popt, _ = curve_fit(config["func"], xdata, ydata, p0=config["p0"], bounds=config["bounds"], maxfev=20000)
                y_pred = config["func"](xdata, *popt)
                rss = np.sum((ydata - y_pred)**2)
                tss = np.sum((ydata - np.mean(ydata))**2)
                r2 = 1 - (rss / tss) if tss > 0 else 0
                
                aic, bic = calculate_aic_bic(n, rss, config["k"])
                
                results.append({
                    "Environment": env.split("/")[-1].replace(".json", ""),
                    "Model": name,
                    "R2": r2,
                    "AIC": aic,
                    "BIC": bic,
                    "Params": [round(p, 4) for p in popt]
                })
            except Exception as e:
                print(f"Failed to fit {name} for {env}: {e}")
                
    df = pd.DataFrame(results)
    print(df.to_string(index=False))
    
    # Save for reference
    df.to_csv("results/phase7D_model_comparison.csv", index=False)
    
if __name__ == "__main__":
    main()
