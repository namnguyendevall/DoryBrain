# Threats to Validity

This document outlines the methodological rigor of the Cognitive Sequence Research Project (CSRP), cataloging known threats to validity and the mitigations in place. This ensures the findings are robust and the boundaries of their applicability are clear.

## 1. Internal Validity
*Are the observed effects (e.g., boundary invariance) truly caused by the independent variables (policy expressiveness), or could they be driven by confounding factors?*

- **Mitigation - Deterministic Simulator**: The simulation dynamics are fully deterministic.
- **Mitigation - Fixed Random Seeds**: Batch runs use 100 fixed seeds (1 to 100) across all agents and environments to ensure identical initial states and random variable streams (if any are introduced).
- **Mitigation - Pre-registration**: Parameters (e.g., $N=5$, $\alpha=0.2$) and state transition logic are pre-registered before execution. No post-hoc tuning or hyperparameter sweeping is allowed, preventing p-hacking.
- **Mitigation - Isomorphic Controls**: Every new computational capability is tested alongside a structural control (e.g., `E005_Control`) that matches the policy's complexity (number of states, transition architecture) but isolates the semantic trigger. This confirms that performance shifts are due to the semantic awareness, not just structural complexity.

## 2. Construct Validity
*Do our metrics actually measure the theoretical concepts they are supposed to represent?*

- **Mitigation - CRT (Critical Recovery Threshold)**: Represents the *boundary shift*. It is strictly pre-defined (e.g., the lowest `rest_gain` where median `work_rate` over the last 200 ticks is $> \epsilon$) rather than relying on qualitative visual inspection of graphs.
- **Mitigation - Work Rate / Total Productive Work**: Represents *functional throughput*. The Comatose state is successfully captured because the metric measures *effective* work (successful action), not just intention to work.

## 3. External Validity
*Can these findings be generalized beyond this specific experimental setup?*

- **Limitation**: The current results strictly apply to the specific resource dynamics environment defined in CSRP-0001 v0.1.0 (with a single bounded resource, fixed work costs, and variable recovery rates).
- **Mitigation**: We do not claim that these phase boundaries exist universally across all possible MDPs or environments. Future protocols (e.g., CSRP-0002) would be needed to test boundary existence in environments with multiple resource types or non-linear physics.

## 4. Conclusion Validity
*Are our conclusions statistically and logically sound based on the data?*

- **Mitigation - Sample Size**: Every batch is executed over 100 seeds, providing sufficient statistical power to smooth out edge cases.
- **Mitigation - Aggregate Measures**: Metrics like CRT rely on majority/median aggregation (e.g., $\ge 95\%$ of seeds must pass the criterion), rejecting outliers or transient "lucky" runs.
- **Mitigation - Restrained Language**: Conclusions are strictly scoped to the evaluated classes. If E009 (depth-3 planning) fails to break the boundary, the conclusion is restricted to "No evaluated policy class up to depth-limited planning (depth = 3) altered the boundary", avoiding the unprovable claim that "planning never works".
