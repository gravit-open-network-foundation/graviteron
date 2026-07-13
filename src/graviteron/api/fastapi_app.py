import logging
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ..core.graviteron_engine import GraviteronEngine
from ..core.redis_store import RedisTraceStore
from ..core.trust_tensor import TrustTensor

# Setup logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("graviteron.api")

# Fetch configuration from environments
REDIS_URL = os.environ.get("REDIS_URL", None)
ADVERSARIAL_THRESHOLD = float(os.environ.get("ADVERSARIAL_THRESHOLD", "0.7"))

# Initialize state store and engine
trace_store = RedisTraceStore(redis_url=REDIS_URL)
engine = GraviteronEngine(adversarial_threshold=ADVERSARIAL_THRESHOLD, store=trace_store)

app = FastAPI(
    title="Graviteron API",
    description="The Fundamental Unit of Verifiable Trust — Epistemic Trust Validation Service",
    version="0.1.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Statistics tracker
start_time = datetime.now(timezone.utc)
requests_processed = 0


# --- Middleware for metrics and request logging ---
@app.middleware("http")
async def log_and_time_requests(request: Request, call_next):
    global requests_processed
    requests_processed += 1

    request_id = str(uuid.uuid4())
    start_ts = time.time()

    logger.info(f"[{request_id}] Incoming request: {request.method} {request.url.path}")

    response = await call_next(request)

    duration = (time.time() - start_ts) * 1000.0
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Processing-Time-Ms"] = f"{duration:.2f}"

    logger.info(f"[{request_id}] Completed in {duration:.2f}ms with status {response.status_code}")
    return response


# --- Pydantic Data Models ---


class TrustTensorInput(BaseModel):
    consistency: float = Field(..., ge=0.0, le=1.0, description="Consistency across contexts")
    stability: float = Field(..., ge=0.0, le=1.0, description="Temporal stability")
    adversarial_robustness: float = Field(..., ge=0.0, le=1.0, description="Resilience to attacks")
    factual_grounding: float = Field(..., ge=0.0, le=1.0, description="Factual accuracy")
    reasoning_soundness: float = Field(..., ge=0.0, le=1.0, description="Logical coherence")
    recovery_score: float = Field(..., ge=0.0, le=1.0, description="Recovery potential")


class ComputeRequest(BaseModel):
    tensor: TrustTensorInput
    input_data: Any = Field(default="", description="The text, prompt, or structure to hash and verify")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadata and parameters")


class ComputeResponse(BaseModel):
    graviteron_score: float
    omega_trace_id: str
    timestamp: float
    input_hash: str
    tensor: Dict[str, float]
    processing_time_ms: float


class TraceResponse(BaseModel):
    trace_id: str
    timestamp: float
    score: float
    tensor: Optional[Dict[str, float]]
    input_hash: str
    metadata: Dict[str, Any]


class VerifyRequest(BaseModel):
    output: str = Field(..., description="Target string output to check")
    model: str = Field(default="unknown", description="Name of the model generating output")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Context variables")


# --- Routes ---


@app.get("/")
async def root():
    return {
        "service": "Graviteron API",
        "description": "The Fundamental Unit of Verifiable Trust",
        "version": "0.1.0",
        "status": "operational",
        "docs_url": "/docs",
    }


@app.get("/health")
async def health():
    uptime = (datetime.now(timezone.utc) - start_time).total_seconds()
    return {
        "status": "healthy",
        "uptime_seconds": uptime,
        "requests_processed": requests_processed,
        "engine_ready": True,
        "store": {
            "fallback_active": trace_store.fallback_mode,
            "cached_traces_count": trace_store.count(),
        },
    }


@app.post("/compute", response_model=ComputeResponse, status_code=status.HTTP_201_CREATED)
async def compute_score(payload: ComputeRequest):
    start_ts = time.time()
    try:
        tensor = TrustTensor(
            consistency=payload.tensor.consistency,
            stability=payload.tensor.stability,
            adversarial_robustness=payload.tensor.adversarial_robustness,
            factual_grounding=payload.tensor.factual_grounding,
            reasoning_soundness=payload.tensor.reasoning_soundness,
            recovery_score=payload.tensor.recovery_score,
        )

        score, trace = engine.compute_with_trace(tensor=tensor, input_data=payload.input_data, context=payload.context)

        duration_ms = (time.time() - start_ts) * 1000.0

        return ComputeResponse(
            graviteron_score=score,
            omega_trace_id=trace.trace_id,
            timestamp=trace.timestamp,
            input_hash=trace.input_hash,
            tensor=trace.tensor.to_dict(),
            processing_time_ms=duration_ms,
        )
    except Exception as e:
        logger.error(f"Computation endpoint failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Computation failed: {str(e)}",
        )


@app.get("/trace/{trace_id}", response_model=TraceResponse)
async def get_trace(trace_id: str):
    trace = engine.get_trace(trace_id)
    if not trace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trace with ID '{trace_id}' not found.")

    return TraceResponse(
        trace_id=trace.trace_id,
        timestamp=trace.timestamp,
        score=trace.score,
        tensor=trace.tensor.to_dict() if trace.tensor else None,
        input_hash=trace.input_hash,
        metadata=trace.metadata,
    )


@app.post("/verify")
async def verify_output(payload: VerifyRequest):
    """
    High-level verification endpoint. Simplifies scoring for external agent integrations
    by returning a default structured trust assessment.
    """
    try:
        # Generate dynamic/simulated metrics based on complexity of text for demonstration
        words_count = len(payload.output.split())

        # Simple heuristic to derive tensor components based on output features
        consistency = 0.90 if words_count > 5 else 0.75
        stability = 0.85
        adversarial_robustness = 0.80
        factual_grounding = 0.92 if "trust" in payload.output.lower() else 0.80
        reasoning_soundness = 0.88
        recovery_score = 0.85

        tensor = TrustTensor(
            consistency=consistency,
            stability=stability,
            adversarial_robustness=adversarial_robustness,
            factual_grounding=factual_grounding,
            reasoning_soundness=reasoning_soundness,
            recovery_score=recovery_score,
        )

        score, trace = engine.compute_with_trace(
            tensor=tensor,
            input_data=payload.output,
            context={"model": payload.model, "interface": "verify_endpoint", **payload.context},
        )

        return {
            "graviteron": float(round(score, 4)),
            "omega_trace_id": trace.trace_id,
            "model": payload.model,
            "timestamp": datetime.fromtimestamp(trace.timestamp).isoformat(),
            "status": "APPROVED" if score >= 0.8 else "RISK_DETECTED",
        }
    except Exception as e:
        logger.error(f"Verification endpoint failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}",
        )
