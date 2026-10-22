import math

from graviteron.evidence.unit import band, beta_cdf, beta_quantile, reading

P = {"a": {"sensitivity": 0.9, "specificity": 0.9}, "b": {"sensitivity": 0.9, "specificity": 0.9},
     "c": {"sensitivity": 0.8, "specificity": 0.95}}
ONE = 10 * math.log10(0.9 / 0.1)  # one verdict of a 90/90 operator, about 9.5 dB


def test_zero_without_evidence():
    r = reading([], P)
    assert r.value == 0 and r.band == "inconclusive" and r.independent_operators == 0


def test_additive_over_independent_operators():
    assert math.isclose(reading([("a", True)], P).value, ONE)
    assert math.isclose(reading([("a", True), ("b", True)], P).value, 2 * ONE)


def test_keys_of_one_operator_count_once():
    many = [("a", True)] * 50
    assert math.isclose(reading(many, P).value, ONE)


def test_contradiction_is_negative_and_flagged():
    r = reading([("a", True), ("b", True), ("c", False)], P)
    assert r.contradicted and r.contributions["c"] < 0
    assert r.band.startswith("contested: ")  # never shown as plain support
    assert r.value < reading([("a", True), ("b", True)], P).value


def test_decay_with_half_life_and_renewal():
    day = 86400.0
    fresh = reading([("a", True)], P, ages={"a": 0}, half_life_seconds=30 * day).value
    old = reading([("a", True)], P, ages={"a": 30 * day}, half_life_seconds=30 * day).value
    assert math.isclose(old, fresh / 2)


def test_no_verdict_and_unknown_operator_count_nothing():
    r = reading([("a", None), ("ghost", True)], P)
    assert r.value == 0 and len(r.notes) == 2


def test_interval_contains_value_and_narrows_with_more_operators():
    r1 = reading([("a", True)], P)
    r3 = reading([("a", True), ("b", True), ("c", True)], P)
    assert r1.low <= r1.value <= r1.high
    assert (r3.high - r3.low) < (r1.high - r1.low)


def test_bands_follow_jeffreys():
    assert band(3) == "inconclusive"
    assert band(7) == "substantial support" and band(-7) == "substantial contradiction"
    assert band(12) == "strong support" and band(17) == "very strong support" and band(25) == "decisive support"


def test_beta_quantile_inverts_cdf():
    for a, b in [(1, 1), (2, 5), (5.5, 1.3)]:
        for q in (0.05, 0.5, 0.95):
            assert abs(beta_cdf(beta_quantile(q, a, b), a, b) - q) < 1e-6
    assert abs(beta_quantile(0.5, 1, 1) - 0.5) < 1e-6
