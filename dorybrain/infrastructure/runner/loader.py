import json
import os

def load_constraint_set(constraint_id: str) -> dict:
    path = os.path.join("infrastructure", "constraint_sets", f"{constraint_id}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Constraint set {constraint_id} not found at {path}")
    with open(path, 'r') as f:
        data = json.load(f)
    return data
