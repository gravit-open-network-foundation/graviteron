# Theta-Critical Verification Notes

## Summary

Graviteron now supports an explicit θ-critical verification threshold for epistemic escalation.

- Threshold: 0.731
- Behavior: scores below the threshold trigger continuum escalation
- Result type: VerificationResult
- API exposure: compute endpoint now includes verification metadata

## How to use

```python
from graviteron import GraviteronEngine, TrustTensor

engine = GraviteronEngine()
tensor = TrustTensor(0.4, 0.4, 0.4, 0.4, 0.4, 0.4)
result = engine.evaluate_verification(tensor)
print(result)
```
