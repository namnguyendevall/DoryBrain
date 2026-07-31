# Continuous State Research Lab (CSRL) Manifesto

## Research Principles

1. **Every hypothesis must be falsifiable.**
   If a hypothesis cannot be proven wrong by an experiment, it is not science.

2. **Every experiment must define success before execution.**
   The falsification conditions (`expected.md`) must be written before any implementation code (`transition.py`).

3. **Every metric must be reproducible.**
   All experiments must be strictly deterministic, governed by a fixed `--seed`.

4. **Every observation must be immutable.**
   Raw event logs (`observations/raw/`) are append-only and must never be modified by humans or algorithms.

5. **Negative results are first-class knowledge.**
   A falsified hypothesis is a successful experiment. Rejected hypotheses are permanently stored in `knowledge/rejected/` to prevent repeating history.

6. **Implementation never precedes measurement.**
   We do not build complex features (like Memory, Planner, or Habit) until we have empirical metrics proving the system fails without them.

7. **Abstraction follows evidence.**
   Do not abstract components into generic classes or frameworks until experimental data shows that multiple concrete implementations share the exact same underlying physics.
