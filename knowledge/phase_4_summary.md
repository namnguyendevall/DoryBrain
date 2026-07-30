# Phase 4 Summary: Causal Authority and the Activation Boundary

## Objective
Phase 4 aimed to resolve a fundamental question inherited from Phase 3: If increasing an agent's internal intelligence (memory, prediction, planning) cannot shift the Critical Resource Threshold (CRT), does increasing its *action space* to include causal interventions over the environment shift it?

## Findings

1. **F012: Action Expansion vs. Causal Power** (Batch 0009 / E010)
   - Expanding the action space to include non-decaying storage (`STORE`/`RETRIEVE`) increased the agent's temporal robustness, allowing it to survive longer in hostile conditions.
   - However, storage strictly obeys conservation laws. It does not alter the fundamental environmental physics (the net resource flow).
   - **Conclusion**: Action space expansion without causal intervention does not shift the CRT.

2. **F013: Environmental Intervention and the Two-Layered Boundary** (Batch 0010 / E011)
   - The agent was granted "Causal Authority": the ability to permanently improve the environment's `rest_gain` or `passive_decay` at a large upfront cost of 30 resources.
   - When the agent could successfully execute this investment, the physics of the environment changed, and the CRT **measurably shifted**.
   - **Crucial Discovery (The Activation Boundary)**: This causal power revealed a meta-boundary. The environment is defined by two layers:
     - **Layer 1: Sustainability Boundary (CRT)** - Can the agent survive?
     - **Layer 2: Activation Boundary (AT - Activation Threshold)** - Can the agent accumulate the capital required to modify the environment?
   - At the singularity where `rest_gain <= passive_decay`, the agent's net accumulation is $\le 0$. Thus, it is physically impossible to reach the 30-resource cost. The causal authority remains permanently locked, and the boundary is absolute.

## Strategic Implication
Intelligence determines how efficiently an agent operates *within* a world. Causal authority determines whether the agent can *reprogram* the world. But both are ultimately governed by the environment's Activation Boundary.

## Next Steps (Phase 5)
Phase 5 will explore "Causal Discovery and Strategy":
- **E012 (Causal Planner)**: How does a planner handle causal interventions? Can it spontaneously discover *when* and *if* to invest, without a hardcoded threshold?
- **E013 / E014**: Credit assignment over long horizons and competing causal actions (Storage vs. Modification).
