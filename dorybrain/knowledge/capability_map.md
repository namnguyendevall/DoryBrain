# Capability Map

This document tracks the explicit computational capabilities incrementally added to the evaluated policies, providing a clear progression of expressiveness across the CSRP project.

| Capability Class | Policy | Added Information | Added Computation | Result / Shift in CRT |
| :--- | :--- | :--- | :--- | :--- |
| **Reactive Threshold** | `E000` | None | Reactive scalar mapping | Baseline |
| **Minimal Adaptive** | `E004` | Starvation counter (`ticks_since_last_work`) | Scalar state adaptation | No measurable shift |
| **Finite-State Controller** | `E005` | Active FSM state | Path-dependent transitions (Hysteresis) | No measurable shift |
| **Finite-History Memory** | `E006` | History window | Aggregation over sliding window | No measurable shift |
| **Continuous Latent State Estimator** | `E007` | Smooth exponential average | Continuous filtering (EWMA) | Transient altered, Invariant |
| **Predictive Model** | `E008` | Projected future resource | Feed-forward dynamics calculation | Improved local trajectory, Invariant |
| **Planner** | `E009` | Search tree | Depth-limited rollout search | No measurable shift |
| **Action Expansion (Storage)** | `E010` | Non-decaying bank | Resource location transfer | No measurable shift |
| **Causal Authority** | `E011` | Environmental investment | Dynamic parameter modification | **Shifted (where capital is accumulable)** |

## Capability Progression

Phase 1:
**Reactive Control** (Baseline thresholds)
        ↓
Phase 2:
**Internal State** (Memory, FSM, Continuous estimation)
        ↓
Phase 3:
**Predictive Intelligence** (Prediction, Rollout Planning)
        ↓
Phase 4A:
**Resource Control** (Storage without decay)
        ↓
Phase 4B:
**Environmental Intervention** (Causal parameter modification)
        ↓
Phase 4C:
**Activation Constraint** (Capital accumulation singularity)

**Insight**: The boundary invariant is not due to a lack of information, memory, prediction, or planning. The agent's intelligence is ultimately bottlenecked by its **Control Authority** (Causal Power) over the environment. Even with expanded action space allowing non-decaying storage (`E010`), the boundary remains invariant. Causal leverage requires modifying the underlying environmental physics, but is strictly governed by the **Activation Boundary**: if the environment forbids the accumulation of capital, causal authority remains unreachable.
