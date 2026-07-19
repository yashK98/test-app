from fastapi import APIRouter, HTTPException, Query

from .. import schemas
from ..services import kube

router = APIRouter(prefix="/api/cluster", tags=["cluster"])


@router.post("/auth", response_model=schemas.AuthResult)
def authenticate():
    """Run the configured skectl command to obtain/refresh cluster credentials."""
    try:
        ok, message, _ = kube.authenticate()
        return schemas.AuthResult(ok=ok, message=message)
    except kube.KubeError as e:
        raise HTTPException(502, str(e))


@router.get("/{namespace}/resources", response_model=schemas.ResourceBundle)
def fetch_all(namespace: str,
              reveal_secrets: bool = Query(False, description="Include secret values")):
    """Fetch configmaps, deployments, secrets, services and ingresses at once."""
    try:
        resources = kube.fetch_all(namespace, reveal_secrets)
    except kube.KubeError as e:
        raise HTTPException(502, str(e))
    counts = {k: len(v) for k, v in resources.items()}
    return schemas.ResourceBundle(namespace=namespace, counts=counts, resources=resources)


@router.get("/{namespace}/resource/{kind}")
def fetch_one(namespace: str, kind: str,
              reveal_secrets: bool = Query(False, description="Include secret values")):
    """Fetch a single kind: configmap | deployment | secret | service | ingress."""
    try:
        items = kube.fetch(kind, namespace, reveal_secrets)
    except kube.KubeError as e:
        # unsupported kind is a client error; everything else is upstream (502)
        status = 400 if str(e).startswith("Unsupported kind") else 502
        raise HTTPException(status, str(e))
    return {"namespace": namespace, "kind": kind, "count": len(items), "items": items}
