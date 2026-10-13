"""Properties the Graviteron v0.2 measure must have, whatever the data."""

import math

import pytest

from graviteron.evidence import (Opinion, averaging_fusion, auc, brier, cumulative_fusion, dawid_skene, discount, ece,
                                 evidence_from_accuracy, from_evidence, graviteron, trust_from_accuracy)


def test_opinion_invariants():
    o = from_evidence(3, 1)
    assert math.isclose(o.b + o.d + o.u, 1.0)
    assert math.isclose(o.expected, (3 + 1) / (3 + 1 + 2))
    with pytest.raises(ValueError):
        Opinion(0.6, 0.6, -0.2)


def test_no_evidence_means_full_uncertainty_not_a_made_up_number():
    g = graviteron([])
    assert g.u == 1.0 and g.expected == 0.5
    g = graviteron([("a", None), ("b", None)])
    assert g.u == 1.0 and g.expected == 0.5


def test_cumulative_fusion_adds_evidence():
    f = cumulative_fusion([from_evidence(2, 0), from_evidence(1, 1)])
    assert math.isclose(f.expected, from_evidence(3, 1).expected)


def test_repeating_a_source_does_not_raise_the_measure():
    one = graviteron([("a", True), ("b", True)])
    many = graviteron([("a", True)] * 50 + [("b", True)])
    assert math.isclose(one.expected, many.expected) and math.isclose(one.u, many.u)


def test_independent_support_raises_and_contradiction_lowers():
    base = graviteron([("a", True)])
    more = graviteron([("a", True), ("b", True)])
    contra = graviteron([("a", True), ("b", True), ("c", False)])
    assert more.expected > base.expected and more.u < base.u
    assert contra.expected < more.expected


def test_no_verdict_adds_no_support():
    assert math.isclose(graviteron([("a", True), ("b", None)]).expected, graviteron([("a", True)]).expected)


def test_single_operator_never_reaches_low_uncertainty():
    g = graviteron([("a", True)] * 1000)
    assert g.u >= 0.5  # one source stays one source: no aggregation laundering


def test_zero_trust_source_is_ignored():
    g = graviteron([("good", True), ("sybil", False)], reliability={"good": 1.0, "sybil": 0.0})
    assert math.isclose(g.expected, graviteron([("good", True)]).expected)


def test_discount_moves_mass_to_uncertainty():
    o = discount(from_evidence(8, 0), 0.5)
    assert math.isclose(o.b + o.d + o.u, 1.0) and o.u > from_evidence(8, 0).u


def test_evidence_weight_reproduces_accuracy_for_a_single_verdict():
    for p in (0.6, 0.75, 0.9, 0.95):
        g = graviteron([("a", True)], evidence_weight={"a": evidence_from_accuracy(p)})
        assert math.isclose(g.expected, p, rel_tol=1e-9)
    assert evidence_from_accuracy(0.5) == 0.0 and trust_from_accuracy(0.4) == 0.0


def test_averaging_fusion_of_identical_opinions_is_identity():
    o = from_evidence(2, 1)
    assert math.isclose(averaging_fusion([o, o, o]).expected, o.expected)


def test_dawid_skene_finds_the_unreliable_operator():
    verdicts = {}
    for i in range(200):
        truth = i % 2 == 0
        verdicts[f"c{i}"] = {"good1": truth, "good2": truth if i % 10 else (not truth), "bad": not truth if i % 3 else truth}
    _, params, _ = dawid_skene(verdicts)
    assert params["good1"]["accuracy"] > 0.9 and params["bad"]["accuracy"] < 0.5


def test_scores():
    truth = [True, False, True, False]
    assert brier([1, 0, 1, 0], truth) == 0.0
    assert auc([0.9, 0.1, 0.8, 0.2], truth) == 1.0
    assert ece([1.0, 0.0, 1.0, 0.0], truth) == 0.0
