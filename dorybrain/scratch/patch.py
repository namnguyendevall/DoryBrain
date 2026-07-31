with open('run_batch_0019B_sensitivity.py', 'r') as f:
    data = f.read()

# Replace run_branch signature
data = data.replace('def run_branch(branch_name, exp_name, selection_enabled, mutation_enabled, pop_size=100, generations=50, max_ticks=2000):', 'def run_branch(branch_name, exp_name, selection_enabled, mutation_enabled, pop_size=100, generations=50, max_ticks=2000, fitness_weights=None, constraint_file="ladder_gain/gain_06.json"):')

# Remove constraint_file hardcoding inside run_branch
data = data.replace('    constraint_file = "ladder_gain/gain_06.json"\n', '')

# Replace evaluate_fitness call
data = data.replace('            fitness_scores = pop_manager.evaluate_fitness(metrics_list)', '            fitness_scores = pop_manager.evaluate_fitness(metrics_list, fitness_weights)')

with open('run_batch_0019B_sensitivity.py', 'w') as f:
    f.write(data)
