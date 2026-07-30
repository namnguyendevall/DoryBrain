<div align="center">
  <h1>🧠 DoryBrain (CSRP)</h1>
  <p><strong>Cognitive System Research Project: An Experimental Platform for Reinforcement Learning, Adaptive Memory, and Evolutionary Optimization</strong></p>
</div>

---

## 📖 Overview

**DoryBrain** is an in-silico laboratory designed for the rigorous scientific study of cognitive architectures. It merges **Reinforcement Learning (RL)** with **Episodic Memory**, and uses an **Evolutionary Engine** to autonomously discover optimal hyperparameter configurations. 

This project was built with a **falsification-first** methodology, prioritizing extreme testing, negative controls, and equivalence testing over simple confirmatory results.

### Core Discoveries (The F022 Hypothesis)
Through extensive global landscape scanning (Global Grid Search), we discovered that evolution does not seek a delicate "needle in a haystack" optimal configuration. Instead, it finds a massive **Pareto Plateau**. Once the brain's Replay mechanism (Memory amplification) crosses an activation saturation threshold, any further investment in parameter optimization offers *no practically meaningful improvement* for both performance and survival. 

---

## ✨ Key Features

*   **🧬 Adaptive Memory Strategy:** An RL agent that systematically forgets obsolete curiosity counts while retaining core semantic knowledge (Q-values), preventing toxic replays and catastrophic interference during environmental shifts.
*   **🌍 System Physics Engine:** A customizable, rule-based simulation environment where agents must manage resources, balance work cost vs. rest gain, and navigate harsh constraints.
*   **⚙️ Evolutionary Engine:** Automates the hyperparameter tuning process (learning rate, discount factor, replay capacity/intensity) through natural selection, cross-over, and mutation over multiple generations.
*   **🌋 Resilience & Catastrophe Testing:** Built-in tools to inject mid-lifetime dose-response shocks (Physics, Cost, Resource, Opportunity) to test how robust the cognitive architecture is against sudden, extreme changes.
*   **📊 Rigorous Statistical Tooling:** Instead of relying on flawed NHST ($p > 0.05$), DoryBrain evaluates architectural equivalence using **TOST (Two One-Sided Tests)**, Kruskal-Wallis, and AIC/BIC model comparisons for continuous saturating functions.

---

## 🛠️ Architecture

1.  `infrastructure/runner/`: The simulation core. Defines the physics, resource constraints, and terminal states.
2.  `infrastructure/evolution/`: The genetic algorithm core. Contains `CognitiveGenome` (the hyperparameters) and `Population` (generation transitions and mutations).
3.  `experiments/`: Contains various Actor implementations ranging from Random, Baseline Q-learning, to the final `E019C_Cognitive` (Adaptive Memory) agent.
4.  `results/`: Holds the extracted data, trajectory mapping, and statistical reports from the 7 experimental phases.

---

## 🔬 The 7-Phase Falsification Workflow

The project is structured as a cumulative chain of evidence, designed to refute competing hypotheses:
*   **Phases 1-2**: Establish baselines and reject simpler explanations.
*   **Phases 3-6**: Incrementally increase policy capability, culminating in the evolutionary discovery of Adaptive Memory.
*   **Phase 7**: The capstone experiment.
    *   **7A & 7B**: Global Empirical Fitness Landscape mapping (discovery of the Plateau).
    *   **7C**: Quadratic Interaction Regression (proving zero epistasis).
    *   **7D**: Cross-environment model comparison (proving continuous saturating mechanisms over binary thresholds).
    *   **7E**: Resilience TOST Equivalence testing (proving the Diminishing Returns hypothesis).

---

## 🚀 Reproducibility

A core tenet of DoryBrain is reproducibility. All experiments, seeds, and statistical tests can be re-run locally.

### Prerequisites
*   Python 3.9+
*   `numpy`, `pandas`, `scipy`, `statsmodels`

### Running an Experiment
To re-run the final Resilience Equivalence testing (Phase 7E):
```bash
python run_phase7E_resilience.py
```
To run the statistical analysis and generate the TOST equivalence reports:
```bash
python analyze_phase7E.py
```

---

<div align="center">
  <i>"A hypothesis earns credibility not because it survives supportive experiments, but because it survives experiments specifically designed to refute it."</i>
</div>
