# Graviteron v0.2 benchmark

Lower Brier, log loss and ECE are better; higher AUC is better.

## Part A, sybil keys 1

| Method | Brier | Log loss | ECE | AUC | Accuracy | False accept | True accept |
|---|---|---|---|---|---|---|---|
| key_majority | 0.1099 | 0.5678 | 0.1593 | 0.9593 | 0.847 | 0.3013 | 0.9864 |
| gevp_rule | 0.2985 | 8.2479 | 0.2985 | 0.71 | 0.7015 | 0.0165 | 0.4365 |
| graviteron_equal | 0.1301 | 0.4305 | 0.2152 | 0.9642 | 0.847 | 0.3013 | 0.9864 |
| graviteron_discounted | 0.1189 | 0.4136 | 0.2571 | 0.9812 | 0.9355 | 0.0733 | 0.9437 |
| graviteron_weighted | 0.0582 | 0.214 | 0.06 | 0.9783 | 0.9255 | 0.0836 | 0.934 |
| dawid_skene_posterior | 0.0495 | 0.169 | 0.0151 | 0.9824 | 0.938 | 0.0681 | 0.9437 |

Learned operator accuracy (true values: a .95, b .90, c .85, d .80, e .70, f .60; Sybil says True always): op-a 0.957, op-b 0.899, op-c 0.855, op-d 0.787, op-e 0.714, op-f 0.627, op-sybil 0.515

## Part A, sybil keys 10

| Method | Brier | Log loss | ECE | AUC | Accuracy | False accept | True accept |
|---|---|---|---|---|---|---|---|
| key_majority | 0.3099 | 1.0214 | 0.3594 | 0.951 | 0.508 | 1.0 | 1.0 |
| gevp_rule | 0.2905 | 8.0268 | 0.2905 | 0.7138 | 0.7095 | 0.0152 | 0.4429 |
| graviteron_equal | 0.1317 | 0.4345 | 0.2221 | 0.962 | 0.8375 | 0.314 | 0.9843 |
| graviteron_discounted | 0.1186 | 0.4131 | 0.2467 | 0.9805 | 0.926 | 0.0833 | 0.935 |
| graviteron_weighted | 0.0601 | 0.2159 | 0.046 | 0.9778 | 0.9185 | 0.0833 | 0.9203 |
| dawid_skene_posterior | 0.0526 | 0.1747 | 0.015 | 0.9818 | 0.926 | 0.0843 | 0.936 |

Learned operator accuracy (true values: a .95, b .90, c .85, d .80, e .70, f .60; Sybil says True always): op-a 0.957, op-b 0.904, op-c 0.835, op-d 0.816, op-e 0.697, op-f 0.609, op-sybil 0.519

## Part A, sybil keys 50

| Method | Brier | Log loss | ECE | AUC | Accuracy | False accept | True accept |
|---|---|---|---|---|---|---|---|
| key_majority | 0.4425 | 1.6397 | 0.4606 | 0.9529 | 0.505 | 1.0 | 1.0 |
| gevp_rule | 0.2945 | 8.1373 | 0.2945 | 0.7083 | 0.7055 | 0.0111 | 0.4277 |
| graviteron_equal | 0.1359 | 0.4435 | 0.223 | 0.9612 | 0.821 | 0.3515 | 0.9901 |
| graviteron_discounted | 0.1227 | 0.4226 | 0.2576 | 0.9781 | 0.931 | 0.0747 | 0.9366 |
| graviteron_weighted | 0.0628 | 0.2275 | 0.052 | 0.9742 | 0.918 | 0.0808 | 0.9168 |
| dawid_skene_posterior | 0.053 | 0.1827 | 0.0158 | 0.9795 | 0.932 | 0.0778 | 0.9416 |

Learned operator accuracy (true values: a .95, b .90, c .85, d .80, e .70, f .60; Sybil says True always): op-a 0.956, op-b 0.887, op-c 0.841, op-d 0.791, op-e 0.684, op-f 0.584, op-sybil 0.516

## Part B, real Grover trace

- gravit-grover theta-calibration.jsonl (3000 claims, seed 20261011, Merkle root sha256:370326aa26d4cf7e5c87fa66e9809e6eeb451a29697ee7c9117b60d5599ac25d)
- network confidence: Brier 0.0774, log loss 0.4084, ECE 0.0535, AUC 0.8564, accuracy 0.922
