"""The Graviteron as a unit: weight of evidence in decibans.

Definition (Turing and Good's weight of evidence):

    G = 10 * log10( P(claim | evidence) / P(not claim | evidence) )  -  10 * log10( prior odds )

that is, how far the signed evidence moves the odds, in decibans (dB-like, base 10).

Properties, each tested:
  * 0 G means no evidence either way; positive supports the claim, negative contradicts it.
  * Additive: independent operators add their contributions; keys of one operator count once.
  * Dynamic: a contribution loses weight with a half life if the check is not renewed
    (G_i(t) = G_i * 2 ** (-age / half_life)); renewing the check restores it.
  * Never a bare point: an interval comes from the Beta posterior of the same evidence.
  * A signed contradiction is reported separately and is never averaged away.

Verbal bands follow Jeffreys' scale for Bayes factors (in decibans), so people read
calibrated words instead of false precision.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Mapping, Optional, Tuple

from .measure import operator_verdicts

DB = 10.0 / math.log(10.0)  # decibans per natural log unit

# Jeffreys (1961), Bayes factor scale expressed in decibans, symmetric for support and contradiction
BANDS = [(5.0, "inconclusive"), (10.0, "substantial"), (15.0, "strong"), (20.0, "very strong"), (math.inf, "decisive")]


def band(g: float) -> str:
    a = abs(g)
    for limit, name in BANDS:
        if a < limit:
            word = name
            break
    if word == "inconclusive":
        return word
    return f"{word} support" if g > 0 else f"{word} contradiction"


def decay(weight: float, age_seconds: float, half_life_seconds: Optional[float]) -> float:
    if half_life_seconds is None or age_seconds <= 0:
        return weight
    return weight * 2.0 ** (-age_seconds / half_life_seconds)


# --- Beta quantile (regularized incomplete beta, Lentz continued fraction), no external deps ---

def _betacf(a: float, b: float, x: float) -> float:
    tiny, qab, qap, qam = 1e-300, a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-12:
            break
    return h


def beta_cdf(x: float, a: float, b: float) -> float:
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbt) * _betacf(b, a, 1 - x) / b


def beta_quantile(q: float, a: float, b: float) -> float:
    lo, hi = 0.0, 1.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if beta_cdf(mid, a, b) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _db(p: float) -> float:
    p = min(max(p, 1e-12), 1 - 1e-12)
    return 10.0 * math.log10(p / (1 - p))


@dataclass
class GraviteronReading:
    value: float                          # G in decibans, relative to the prior
    low: float                            # lower end of the interval, decibans
    high: float                           # upper end
    band: str                             # verbal band (Jeffreys)
    contributions: Dict[str, float]       # operator -> decibans after decay
    independent_operators: int            # operators that gave a verdict
    contradicted: bool                    # at least one counted operator signed "false"
    interval: float = 0.9
    notes: List[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {"G_dB": round(self.value, 1), "interval_dB": [round(self.low, 1), round(self.high, 1)],
                "interval": self.interval, "band": self.band, "operators": self.independent_operators,
                "contradicted": self.contradicted, "contributions_dB": {k: round(v, 1) for k, v in self.contributions.items()},
                "notes": self.notes}


def reading(
    records: Iterable[Tuple[str, object]],
    params: Mapping[str, Mapping[str, float]],
    ages: Optional[Mapping[str, float]] = None,
    half_life_seconds: Optional[float] = None,
    interval: float = 0.9,
) -> GraviteronReading:
    """records: (operator, result) pairs; params: operator -> {sensitivity, specificity} (Dawid-Skene);
    ages: operator -> seconds since its verdict was signed. Operators without params count zero."""
    verdicts = operator_verdicts(records)
    contrib: Dict[str, float] = {}
    notes: List[str] = []
    for op, v in verdicts.items():
        p = params.get(op)
        if v is None:
            notes.append(f"{op}: no verdict, counts nothing")
            continue
        if p is None:
            notes.append(f"{op}: no measured reliability, counts nothing")
            continue
        sens = min(max(p["sensitivity"], 1e-6), 1 - 1e-6)
        spec = min(max(p["specificity"], 1e-6), 1 - 1e-6)
        lr = sens / (1 - spec) if v else (1 - sens) / spec
        contrib[op] = decay(10.0 * math.log10(lr), (ages or {}).get(op, 0.0), half_life_seconds)
    g = sum(contrib.values())
    # interval: Beta posterior on "an independent check confirms", with the decayed evidence as pseudo-counts
    pos = sum(1 - 2 ** (-abs(c) / 10.0) for c in contrib.values() if c > 0)  # decibans -> pseudo-count in (0, 1)
    neg = sum(1 - 2 ** (-abs(c) / 10.0) for c in contrib.values() if c < 0)
    a, b = 1.0 + pos, 1.0 + neg
    lo_p, hi_p = beta_quantile((1 - interval) / 2, a, b), beta_quantile(1 - (1 - interval) / 2, a, b)
    spread_lo, spread_hi = _db(lo_p) - _db(a / (a + b)), _db(hi_p) - _db(a / (a + b))
    contradicted = any(verdicts.get(op) is False for op in contrib)
    if contradicted:
        notes.append("signed contradiction present: reported, never averaged away")
    words = ("contested: " + band(g)) if contradicted else band(g)
    return GraviteronReading(g, g + spread_lo, g + spread_hi, words, contrib,
                             sum(1 for op in contrib), contradicted, interval, notes)
