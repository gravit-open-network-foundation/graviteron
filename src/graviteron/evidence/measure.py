"""The Graviteron of a claim, computed from signed evidence records.

Input: records in the Gravit Verifier format (the field `result` is the
verifier's signed verdict: True supports, False contradicts, None gives no
verdict) and, for each record, the operator responsible for its key.

Steps, each one checkable:
  1. each record becomes an opinion: True -> one unit of evidence for,
     False -> one unit against, None -> no evidence (pure uncertainty);
  2. records of one operator are dependent: averaging fusion, so an operator
     with many keys still counts as one source (no Sybil amplification);
  3. each operator's opinion is discounted by its reliability (trust in [0, 1]);
     without a reliability estimate every operator gets the same trust;
  4. operators are independent: cumulative fusion.

The Graviteron is the resulting opinion. Its `expected` value is the measure;
its `uncertainty` says how much evidence stands behind it. A single operator
can never produce low uncertainty on its own, which is the "no aggregation
laundering" rule of GEVP expressed as a number.
"""

import math
from collections import defaultdict
from typing import Dict, Iterable, Mapping, Optional, Tuple

from .opinion import PRIOR_WEIGHT, Opinion, averaging_fusion, cumulative_fusion, discount, from_evidence

VERSION = "0.3.0"


def record_opinion(result, a: float = 0.5) -> Opinion:
    if result is True:
        return from_evidence(1.0, 0.0, a)
    if result is False:
        return from_evidence(0.0, 1.0, a)
    if result is None:
        return from_evidence(0.0, 0.0, a)
    raise ValueError("result must be True, False or None")


def evidence_from_accuracy(p: float, cap: float = 50.0) -> float:
    """Evidence units carried by one verdict of a source that is right with probability p.

    Chosen so that a single verdict, alone, yields an opinion whose expected value is p:
    with prior weight W = 2 and base rate 0.5, P = (r + 1) / (r + 2) = p gives r = (2p - 1) / (1 - p).
    A source at chance (p <= 0.5) carries no evidence; a near-perfect source is capped.
    """
    if p <= 0.5:
        return 0.0
    if p >= 1.0:
        return cap
    return min(cap, (2.0 * p - 1.0) / (1.0 - p))


def trust_from_accuracy(p: float) -> float:
    """A source right with probability p carries information only above chance: trust = 2p - 1, at least 0."""
    return max(0.0, min(1.0, 2.0 * p - 1.0))


def graviteron(
    records: Iterable[Tuple[str, object]],
    reliability: Optional[Mapping[str, float]] = None,
    base_rate: float = 0.5,
    default_trust: float = 1.0,
    evidence_weight: Optional[Mapping[str, float]] = None,
) -> Opinion:
    """records: (operator, result) pairs.

    reliability: operator -> trust in [0, 1], applied by discounting (variant "discount");
    evidence_weight: operator -> evidence units per verdict, e.g. evidence_from_accuracy(p)
    (variant "weighted"); operators missing from the map count one unit.
    """
    by_op: Dict[str, list] = defaultdict(list)
    for operator, result in records:
        o = record_opinion(result, base_rate)
        if evidence_weight is not None and result is not None:
            k = evidence_weight.get(operator, 1.0)
            o = from_evidence(k if result else 0.0, 0.0 if result else k, base_rate)
        by_op[operator].append(o)
    fused = []
    for operator, ops in sorted(by_op.items()):
        trust = (reliability or {}).get(operator, default_trust)
        fused.append(discount(averaging_fusion(ops, base_rate), trust))
    if not fused:
        return Opinion(0.0, 0.0, 1.0, base_rate)
    return cumulative_fusion(fused, base_rate)


__all__ = [
    "VERSION",
    "PRIOR_WEIGHT",
    "graviteron",
    "graviteron_v3",
    "operator_verdicts",
    "record_opinion",
    "trust_from_accuracy",
    "evidence_from_accuracy",
]


def operator_verdicts(records: Iterable[Tuple[str, object]]) -> Dict[str, Optional[bool]]:
    """One verdict per operator: the majority of its keys' non-null verdicts; None if none or tied."""
    by_op: Dict[str, list] = defaultdict(list)
    for operator, result in records:
        if result not in (True, False, None):
            raise ValueError("result must be True, False or None")
        by_op[operator].append(result)
    out: Dict[str, Optional[bool]] = {}
    for operator, results in sorted(by_op.items()):
        votes = [r for r in results if r is not None]
        yes = sum(1 for r in votes if r)
        out[operator] = None if not votes or 2 * yes == len(votes) else 2 * yes > len(votes)
    return out


def graviteron_v3(
    records: Iterable[Tuple[str, object]], params: Mapping[str, Mapping[str, float]], prior: float = 0.5, cap: float = 50.0
) -> Dict[str, float]:
    """Graviteron v0.3: the expected value combines independent operators as Bayes does.

    Each operator's verdict multiplies the odds by its likelihood ratio, from its measured
    sensitivity and specificity (Dawid-Skene): True by sens / (1 - spec), False by (1 - sens) / spec.
    Keys of one operator still give one verdict. Operators without parameters are ignored.
    The uncertainty is the Subjective Logic uncertainty of the same evidence (v0.2 weighting), so
    the result says both how likely the claim is and how much evidence stands behind it.
    """
    verdicts = operator_verdicts(records)
    log_odds = math.log(prior / (1.0 - prior))
    weights: Dict[str, float] = {}
    for operator, v in verdicts.items():
        p = params.get(operator)
        if p is None or v is None:
            continue
        sens = min(max(p["sensitivity"], 1e-6), 1 - 1e-6)
        spec = min(max(p["specificity"], 1e-6), 1 - 1e-6)
        log_odds += math.log(sens / (1 - spec)) if v else math.log((1 - sens) / spec)
        acc = prior * p["sensitivity"] + (1 - prior) * p["specificity"]
        weights[operator] = evidence_from_accuracy(acc, cap)
    log_odds = max(-50.0, min(50.0, log_odds))
    expected = 1.0 / (1.0 + math.exp(-log_odds))
    sl = graviteron([(op, v) for op, v in verdicts.items()], evidence_weight=weights or None)
    return {
        "expected": expected,
        "uncertainty": sl.u,
        "belief": sl.b,
        "disbelief": sl.d,
        "operators_counted": sum(1 for op, v in verdicts.items() if v is not None and op in params),
        "method": "graviteron-0.3 (Bayes over operators, Dawid-Skene parameters)",
    }
