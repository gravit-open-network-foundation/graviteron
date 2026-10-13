# Graviteron Mathematics

> **Correction (13 Oct 2026).** This page describes v0.1. The Trust Tensor components have no defined
> measurement procedure and the calibration claim in Section 4 was not measured. The evidence-based
> measure of v0.2, with measured calibration, is described in [evidence-measure.md](evidence-measure.md).

## 1. Trust Tensor

The foundation of Graviteron is the **6-dimensional Trust Tensor** $T$:

$$T = [C, S, R, F, N, V] \in \mathbb{R}^6$$

Where:
- **C** — Consistency: Measures uniformity of reasoning pathways across semantic variants.
- **S** — Stability: Evaluates robustness of output over context and temporal changes.
- **R** — Adversarial Robustness: Measures resistance to adversarial prompts, perturbations, and prompt injections.
- **F** — Factual Grounding: Quantifies empirical grounding in validated knowledge bases.
- **N** — Reasoning Soundness: Evaluates the logical flow and consistency of inference steps (reasoning coherence).
- **V** — Recovery / Rehabilitation: Measures the capacity of the model to self-correct and recover from bad states.

## 2. Computation Pipeline

1. **$\Omega$ Trace Generation**: Collect inference path, context, and outputs.
2. **Semantic Comparison**: Run Gower similarity checks on components.
3. **Grover Amplification**: Quantum-inspired search of hypothesis space to locate semantic deviations.
4. **Probabilistic Assessment**: Decentralized validation via consensus protocols across the Gravit Continuum validators.
5. **Tensor Aggregation**: Reduce the multi-dimensional tensor into a singular scalar Graviteron value.

## 3. Final Formula (Simplified)

$$G = \left( \frac{1}{6} \sum_{i=1}^{6} w_i \cdot \text{norm}(T_i) \right) \times A$$

Where:
- $w_i \ge 0$ are dynamic weights normalized such that $\sum w_i = 1$. By default, $w_i = 1/6$ for all $i$.
- $\text{norm}(T_i) \in [0, 1]$ represents the normalized score of each Trust Tensor component.
- $A \in [0, 1]$ is the Adversarial Stability Multiplier derived from the Gravit Continuum validation network:
  $$A = \begin{cases} 
      1.0 & \text{if } R \ge \tau_R \\
      \frac{R}{\tau_R} & \text{if } R < \tau_R
  \end{cases}$$
  where $\tau_R$ is the system-wide adversarial threshold (e.g., $0.7$).

## 4. Key Properties

- **Monotonicity**: $G(T_1) \ge G(T_2)$ holds true if all components of $T_1$ are greater than or equal to $T_2$.
- **Transitivity**: Computes normalized scalars allowing cross-model trust evaluation.
- **Calibration**: Calibrated to match human evaluator audit limits under high risk.
