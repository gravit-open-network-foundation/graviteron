"""Does a score mean what it says? Proper scoring rules and calibration.

A trust measure is calibrated when, among all claims it scores near 0.9, about
90 % are true. These functions compare scores with known outcomes.
"""

import math
from typing import Dict, List, Sequence


def brier(scores: Sequence[float], truth: Sequence[bool]) -> float:
    """Mean squared error of the probability; 0 is perfect, 0.25 is a coin flip at 0.5."""
    return sum((s - (1.0 if t else 0.0)) ** 2 for s, t in zip(scores, truth)) / len(scores)


def log_loss(scores: Sequence[float], truth: Sequence[bool], eps: float = 1e-12) -> float:
    total = 0.0
    for s, t in zip(scores, truth):
        s = min(max(s, eps), 1 - eps)
        total -= math.log(s if t else 1 - s)
    return total / len(scores)


def reliability_bins(scores: Sequence[float], truth: Sequence[bool], bins: int = 10) -> List[Dict]:
    out = []
    for k in range(bins):
        lo, hi = k / bins, (k + 1) / bins
        idx = [i for i, s in enumerate(scores) if (lo <= s < hi) or (k == bins - 1 and s == 1.0)]
        if idx:
            out.append(
                {
                    "bin": f"[{lo:.1f}, {hi:.1f})",
                    "n": len(idx),
                    "mean_score": sum(scores[i] for i in idx) / len(idx),
                    "share_true": sum(1 for i in idx if truth[i]) / len(idx),
                }
            )
    return out


def ece(scores: Sequence[float], truth: Sequence[bool], bins: int = 10) -> float:
    """Expected calibration error: weighted gap between score and observed frequency."""
    n = len(scores)
    return sum(b["n"] / n * abs(b["mean_score"] - b["share_true"]) for b in reliability_bins(scores, truth, bins))


def auc(scores: Sequence[float], truth: Sequence[bool]) -> float:
    """Probability that a true claim scores above a false one (ties count half)."""
    pos = [s for s, t in zip(scores, truth) if t]
    neg = [s for s, t in zip(scores, truth) if not t]
    if not pos or not neg:
        return float("nan")
    ranked = sorted([(s, 1) for s in pos] + [(s, 0) for s in neg])
    rank_sum, i = 0.0, 0
    while i < len(ranked):
        j = i
        while j < len(ranked) and ranked[j][0] == ranked[i][0]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        rank_sum += avg_rank * sum(1 for k in range(i, j) if ranked[k][1] == 1)
        i = j
    return (rank_sum - len(pos) * (len(pos) + 1) / 2.0) / (len(pos) * len(neg))


def report(scores: Sequence[float], truth: Sequence[bool]) -> Dict[str, float]:
    acc = sum(1 for s, t in zip(scores, truth) if (s >= 0.5) == t) / len(scores)
    neg = [s for s, t in zip(scores, truth) if not t]
    pos = [s for s, t in zip(scores, truth) if t]
    far = sum(1 for s in neg if s >= 0.5) / len(neg) if neg else float("nan")
    tar = sum(1 for s in pos if s >= 0.5) / len(pos) if pos else float("nan")
    return {
        "brier": brier(scores, truth),
        "log_loss": log_loss(scores, truth),
        "ece": ece(scores, truth),
        "auc": auc(scores, truth),
        "accuracy_at_0.5": acc,
        "false_accept_rate": far,
        "true_accept_rate": tar,
        "n": len(scores),
    }
