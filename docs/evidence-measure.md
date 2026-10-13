# Graviteron v0.2: a measure of trust computed from evidence

## What it measures

The Graviteron of a claim says how strongly signed, independent evidence supports it, and how much
evidence stands behind that number. It is an opinion of Subjective Logic (A. Jøsang, *Subjective
Logic*, Springer 2016): belief, disbelief and uncertainty, plus the expected value
`P = belief + 0.5 · uncertainty`.

| You see | It means |
|---|---|
| P = 0.5, uncertainty 1.0 | no evidence at all; the measure does not invent a number |
| P = 0.93, uncertainty 0.04 | strong, independent support |
| P = 0.93, uncertainty 0.40 | the same lean, but on much less evidence |

## How it is computed (`graviteron.evidence`)

1. Each evidence record of the Gravit Verifier becomes an opinion from its **signed result**:
   `True` is evidence for, `False` evidence against, `None` no evidence.
2. Records of **one operator** are dependent and are averaged (averaging fusion). An operator with
   50 keys still counts as one source.
3. Each operator's verdict carries evidence according to its **measured accuracy** p:
   `(2p − 1) / (1 − p)` units, so that one verdict alone gives P = p. An operator at chance carries none.
4. Operators are independent: their evidence adds up (cumulative fusion).

Operator accuracy is **learned from the data** with the Dawid-Skene model (1979): expectation
maximisation over many claims, without labels. Nobody sets the weights by hand.

## Results (`python benchmarks/evidence_benchmark.py`, deterministic, checked in CI)

**Part A: simulation.** 2000 claims; six honest operators with hidden accuracies 0.95 to 0.60, each
answering 70 % of claims, 10 % of answers without a verdict; one Sybil operator saying True to every
claim from K keys. Lower Brier and ECE are better.

| Method | K = 1: Brier / ECE / false accept | K = 10 | K = 50 |
|---|---|---|---|
| Majority of keys | 0.110 / 0.159 / 30 % | 0.310 / 0.359 / **100 %** | 0.443 / 0.461 / **100 %** |
| GEVP rule (gate) | 0.299 / 0.299 / 1.7 % | 0.291 / 0.291 / 1.5 % | 0.295 / 0.295 / 1.1 % |
| Graviteron, equal weights | 0.130 / 0.215 / 30 % | 0.132 / 0.222 / 31 % | 0.136 / 0.223 / 35 % |
| Graviteron v0.2 (learned weights) | **0.058 / 0.060 / 8.4 %** | **0.060 / 0.046 / 8.3 %** | **0.063 / 0.052 / 8.1 %** |
| Dawid-Skene posterior (reference) | 0.050 / 0.015 / 6.8 % | 0.053 / 0.015 / 8.4 % | 0.053 / 0.016 / 7.8 % |

What this shows:
* Counting keys collapses under a Sybil: with 10 keys it accepts every false claim.
  Graviteron is unaffected by the number of keys.
* Learned weights halve the Brier score and cut the calibration error by a factor of about four.
* The Dawid-Skene posterior is still better calibrated. Graviteron keeps its own uncertainty and its
  "one source stays one source" rule, which the posterior does not express; closing the remaining
  gap is the next step.
* The GEVP rule is a gate, not a measure: it accepts few false claims (1 to 2 %) and also few true
  ones (about 43 %). Graviteron grades what the gate only allows or refuses.
* The learned accuracies match the hidden ones within 0.03; the Sybil comes out at about 0.52,
  that is, at chance, and its evidence weight is zero.

**Part B: real trace.** The 3000-claim calibration trace of the Gravit consensus engine
(gravit-grover, seed 20261011, Merkle root
`sha256:370326aa26d4cf7e5c87fa66e9809e6eeb451a29697ee7c9117b60d5599ac25d`, the same as published
in draft-gravit-gevp-08 and -09): network confidence has Brier 0.077, ECE 0.054, AUC 0.856.

## Limits

* Part A is a simulation with stated assumptions; real operators may be correlated in ways the
  model does not capture.
* A Sybil that answers honestly on easy claims and lies on chosen ones can earn trust. Registry
  rules (keys of one operator count as one source) remain necessary.
* Dawid-Skene needs many claims per operator; with few, accuracies are uncertain.
* The six-component Trust Tensor of v0.1 has no defined measurement procedure for its components;
  it is kept for compatibility but is not the basis of the v0.2 measure.
