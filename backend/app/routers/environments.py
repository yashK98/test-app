from fastapi import APIRouter, HTTPException

from app import state
from app.models import DeploymentSpec

router = APIRouter()


@router.get("/apps")
def list_apps():
    return sorted(state.cluster_state.keys())


@router.get("/{app}", response_model=dict[str, DeploymentSpec])
def get_app_environments(app: str):
    envs = state.cluster_state.get(app)
    if not envs:
        raise HTTPException(status_code=404, detail="App not found")
    return envs
