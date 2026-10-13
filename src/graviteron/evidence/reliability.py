"""Operator reliability learned from data: the Dawid-Skene model (1979), binary case.

Each operator j reports a verdict on many claims. The model assumes a hidden true
label per claim and, for each operator, a sensitivity (P(says true | claim true))
and a specificity (P(says false | claim false)). Expectation-maximisation finds
the parameters that best explain the observed agreement and disagreement, with
or without known labels. Verdicts None are simply missing.

Weights are therefore measured, not set by hand: an operator that often
disagrees with the consensus of the others gets a low reliability.
"""

import math
from typing import Dict, List, Mapping, Optional, Tuple

Verdicts = Mapping[str, Mapping[str, Optional[bool]]]  # claim -> operator -> verdict


def dawid_skene(
    verdicts: Verdicts, iterations: int = 50, smoothing: float = 1.0, init_posterior: Optional[Mapping[str, float]] = None
) -> Tuple[Dict[str, float], Dict[str, dict], float]:
    """Return (posterior P(claim true) per claim, per-operator {sensitivity, specificity, accuracy}, prior)."""
    claims = sorted(verdicts)
    operators = sorted({op for c in claims for op in verdicts[c]})
    # initialise with the share of "true" verdicts (majority vote per operator, not per key)
    post: Dict[str, float] = {}
    for c in claims:
        votes = [v for v in verdicts[c].values() if v is not None]
        post[c] = (init_posterior or {}).get(c, (sum(votes) + 1.0) / (len(votes) + 2.0))
    params: Dict[str, dict] = {}
    prior = 0.5
    for _ in range(iterations):
        # M-step: operator parameters with Laplace smoothing
        prior = (sum(post.values()) + smoothing) / (len(claims) + 2 * smoothing)
        for op in operators:
            tp = fn = tn = fp = 0.0
            for c in claims:
                v = verdicts[c].get(op)
                if v is None:
                    continue
                p = post[c]
                if v:
                    tp += p
                    fp += 1 - p
                else:
                    fn += p
                    tn += 1 - p
            sens = (tp + smoothing) / (tp + fn + 2 * smoothing)
            spec = (tn + smoothing) / (tn + fp + 2 * smoothing)
            params[op] = {"sensitivity": sens, "specificity": spec}
        # E-step: posterior of each claim
        for c in claims:
            lt, lf = math.log(prior), math.log(1 - prior)
            for op, v in verdicts[c].items():
                if v is None:
                    continue
                s, t = params[op]["sensitivity"], params[op]["specificity"]
                lt += math.log(s if v else 1 - s)
                lf += math.log(1 - t if v else t)
            m = max(lt, lf)
            post[c] = math.exp(lt - m) / (math.exp(lt - m) + math.exp(lf - m))
    for op in operators:
        p = params[op]
        p["accuracy"] = prior * p["sensitivity"] + (1 - prior) * p["specificity"]
    return post, params, prior


def accuracy_table(params: Mapping[str, dict]) -> List[Tuple[str, float]]:
    return sorted(((op, p["accuracy"]) for op, p in params.items()), key=lambda x: -x[1])
