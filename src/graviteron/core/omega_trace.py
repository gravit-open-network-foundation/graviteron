import time
import uuid
from typing import Any, Dict, Optional

from .trust_tensor import TrustTensor


class OmegaTrace:
    """Immutable trace representation of a Graviteron verification event"""

    def __init__(
        self,
        score: float,
        tensor: TrustTensor,
        input_hash: str,
        trace_id: Optional[str] = None,
        timestamp: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.trace_id = trace_id or str(uuid.uuid4())
        self.timestamp = timestamp or time.time()
        self.score = float(score)
        self.tensor = tensor
        self.input_hash = input_hash
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert the OmegaTrace instance to a dictionary representation"""
        return {
            "trace_id": self.trace_id,
            "timestamp": self.timestamp,
            "score": self.score,
            "tensor": self.tensor.to_dict() if self.tensor else None,
            "input_hash": self.input_hash,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OmegaTrace":
        """Instantiate an OmegaTrace from a dictionary representation"""
        tensor_data = data.get("tensor")
        tensor = TrustTensor.from_dict(tensor_data) if tensor_data else None

        return cls(
            score=data.get("score", 0.0),
            tensor=tensor,
            input_hash=data.get("input_hash", ""),
            trace_id=data.get("trace_id"),
            timestamp=data.get("timestamp"),
            metadata=data.get("metadata"),
        )

    def verify(self) -> bool:
        """Verify structural validity and mathematical alignment of the trace"""
        if not self.trace_id:
            return False
        if not (0.0 <= self.score <= 1.0):
            return False
        if not self.input_hash:
            return False
        if not self.tensor:
            return False

        # Verify the scores in the tensor are in bounds
        t = self.tensor
        for val in [
            t.consistency,
            t.stability,
            t.adversarial_robustness,
            t.factual_grounding,
            t.reasoning_soundness,
            t.recovery_score,
        ]:
            if not (0.0 <= val <= 1.0):
                return False

        return True

    def __repr__(self) -> str:
        return f"OmegaTrace(trace_id={self.trace_id}, score={self.score:.4f}, input_hash={self.input_hash})"
