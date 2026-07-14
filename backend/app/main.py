from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import environments, drift, dashboard, remediation
from app import state

app = FastAPI(
    title="K8s Environment Drift Detection & Auto-Remediation API",
    description="Detects configuration drift across Dev/Prod/DR Kubernetes clusters, "
                 "predicts root cause with ML, and recommends remediation.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Seed synthetic K8s cluster state and train the ML root-cause model."""
    state.initialize()


app.include_router(environments.router, prefix="/api/environments", tags=["environments"])
app.include_router(drift.router, prefix="/api/drift", tags=["drift"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(remediation.router, prefix="/api/remediation", tags=["remediation"])


@app.get("/api/health")
def health():
    return {"status": "ok"}
