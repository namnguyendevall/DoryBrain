import json
import collections
import sys
import os
import numpy as np

def compute_gradients():
    data = []
    with open("results/phase7B/landscape_boundary.jsonl", "r") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
                
    if not data:
        print("No data found.")
        return
        
    grid = {}
    for d in data:
        b = round(d["beta"], 4)
        dc = round(d["decay"], 4)
        grid[(b, dc)] = d
        
    betas = sorted(list(set(b for b, d in grid.keys())))
    decays = sorted(list(set(d for b, d in grid.keys())))
    
    out_data = []
    
    b_step = 2.0
    
    for dc in decays:
        for b in betas:
            if b == 0 or b == max(betas):
                continue
            
            b_prev = round(b - b_step, 4)
            b_next = round(b + b_step, 4)
            
            if (b_prev, dc) in grid and (b_next, dc) in grid:
                d_prev = grid[(b_prev, dc)]
                d_next = grid[(b_next, dc)]
                d_curr = grid[(b, dc)]
                
                # Central difference: (f(x+h) - f(x-h)) / 2h
                grad_fitness = (d_next["fitness_mean"] - d_prev["fitness_mean"]) / (2 * b_step)
                grad_work = (d_next["work_rate"] - d_prev["work_rate"]) / (2 * b_step)
                grad_discovery = (d_next["discovery"] - d_prev["discovery"]) / (2 * b_step)
                grad_adaptation = (d_next["adaptation"] - d_prev["adaptation"]) / (2 * b_step)
                grad_memory = (d_next["memory"] - d_prev["memory"]) / (2 * b_step)
                
                out_data.append({
                    "beta": b,
                    "decay": dc,
                    "fitness": d_curr["fitness_mean"],
                    "grad_fitness": grad_fitness,
                    "grad_work": grad_work,
                    "grad_discovery": grad_discovery,
                    "grad_adaptation": grad_adaptation,
                    "grad_memory": grad_memory
                })
                
    with open("results/phase7B/boundary_gradients.json", "w") as f:
        json.dump(out_data, f, indent=2)
        
    print("Gradients computed successfully.")
    
if __name__ == "__main__":
    compute_gradients()
