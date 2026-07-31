# O001: Policy Equivalence Region

## Definition
A **Policy Equivalence Region** is a region of the state space in which multiple distinct local policies converge to an identical trajectory due to the overriding influence of environmental dynamics.

## Context
During Batch 0003, three policies were tested under extreme constraint ladders (`rest_gain <= passive_decay`):
- E000 (Reactive, Fixed Threshold = 20)
- E004 (Adaptive, Threshold dynamically drops to 15 when starving)
- E004_Control (Deterministic, Threshold alternates between 15 and 20)

## Observation
Despite the different policy mechanisms and differing internal states, all three actors produced an identical emergent trajectory and boundary (Comatose fraction = 1.00, Work Rate approaching 0).

The policies instructed different behavior given the state (e.g., E004 attempting to `work` at resource level 15 while E000 would `rest`). However, because the net energy dynamics (`rest_gain - passive_decay`) were zero or negative, the physical `resource` could never reach 15. The system physics dominated the actors' internal logic, forcing them down the exact same physical path.

This abstraction highlights that the emergent boundary observed in Phase 1 and 2 is an intrinsic property of the system's dynamics, independent of the local policy variations tested.
