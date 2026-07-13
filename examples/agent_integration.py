import os
import json
import urllib.request
import urllib.error
from graviteron import GraviteronEngine, TrustTensor

def run_local_demo():
    print("--- 1. Local Graviteron Scoring Engine Demo ---")
    
    # Initialize engine
    engine = GraviteronEngine()

    # Define a 6D Trust Tensor
    tensor = TrustTensor(
        consistency=0.95,
        stability=0.88,
        adversarial_robustness=0.92,
        factual_grounding=0.97,
        reasoning_soundness=0.90,
        recovery_score=0.85
    )

    # Compute Graviteron score and write immutable trajectory
    score, trace = engine.compute_with_trace(
        tensor=tensor,
        input_data="Verify model decision validation process.",
        context={
            "agent_id": "core-executor-9",
            "model_family": "grok-4"
        }
    )

    print(f"Computed local score : {score:.4f} Graviteron")
    print(f"Generated Omega Trace: {trace.trace_id}")
    print(f"Input verification Hash: {trace.input_hash}")
    print(f"Serialized output: {json.dumps(trace.to_dict(), indent=2)}\n")


def run_api_client_demo():
    print("--- 2. FastAPI Verification API Demo ---")
    api_url = os.environ.get("GRAVITERON_API_URL", "http://localhost:8000")
    
    # Verification query payload
    payload = {
        "output": "The Graviteron measures the epistemic weight of truth.",
        "model": "claude-3-5-sonnet",
        "context": {"importance": "critical"}
    }
    
    try:
        req = urllib.request.Request(
            f"{api_url}/verify",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        print(f"Sending verify request to {api_url}/verify...")
        with urllib.request.urlopen(req, timeout=3.0) as response:
            res_body = json.loads(response.read().decode("utf-8"))
            print("API Response:")
            print(json.dumps(res_body, indent=2))
    except urllib.error.URLError as e:
        print(f"Could not connect to API server at {api_url}: {e}.")
        print("Note: Start the FastAPI application (e.g. `uvicorn graviteron.api.fastapi_app:app`) to test this endpoint.")


if __name__ == "__main__":
    run_local_demo()
    run_api_client_demo()
