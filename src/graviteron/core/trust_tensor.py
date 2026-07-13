import numpy as np
from typing import Dict, Any, List

class TrustTensor:
    """6-dimensional Trust Tensor for Graviteron trust computation"""

    def __init__(
        self,
        consistency: float,
        stability: float,
        adversarial_robustness: float,
        factual_grounding: float,
        reasoning_soundness: float,
        recovery_score: float
    ):
        self.consistency = float(consistency)
        self.stability = float(stability)
        self.adversarial_robustness = float(adversarial_robustness)
        self.factual_grounding = float(factual_grounding)
        self.reasoning_soundness = float(reasoning_soundness)
        self.recovery_score = float(recovery_score)

    def to_array(self) -> np.ndarray:
        """Convert components to a numpy array for mathematical vector operations"""
        return np.array([
            self.consistency,
            self.stability,
            self.adversarial_robustness,
            self.factual_grounding,
            self.reasoning_soundness,
            self.recovery_score
        ], dtype=float)

    def normalize(self) -> 'TrustTensor':
        """Normalize all components strictly to [0.0, 1.0] bound limits"""
        return TrustTensor(
            consistency=max(0.0, min(1.0, self.consistency)),
            stability=max(0.0, min(1.0, self.stability)),
            adversarial_robustness=max(0.0, min(1.0, self.adversarial_robustness)),
            factual_grounding=max(0.0, min(1.0, self.factual_grounding)),
            reasoning_soundness=max(0.0, min(1.0, self.reasoning_soundness)),
            recovery_score=max(0.0, min(1.0, self.recovery_score))
        )

    def to_dict(self) -> Dict[str, float]:
        """Convert the TrustTensor instance to a dictionary representation"""
        return {
            "consistency": self.consistency,
            "stability": self.stability,
            "adversarial_robustness": self.adversarial_robustness,
            "factual_grounding": self.factual_grounding,
            "reasoning_soundness": self.reasoning_soundness,
            "recovery_score": self.recovery_score
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrustTensor':
        """Instantiate a TrustTensor from a dictionary representation"""
        return cls(
            consistency=data.get("consistency", 0.0),
            stability=data.get("stability", 0.0),
            adversarial_robustness=data.get("adversarial_robustness", 0.0),
            factual_grounding=data.get("factual_grounding", 0.0),
            reasoning_soundness=data.get("reasoning_soundness", 0.0),
            recovery_score=data.get("recovery_score", 0.0)
        )

    def __repr__(self) -> str:
        return (
            f"TrustTensor(consistency={self.consistency:.4f}, stability={self.stability:.4f}, "
            f"adversarial_robustness={self.adversarial_robustness:.4f}, factual_grounding={self.factual_grounding:.4f}, "
            f"reasoning_soundness={self.reasoning_soundness:.4f}, recovery_score={self.recovery_score:.4f})"
        )
