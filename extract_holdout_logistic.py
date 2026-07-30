import json
import collections
import numpy as np
from scipy.optimize import curve_fit
from scipy import stats

def logistic(x, p_base, c, k):
    # Modified logistic that goes from p_base to 1.0
    z = np.clip(-k * (x - c), -500, 500)
    return p_base + (1.0 - p_base) / (1.0 + np.exp(z))

def extract_logistic():
    data = []
    with open("results/phase7D/holdout_data.jsonl", "r") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
                
    if not data:
        print("No data found.")
        return
        
    envs = sorted(list(set(d["env"] for d in data)))
    
    out_res = {}
    
    print("=== Modified Logistic Threshold Modeling ===")
    print("Model: P(active) = P_base + (1 - P_base) / (1 + exp(-k * (Beta - c)))")
    
    for env in envs:
        env_data = [d for d in data if d["env"] == env]
        
        xdata = np.array([d["beta"] for d in env_data])
        ydata_disc = np.array([d["p_discovery"] for d in env_data])
        
        try:
            # Initial guess: p_base = min(ydata), c = 8, k = 0.5
            p0 = [max(0, min(ydata_disc)), 8.0, 0.5]
            bounds = ([0.0, 0.0, 0.0], [1.0, 100.0, 10.0])
            popt, pcov = curve_fit(logistic, xdata, ydata_disc, p0=p0, bounds=bounds, maxfev=10000)
            p_base, c, k = popt
            perr = np.sqrt(np.diag(pcov))
            ci_c = 1.96 * perr[1]
            
            # Calculate R^2
            residuals = ydata_disc - logistic(xdata, *popt)
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((ydata_disc - np.mean(ydata_disc))**2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        except Exception as e:
            print(f"Failed to fit Discovery for {env}: {e}")
            p_base, c, k, ci_c, r_squared = 0, 0, 0, 0, 0
            
        print(f"\nEnvironment: {env}")
        print(f"  Base Probability (P_base): {p_base:.4f}")
        print(f"  Activation Threshold (c):  {c:.4f} ± {ci_c:.4f}")
        print(f"  Steepness (k):             {k:.4f}")
        print(f"  R^2:                       {r_squared:.4f}")
        
        out_res[env] = {
            "p_base": float(p_base),
            "threshold": float(c),
            "threshold_ci": float(ci_c),
            "steepness": float(k),
            "rsquared": float(r_squared)
        }
        
    with open("results/phase7D_logistic.json", "w") as f:
        json.dump(out_res, f, indent=2)

if __name__ == "__main__":
    extract_logistic()
