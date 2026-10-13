"""Binomial opinions of Subjective Logic (Josang, "Subjective Logic", Springer 2016).

An opinion about a binary claim is (b, d, u, a): belief, disbelief, uncertainty
(b + d + u = 1) and base rate a. It is equivalent to evidence counts r (for) and
s (against) with a non-informative prior weight W:

    b = r / (r + s + W),  d = s / (r + s + W),  u = W / (r + s + W)

Its expected probability is P = b + a * u. With no evidence, u = 1 and P = a:
the opinion says "I do not know" instead of inventing a number.

Fusion is done on evidence, which makes the operators exact and easy to check:
  * cumulative fusion (independent sources): evidence adds up;
  * averaging fusion (dependent sources, e.g. keys of one operator): evidence is
    averaged, so a source cannot outvote itself by repeating itself;
  * trust discounting: an opinion from a source we trust with probability t keeps
    only the share t of its belief and disbelief; the rest becomes uncertainty.
"""

from dataclasses import dataclass
from typing import Iterable

PRIOR_WEIGHT = 2.0  # W: the standard non-informative prior weight for binomial opinions


@dataclass(frozen=True)
class Opinion:
    b: float
    d: float
    u: float
    a: float = 0.5

    def __post_init__(self) -> None:
        for name in ("b", "d", "u", "a"):
            v = getattr(self, name)
            if not 0.0 <= v <= 1.0:
                raise ValueError(f"{name} must lie in [0, 1], got {v}")
        if abs(self.b + self.d + self.u - 1.0) > 1e-9:
            raise ValueError("b + d + u must equal 1")

    @property
    def expected(self) -> float:
        """Projected probability P = b + a * u."""
        return self.b + self.a * self.u

    def evidence(self, w: float = PRIOR_WEIGHT) -> tuple:
        """(r, s) evidence equivalent to this opinion. Infinite if u == 0 (dogmatic opinion)."""
        if self.u == 0.0:
            raise ValueError("a dogmatic opinion (u = 0) has unbounded evidence")
        return w * self.b / self.u, w * self.d / self.u

    def as_dict(self) -> dict:
        return {"belief": self.b, "disbelief": self.d, "uncertainty": self.u, "base_rate": self.a, "expected": self.expected}


def from_evidence(r: float, s: float, a: float = 0.5, w: float = PRIOR_WEIGHT) -> Opinion:
    if r < 0 or s < 0:
        raise ValueError("evidence must be non-negative")
    n = r + s + w
    return Opinion(r / n, s / n, w / n, a)


VACUOUS = Opinion(0.0, 0.0, 1.0, 0.5)


def cumulative_fusion(opinions: Iterable[Opinion], a: float = 0.5, w: float = PRIOR_WEIGHT) -> Opinion:
    """Fuse opinions of independent sources: their evidence adds up."""
    r = s = 0.0
    for o in opinions:
        ri, si = o.evidence(w)
        r, s = r + ri, s + si
    return from_evidence(r, s, a, w)


def averaging_fusion(opinions: Iterable[Opinion], a: float = 0.5, w: float = PRIOR_WEIGHT) -> Opinion:
    """Fuse opinions of dependent sources (one operator): their evidence is averaged."""
    ev = [o.evidence(w) for o in opinions]
    if not ev:
        return Opinion(0.0, 0.0, 1.0, a)
    return from_evidence(sum(r for r, _ in ev) / len(ev), sum(s for _, s in ev) / len(ev), a, w)


def discount(o: Opinion, trust: float) -> Opinion:
    """Probability-sensitive trust discounting: keep the share `trust` of belief and disbelief."""
    if not 0.0 <= trust <= 1.0:
        raise ValueError("trust must lie in [0, 1]")
    b, d = trust * o.b, trust * o.d
    return Opinion(b, d, 1.0 - b - d, o.a)
