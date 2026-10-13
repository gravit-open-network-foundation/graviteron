# Graviteron Integration Guide

## Quick Start

### 1. HTTP Endpoint Query

Send a verification payload to the Graviteron API:

```python
import requests

response = requests.post("http://localhost:8000/compute", json={
    "tensor": {
        "consistency": 0.95,
        "stability": 0.88,
        "adversarial_robustness": 0.92,
        "factual_grounding": 0.97,
        "reasoning_soundness": 0.90,
        "recovery_score": 0.85
    },
    "context": {
        "model": "claude-3-5-sonnet",
        "agent_id": "nexus-agent-9"
    },
    "input_data": "Decide on database migration strategy."
})

data = response.json()
print("Graviteron Score:", data["graviteron_score"])
print("Omega Trace ID:", data["omega_trace_id"])
```

### 2. Core Integration Hooks

- **Pre-Execution Guard**: Query Graviteron score prior to performing irreversible actions (e.g., executing blockchain transactions or filesystem changes). Block execution if $G < \text{threshold}$.
- **Immutable Audit Logging**: Store `omega_trace_id` returned from validation inside database execution headers.
- **Dynamic Routing**: Route highly complex queries to agents with verified historical reputation and higher Graviteron validation scores.

## Supported Protocols & Formats

- **REST API**: HTTP JSON payload with standard JSON Schema.
- **On-Chain Attestation**: payload format to be defined in the GEVP agentic-finance profile (the earlier name "ERC-8004-GT" is retired).
- **Redis Cache**: Instant key lookup of computed $\Omega$ traces.

## Best Practices

1. **Threshold Settings**: 
   - Financial operations: Minimum $G \ge 0.95$.
   - General informational generation: Minimum $G \ge 0.60$.
2. **Context Passing**: Include as much operational metadata (e.g., system prompts, parameters) as possible in the request context for downstream verification.
