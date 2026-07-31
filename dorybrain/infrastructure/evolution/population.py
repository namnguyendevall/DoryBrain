import math
import random

class PopulationManager:
    def __init__(self, size=100, mutation_enabled=True, selection_enabled=True):
        self.size = size
        self.mutation_enabled = mutation_enabled
        self.selection_enabled = selection_enabled
        
    def evaluate_fitness(self, metrics, fitness_weights=None):
        if fitness_weights is None:
            fitness_weights = {"work": 0.4, "discovery": 0.3, "adaptation": 0.2, "memory": 0.1}
            
        """
        metrics: list of dicts, one for each agent.
        Requires:
        - work_rate: steady state work rate (e.g. from Episode 4)
        - max_work_rate: theoretical max work rate for environment
        - ep1_latency: first invest tick in episode 1
        - ep4_latency: first invest tick in episode 4
        - replay_capacity: genome capacity
        """
        fitness_scores = []
        for m in metrics:
            # 1. Work Score
            max_w = m.get("max_work_rate", 1.0)
            work_score = min(max(m.get("work_rate", 0) / max_w, 0.0), 1.0)
            
            # 2. Discovery Score (based on Ep 1)
            ep1_lat = m.get("ep1_latency", 10000)
            if ep1_lat == -1: ep1_lat = 10000
            discovery_score = 1.0 - min(ep1_lat / 10000.0, 1.0)
            
            # 3. Adaptation Score (Ep 1 to Ep 4)
            ep4_lat = m.get("ep4_latency", 10000)
            if ep4_lat == -1: ep4_lat = 10000
            
            if ep1_lat == 10000:
                adaptation_score = 0.0
            else:
                adapt_val = (ep1_lat - ep4_lat) / float(ep1_lat)
                adaptation_score = min(max(adapt_val, 0.0), 1.0)
                
            # 4. Memory Efficiency
            capacity = m.get("replay_capacity", 10000)
            if capacity == 0: capacity = 1
            # Using performance_gain (adaptation_score) / (capacity / 10000)
            mem_eff = adaptation_score / (capacity / 10000.0)
            mem_eff = min(max(mem_eff, 0.0), 1.0)
            
            total_fitness = (fitness_weights["work"] * work_score + 
                             fitness_weights["discovery"] * discovery_score + 
                             fitness_weights["adaptation"] * adaptation_score + 
                             fitness_weights["memory"] * mem_eff)
            fitness_scores.append(total_fitness)
            
        return fitness_scores
        
    def next_generation(self, genomes, fitness_scores):
        if not self.selection_enabled:
            # Random selection
            next_gen = []
            for _ in range(self.size):
                parent = random.choice(genomes)
                child = parent.clone()
                if self.mutation_enabled:
                    child.mutate()
                next_gen.append(child)
            return next_gen
            
        # Top 20% survive and reproduce
        paired = list(zip(genomes, fitness_scores))
        paired.sort(key=lambda x: x[1], reverse=True)
        
        top_k = max(1, int(self.size * 0.20))
        elites = [p[0] for p in paired[:top_k]]
        
        next_gen = []
        for _ in range(self.size):
            parent = random.choice(elites)
            child = parent.clone()
            if self.mutation_enabled:
                child.mutate()
            next_gen.append(child)
            
        return next_gen
        
    def calculate_cir(self, current_fitness_scores, previous_top_10_percent_threshold):
        if previous_top_10_percent_threshold is None:
            return 1.0 # First generation, everything is innovative
            
        count = sum(1 for f in current_fitness_scores if f > previous_top_10_percent_threshold)
        return count / float(len(current_fitness_scores))
        
    def get_top_genomes(self, genomes, fitness_scores, k=10):
        paired = list(zip(genomes, fitness_scores))
        paired.sort(key=lambda x: x[1], reverse=True)
        return [{"genome": p[0].to_dict(), "fitness": p[1]} for p in paired[:k]]
        
    def get_top_10_percent_threshold(self, fitness_scores):
        sorted_scores = sorted(fitness_scores, reverse=True)
        idx = max(0, int(len(sorted_scores) * 0.10) - 1)
        return sorted_scores[idx]
        
    def calculate_entropy(self, genomes):
        # Very simple binning to calculate entropy of the genome distribution
        bins = {}
        for g in genomes:
            # Binning beta (steps of 10) and decay (steps of 0.01)
            b_beta = int(g.beta / 10)
            b_decay = int(g.memory_decay_rate * 100)
            k = (b_beta, b_decay)
            bins[k] = bins.get(k, 0) + 1
            
        entropy = 0.0
        for v in bins.values():
            p = v / len(genomes)
            entropy -= p * math.log2(p)
        return entropy
