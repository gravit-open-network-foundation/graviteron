import pytest
from fastapi.testclient import TestClient
from graviteron.api.fastapi_app import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["service"] == "Graviteron API"
    assert "version" in json_data

def test_read_health():
    response = client.get("/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "healthy"
    assert "uptime_seconds" in json_data
    assert "requests_processed" in json_data

def test_compute_endpoint():
    payload = {
        "tensor": {
            "consistency": 0.95,
            "stability": 0.88,
            "adversarial_robustness": 0.92,
            "factual_grounding": 0.97,
            "reasoning_soundness": 0.90,
            "recovery_score": 0.85
        },
        "input_data": "Decide on consensus algorithm validation.",
        "context": {"agent_id": "test-agent"}
    }
    response = client.post("/compute", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "graviteron_score" in data
    assert "omega_trace_id" in data
    assert data["tensor"]["consistency"] == 0.95

    # Retrieve the trace we just computed
    trace_id = data["omega_trace_id"]
    trace_response = client.get(f"/trace/{trace_id}")
    assert trace_response.status_code == 200
    trace_data = trace_response.json()
    assert trace_data["trace_id"] == trace_id
    assert trace_data["metadata"]["agent_id"] == "test-agent"

def test_get_trace_not_found():
    response = client.get("/trace/non-existent-uuid")
    assert response.status_code == 404

def test_verify_endpoint():
    payload = {
        "output": "Standardized compute units of verifiable trust.",
        "model": "gpt-4",
        "context": {"temperature": 0.5}
    }
    response = client.post("/verify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "graviteron" in data
    assert "omega_trace_id" in data
    assert data["model"] == "gpt-4"
    assert data["status"] in ["APPROVED", "RISK_DETECTED"]
