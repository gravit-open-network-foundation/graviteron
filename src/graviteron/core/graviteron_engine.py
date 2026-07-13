import hashlib
import json
from typing import Any, Dict, Optional, Tuple

import numpy as np

from .omega_trace import OmegaTrace
from .redis_store import RedisTraceStore
from .trust_tensor import TrustTensor


class GraviteronEngine:
    """Core mathematical engine that computes Graviteron scores from Trust Tensors"""

    def __init__(
        self,
        weights: Optional[np.ndarray] = None,
        adversarial_threshold: float = 0.7,
        redis_url: Optional[str] = None,
        store: Optional[RedisTraceStore] = None,
    ):
        if weights is not None:
            self.weights = np.array(weights, dtype=float)
            # Normalize weights to sum to 1.0 if not already
            total = float(np.sum(self.weights))
            if total > 0:
                self.weights = self.weights / total
        else:
            self.weights = np.ones(6, dtype=float) / 6.0

        self.adversarial_threshold = adversarial_threshold
        self.store = store or RedisTraceStore(redis_url=redis_url)

    def compute(self, tensor: TrustTensor) -> float:
        """Compute the scalar Graviteron score from a given Trust Tensor"""
        normalized_tensor = tensor.normalize()
        arr = normalized_tensor.to_array()

        # Weighted dot product
        raw_score = float(np.dot(arr, self.weights))

        # Apply Adversarial Stability Multiplier (A)
        # If R is below the threshold, scale down the trust score proportionally
        r = normalized_tensor.adversarial_robustness
        if r >= self.adversarial_threshold:
            multiplier = 1.0
        else:
            # Avoid division by zero
            if self.adversarial_threshold > 0:
                multiplier = r / self.adversarial_threshold
            else:
                multiplier = 1.0

        final_score = raw_score * multiplier
        return max(0.0, min(1.0, final_score))

    def compute_with_trace(
        self, tensor: TrustTensor, input_data: Any, context: Optional[Dict[str, Any]] = None
    ) -> Tuple[float, OmegaTrace]:
        """Compute the Graviteron score and write the resulting OmegaTrace to the store"""
        score = self.compute(tensor)
        input_hash = self._hash_input(input_data)

        trace = OmegaTrace(score=score, tensor=tensor, input_hash=input_hash, metadata=context or {})

        # Save trace to store
        self.store.put(trace)

        return score, trace

    def get_trace(self, trace_id: str) -> Optional[OmegaTrace]:
        """Retrieve a stored OmegaTrace record by its trace_id"""
        return self.store.get(trace_id)

    def _hash_input(self, input_data: Any) -> str:
        """Generate deterministic SHA-256 hash representation of input data"""
        if isinstance(input_data, str):
            data_bytes = input_data.encode("utf-8")
        else:
            try:
                # Use sort_keys to ensure deterministic dictionary hashing
                data_str = json.dumps(input_data, sort_keys=True)
                data_bytes = data_str.encode("utf-8")
            except Exception:
                data_bytes = str(input_data).encode("utf-8")

        return hashlib.sha256(data_bytes).hexdigest()
