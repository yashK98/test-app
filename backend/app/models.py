from typing import Optional
from pydantic import BaseModel


class ContainerSpec(BaseModel):
    name: str
    image: str
    image_tag: str
    cpu_request: str
    cpu_limit: str
    memory_request: str
    memory_limit: str


class DeploymentSpec(BaseModel):
    app: str
    environment: str
    replicas: int
    containers: list[ContainerSpec]
    env_vars: dict[str, str]
    config_map_keys: list[str]
    secret_keys: list[str]
    service_port: int
    last_modified: str
    modified_by: str


class DriftItem(BaseModel):
    field: str
    category: str  # image | replicas | resources | env_vars | config | secret | service
    dev_value: Optional[str] = None
    baseline_value: Optional[str] = None
    target_value: Optional[str] = None
    severity: str  # low | medium | high | critical
    description: str


class DriftReport(BaseModel):
    app: str
    baseline_env: str
    target_env: str
    parity_score: float
    drift_items: list[DriftItem]
    root_cause: Optional[str] = None
    root_cause_confidence: Optional[float] = None
    summary: Optional[str] = None
    scanned_at: str


class RemediationSuggestion(BaseModel):
    app: str
    target_env: str
    action: str
    description: str
    success_likelihood: float


class RemediationResult(BaseModel):
    app: str
    target_env: str
    action: str
    status: str
    message: str
