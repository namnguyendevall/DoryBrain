import json
import collections
import sys
import os
import numpy as np

def extract_plateau():
    # Load dataset
    data = []
    with open("results/phase7A/landscape.jsonl", "r") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
                
    if not data:
        print("No data found.")
        return
        
    # Find max global fitness_mean
    max_fitness = max([d["fitness_mean"] for d in data])
    print(f"Global Max Fitness: {max_fitness:.4f}")
    
    threshold95 = max_fitness * 0.95
    threshold99 = max_fitness * 0.99
    
    # Store points in a grid dict
    # We know the grid is Beta: step 20, Decay: step 0.02
    b_step = 20
    d_step = 0.02
    
    grid = {}
    for d in data:
        b = round(d["beta"], 4)
        dc = round(d["decay"], 4)
        grid[(b, dc)] = d
        
    # Identify valid plateau nodes
    valid_nodes = set()
    core_nodes = set()
    for (b, dc), d in grid.items():
        if d["fitness_mean"] >= threshold95:
            valid_nodes.add((b, dc))
        if d["fitness_mean"] >= threshold99:
            core_nodes.add((b, dc))
            
    print(f"Total points >= 95%: {len(valid_nodes)}")
    print(f"Total points >= 99%: {len(core_nodes)}")
    
    # BFS for Connected Components
    visited = set()
    components = {} # comp_id -> list of nodes
    comp_id = 1
    
    for start_node in valid_nodes:
        if start_node in visited:
            continue
            
        queue = [start_node]
        visited.add(start_node)
        components[comp_id] = [start_node]
        
        while queue:
            node = queue.pop(0)
            b, dc = node
            
            neighbors = [
                (round(b + b_step, 4), dc),
                (round(b - b_step, 4), dc),
                (b, round(dc + d_step, 4)),
                (b, round(dc - d_step, 4))
            ]
            
            for nb, ndc in neighbors:
                matched = None
                for vn in valid_nodes:
                    if abs(vn[0] - nb) < 1e-5 and abs(vn[1] - ndc) < 1e-5:
                        matched = vn
                        break
                        
                if matched and matched not in visited:
                    visited.add(matched)
                    components[comp_id].append(matched)
                    queue.append(matched)
                    
        comp_id += 1
        
    # Calculate metadata for each component
    print("\n=== Component Metadata ===")
    for cid, nodes in components.items():
        area = len(nodes)
        
        # Bbox
        min_b = min([n[0] for n in nodes])
        max_b = max([n[0] for n in nodes])
        min_d = min([n[1] for n in nodes])
        max_d = max([n[1] for n in nodes])
        bbox = {"beta": [min_b, max_b], "decay": [min_d, max_d]}
        
        # Peak
        peak = max([grid[n]["fitness_mean"] for n in nodes])
        
        # Bbox volume in grid points
        b_range = round((max_b - min_b) / b_step) + 1
        d_range = round((max_d - min_d) / d_step) + 1
        bbox_volume = b_range * d_range
        density = area / bbox_volume if bbox_volume > 0 else 0
        
        print(f"Component {cid}:")
        print(f"  Area: {area} cells")
        print(f"  Peak Fitness: {peak:.4f}")
        print(f"  BBox: Beta [{min_b}, {max_b}], Decay [{min_d}, {max_d}]")
        print(f"  Density: {density:.2%}")
        
    # We will write this out to a json file to be read by the artifact generator
    out_data = {
        "global_max_fitness": max_fitness,
        "threshold95": threshold95,
        "threshold99": threshold99,
        "total_nodes": len(grid),
        "plateau95_nodes": len(valid_nodes),
        "plateau99_nodes": len(core_nodes),
        "components": {}
    }
    
    for cid, nodes in components.items():
        min_b = min([n[0] for n in nodes])
        max_b = max([n[0] for n in nodes])
        min_d = min([n[1] for n in nodes])
        max_d = max([n[1] for n in nodes])
        peak = max([grid[n]["fitness_mean"] for n in nodes])
        
        b_range = round((max_b - min_b) / b_step) + 1
        d_range = round((max_d - min_d) / d_step) + 1
        bbox_volume = b_range * d_range
        density = area / bbox_volume if bbox_volume > 0 else 0
        
        out_data["components"][cid] = {
            "area": len(nodes),
            "peak": peak,
            "bbox": {"beta": [min_b, max_b], "decay": [min_d, max_d]},
            "density": density
        }
        
    with open("results/phase7A/plateau_metadata.json", "w") as f:
        json.dump(out_data, f, indent=2)
        
if __name__ == "__main__":
    extract_plateau()
