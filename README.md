# Graviteron — The Fundamental Unit of Verifiable Trust

[![CI/CD](https://github.com/gravit-open-network-foundation/graviteron/actions/workflows/ci.yml/badge.svg)](https://github.com/gravit-open-network-foundation/graviteron/actions)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](./LICENSE)

**Graviteron** (GU) is the first standardized, computable unit of verifiable trust in the age of autonomous AI agents.

Just as the *meter* measures length, the *kilogram* measures mass, and the *second* measures time — **Graviteron** measures **epistemic reliability** — the verifiable weight of truth.

## v0.2: Graviteron computed from evidence (13 Oct 2026)

Graviteron v0.2 is computed from the **signed evidence records** of the
[Gravit Verifier](https://github.com/gravit-open-network-foundation/verifier), with
Subjective Logic (belief, disbelief, uncertainty) and operator weights **learned from data**
(Dawid-Skene), and it is checked for **calibration**: a score of 0.9 should be right about 90 % of the time.

```python
from graviteron.evidence import graviteron, dawid_skene, evidence_from_accuracy
g = graviteron([("operator-a", True), ("operator-b", True), ("operator-c", None)])
g.expected, g.u      # 0.75 on two independent verdicts, with uncertainty 0.5
```

In a reproducible benchmark with a Sybil operator using 1, 10 or 50 keys, counting keys accepts
**every** false claim once the Sybil has 10 keys; Graviteron v0.2 accepts about 8 %, whatever the
number of keys, with a calibration error of 0.05. Method, all results and limits:
[docs/evidence-measure.md](docs/evidence-measure.md) · `python benchmarks/evidence_benchmark.py`

## Corrections (13 Oct 2026)

The text below is kept as it was; these statements in it are corrected:

* **θ-critical 0.731.** The threshold came from a calibration that could not be reproduced and
  is no longer recommended (draft-gravit-gevp-08). The reproduced calibration shows the same
  rates for every θ between 0.11 and 0.78.
* **Trust Tensor.** Its six components have no defined measurement procedure, and the weights of 1/6
  are not derived from data. It remains in the code for compatibility (v0.1) but is not the basis of
  the v0.2 measure.
* **"Calibrated to match human evaluator audit limits"** (docs/mathematics.md) was not supported
  by any measurement. Calibration is now measured; see the benchmark.
* **Package.** Graviteron is not published on PyPI; the former PyPI badge was removed.
  Install from this repository: `pip install -e .`


---

## Manifesto

We are entering the age of autonomous agents.

The critical missing infrastructure layer is no longer raw intelligence — it is **verifiable trust**.

**Graviteron** is the fundamental unit of computable trust. It transforms probabilistic outputs of large language models and autonomous agents into immutable, auditable, and quantifiable knowledge.

Built on the **Gravit Open Network**, Graviteron makes trust measurable, comparable, and interoperable across systems.

**Trust must become computable. Truth must become verifiable. Intelligence must become reliable.**

**Graviteron** is the gravity that holds reliable intelligence together.

---

## Core Concept

**Graviteron** is a quantitative measure of epistemic reliability assigned to any unit of knowledge or agent decision through the Gravit stack.

A statement, decision, or model output with a score of **0.97 Graviteron** carries significantly higher verifiable weight than one with **0.41 Graviteron**.

---

## Technical Foundation

### 3-Layer Verification Model
Graviteron now supports an explicit epistemic verification workflow:

1. L1 — factual consensus
2. L2 — logical proof / formal verification
3. L3 — continuum / semantic escalation

A verification result below the θ-critical threshold ($0.731$) is automatically marked for continuum escalation.

### 1. Gravit Triad
- **Identity Layer**
- **Reputation Layer**
- **Epistemic Validation Layer** ← Graviteron is primarily computed here

### 2. Core Components
- **EES** — Epistemic Execution Systems
- **Ω Trace** (History Keeper) — Immutable reasoning trajectory
- **Trust Tensor** — 6-dimensional tensor evaluating consistency, stability, adversarial robustness, factual grounding, reasoning soundness, and recovery score.
- **GQRVP** — Gravit Quantum-Ready Verification Protocol
- **Gravit Continuum** — Decentralized network of semantic validators

### 3. Mathematical Basis
Graviteron is derived from the **Trust Tensor** $T \in \mathbb{R}^6$, processed through:
- Gower similarity metrics
- Grover amplification
- Gossip-based probabilistic truth assessment
- Epistemic stability under adversarial conditions

The final Graviteron value is a normalized scalar $G \in [0, 1]$, where:
- $G \approx 1.0$: Highly stable, verifiable epistemic structure
- $G \approx 0.0$: Unstable or unverifiable output

---

## Repository Structure

```
graviteron/
├── docs/
│   ├── specification.md          # Full technical specification
│   ├── mathematics.md            # Deep mathematical foundation
│   ├── integration-guide.md      # How to integrate with other systems
│   └── roadmap.md                # Development milestone roadmap
├── papers/
│   └── graviteron-whitepaper.md  # Graviteron research whitepaper
├── examples/
│   └── agent_integration.py      # Python integration examples
├── schema/
│   └── graviteron-json-schema.json
├── src/
│   └── graviteron/               # Core library and API
├── tests/                        # Unit and integration tests
├── LICENSE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
└── README.md
```

---

## Installation & Quick Start

Install the package directly:
```bash
pip install .
```

To run the API development server locally:
```bash
pip install -e ".[dev]"
python -m uvicorn graviteron.api.fastapi_app:app --reload --port 8000
```

Compute a local Graviteron score:
```python
from graviteron import GraviteronEngine, TrustTensor

engine = GraviteronEngine()
tensor = TrustTensor(
    consistency=0.95,
    stability=0.88,
    adversarial_robustness=0.92,
    factual_grounding=0.97,
    reasoning_soundness=0.90,
    recovery_score=0.85
)

score, trace = engine.compute_with_trace(tensor, input_data={"query": "hello"})
print(f"Score: {score}")
print(f"Trace ID: {trace.trace_id}")
```

---

## Get Involved

This repository is maintained by the **Gravit Open Network Foundation**.

We welcome researchers, engineers, and institutions working on verifiable AI, epistemic systems, and agentic infrastructure.

**Website:** [graviteron.info](https://www.graviteron.info)  
**Main Project:** [Gravit Open Network](https://www.gravit.space)
