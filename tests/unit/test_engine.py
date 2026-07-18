import numpy as np
import pytest

from graviteron.core.graviteron_engine import GraviteronEngine, VerificationResult
from graviteron.core.omega_trace import OmegaTrace
from graviteron.core.trust_tensor import TrustTensor
from graviteron.validators.continuum_validator import ContinuumValidator
from graviteron.validators.gqrvp import GqrvpValidator


def test_trust_tensor_creation():
    tensor = TrustTensor(
        consistency=0.9,
        stability=0.8,
        adversarial_robustness=0.7,
        factual_grounding=0.6,
        reasoning_soundness=0.5,
        recovery_score=0.4,
    )
    assert tensor.consistency == 0.9
    assert tensor.stability == 0.8
    assert tensor.adversarial_robustness == 0.7
    assert tensor.factual_grounding == 0.6
    assert tensor.reasoning_soundness == 0.5
    assert tensor.recovery_score == 0.4

    arr = tensor.to_array()
    assert np.array_equal(arr, np.array([0.9, 0.8, 0.7, 0.6, 0.5, 0.4]))


def test_trust_tensor_normalization():
    tensor = TrustTensor(
        consistency=1.5,
        stability=-0.2,
        adversarial_robustness=0.7,
        factual_grounding=1.0,
        reasoning_soundness=0.0,
        recovery_score=0.5,
    )
    norm = tensor.normalize()
    assert norm.consistency == 1.0
    assert norm.stability == 0.0
    assert norm.adversarial_robustness == 0.7
    assert norm.factual_grounding == 1.0
    assert norm.reasoning_soundness == 0.0
    assert norm.recovery_score == 0.5


def test_trust_tensor_dict_conversion():
    data = {
        "consistency": 0.9,
        "stability": 0.8,
        "adversarial_robustness": 0.7,
        "factual_grounding": 0.6,
        "reasoning_soundness": 0.5,
        "recovery_score": 0.4,
    }
    tensor = TrustTensor.from_dict(data)
    assert tensor.consistency == 0.9
    assert tensor.to_dict() == data


def test_engine_basic_computation():
    engine = GraviteronEngine(adversarial_threshold=0.7)

    # Adversarial robustness is 0.8 (above 0.7), so multiplier is 1.0
    # Average of [0.8]*6 = 0.8
    tensor = TrustTensor(0.8, 0.8, 0.8, 0.8, 0.8, 0.8)
    score = engine.compute(tensor)
    assert pytest.approx(score) == 0.8


def test_engine_adversarial_scaling():
    engine = GraviteronEngine(adversarial_threshold=0.8)

    # Adversarial robustness is 0.4 (below 0.8), so multiplier is 0.4 / 0.8 = 0.5
    # Average of five 0.88 components and one 0.4 component: (0.88*5 + 0.4)/6 = 0.8
    # Multiplied by 0.5 = 0.4
    tensor = TrustTensor(0.88, 0.88, 0.4, 0.88, 0.88, 0.88)
    score = engine.compute(tensor)
    assert pytest.approx(score) == 0.4


def test_theta_critical_escalation_for_low_confidence():
    engine = GraviteronEngine(adversarial_threshold=0.7)
    tensor = TrustTensor(0.4, 0.4, 0.4, 0.4, 0.4, 0.4)

    result = engine.evaluate_verification(tensor)

    assert isinstance(result, VerificationResult)
    assert result.theta_critical == 0.731
    assert result.requires_continuum is True
    assert result.verdict == "ESCALATE_TO_CONTINUUM"
    assert result.confidence < result.theta_critical


def test_theta_critical_passes_for_strong_confidence():
    engine = GraviteronEngine(adversarial_threshold=0.7)
    tensor = TrustTensor(0.9, 0.9, 0.9, 0.9, 0.9, 0.9)

    result = engine.evaluate_verification(tensor)

    assert result.requires_continuum is False
    assert result.verdict == "APPROVED"
    assert result.confidence >= result.theta_critical


def test_compute_with_trace_includes_theta_critical_metadata():
    engine = GraviteronEngine(adversarial_threshold=0.7)
    tensor = TrustTensor(0.4, 0.4, 0.4, 0.4, 0.4, 0.4)

    score, trace = engine.compute_with_trace(tensor=tensor, input_data="low-confidence")

    assert score < 0.731
    assert trace.metadata["theta_critical"] == 0.731
    assert trace.metadata["requires_continuum"] is True
    assert trace.metadata["verification_verdict"] == "ESCALATE_TO_CONTINUUM"


def test_omega_trace_serialization():
    tensor = TrustTensor(0.9, 0.9, 0.9, 0.9, 0.9, 0.9)
    trace = OmegaTrace(score=0.9, tensor=tensor, input_hash="dummy_hash", metadata={"test": True})

    assert trace.verify() is True

    serialized = trace.to_dict()
    assert serialized["score"] == 0.9
    assert serialized["input_hash"] == "dummy_hash"
    assert serialized["metadata"]["test"] is True
    assert serialized["tensor"]["consistency"] == 0.9

    deserialized = OmegaTrace.from_dict(serialized)
    assert deserialized.score == 0.9
    assert deserialized.tensor.consistency == 0.9
    assert deserialized.verify() is True


def test_gqrvp_validator():
    validator = GqrvpValidator()
    tensor = TrustTensor(0.9, 0.8, 0.7, 0.9, 0.9, 0.9)

    assessment = validator.assess_quantum_safety(tensor)
    assert assessment["quantum_resistant_status"] == "SECURE"
    assert assessment["verified"] is True

    # Low entropy verification test
    low_tensor = TrustTensor(0.2, 0.2, 0.2, 0.2, 0.2, 0.2)
    low_assessment = validator.assess_quantum_safety(low_tensor)
    assert low_assessment["quantum_resistant_status"] == "WARNING_LOW_ENTROPY"
    assert low_assessment["verified"] is False


def test_continuum_validator_mock():
    client = ContinuumValidator()
    tensor = TrustTensor(0.9, 0.8, 0.7, 0.9, 0.9, 0.9)
    trace = OmegaTrace(score=0.85, tensor=tensor, input_hash="h123")

    res = client.validate_trace(trace)
    assert res["verdict"] in ["APPROVED", "WARN_UNSTABLE"]
    assert "consensus_score" in res
    assert res["signature"].startswith("gqrvp_")
