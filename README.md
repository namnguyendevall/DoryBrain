<div align="center">
  <h1>🧠 DoryBrain (CSRP)</h1>
  <p><strong>The adaptive cognitive engine behind Dory, an autonomous AI work assistant.</strong></p>
</div>

---

## 📖 Overview

**Dory** is an autonomous AI work assistant built to help people create value, automate work, and generate income.

**DoryBrain** is the research engine that powers Dory's adaptive learning capabilities. While modern LLMs provide reasoning and knowledge, DoryBrain explores how an AI assistant can continuously improve from experience through **Reinforcement Learning**, **Adaptive Memory**, and **Evolutionary Optimization**.

```text
 User
   │
   ▼
 Dory
 (AI Assistant)
   │
   ▼
 DoryBrain
 (Adaptive Cognitive Engine)
```

### Vision

Our long-term vision is to build an AI assistant that works alongside people as a productive teammate—planning, creating, automating, learning from experience, and continuously improving to generate real-world value.

---

## 🔬 Core Discoveries (The F022 Hypothesis)

DoryBrain was built with a **falsification-first** methodology, prioritizing extreme testing, negative controls, and equivalence testing over simple confirmatory results.

Through extensive global landscape scanning (Global Grid Search), we discovered that evolution does not seek a delicate "needle in a haystack" optimal configuration. Instead, it finds a massive **Pareto Plateau**. Once the brain's Replay mechanism (Memory amplification) crosses an activation saturation threshold, any further investment in parameter optimization offers *no practically meaningful improvement* for both performance and survival. 

---

## 🆚 Why DoryBrain Is Different (RL vs. LLM)

One of the biggest questions in AI today is the relationship between **Reinforcement Learning (RL)** and **Large Language Models (LLMs)**. At first glance, they appear to solve similar problems, but they address fundamentally different aspects of intelligence.

### Large Language Models
LLMs are pre-trained on enormous amounts of human-generated text. Through this pretraining, they acquire broad prior knowledge about language, programming, reasoning patterns, and many real-world concepts. This allows an LLM-based agent to immediately perform tasks such as writing code, using software tools, browsing the web, and following natural language instructions.

However, an LLM's behavior is largely determined by its pretraining and subsequent fine-tuning. While modern systems can learn from new interactions through external memory or retrieval, *continuously adapting their core behavior* remains an active research challenge.

### DoryBrain
DoryBrain starts from a completely different assumption. Instead of assuming extensive prior knowledge, it studies how a cognitive system can learn adaptive behavior from raw interaction with an environment.

The project investigates questions such as:
* How should an agent remember past experiences?
* When should old memories be forgotten?
* How does replay influence learning?
* Which cognitive parameters are actually important?
* How do robust cognitive architectures emerge through evolution?

Rather than teaching an agent *what* to think, DoryBrain studies *how learning itself should work*.

### Complementary, Not Competing
DoryBrain is not intended to replace LLMs. Instead, it explores a complementary layer of intelligence:
* **LLMs** provide extensive prior knowledge and reasoning capabilities.
* **DoryBrain** investigates adaptive learning mechanisms that operate through ongoing interaction and experience.

A future cognitive agent could combine both: an LLM for language understanding and planning, and a DoryBrain-inspired adaptive learning system for long-term experience accumulation, memory management, and continual adaptation.

### Research Vision
The long-term vision of DoryBrain is not to build another chatbot. It is to develop and experimentally validate general cognitive learning mechanisms that can eventually be integrated into future AI agents, providing more robust adaptation and scientifically grounded cognitive architectures.

> **Note on Generalization:** DoryBrain is explicitly designed to study adaptation under changing environments. Whether these same adaptive mechanisms generalize to substantially different domains remains an empirical question rather than an assumption.

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

## 🌐 The Dory Ecosystem

```text
Dory
└── AI Work Assistant
    ├── Browser Automation
    ├── Coding
    ├── Research
    ├── Content Creation
    ├── Business Automation
    ├── Tool Use
    └── DoryBrain (CSRP)
        ├── Reinforcement Learning
        ├── Adaptive Memory
        ├── Evolutionary Optimization
        ├── Continual Learning
        └── Cognitive Systems Research
```

---

<div align="center">
  <i>"A hypothesis earns credibility not because it survives supportive experiments, but because it survives experiments specifically designed to refute it."</i>
</div>
