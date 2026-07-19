from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RepositoryIn(BaseModel):
    name: str
    ado_project: str = ""
    ado_repo: str = ""
    chart_path: str = "charts"
    values_dir: str = "charts/values"
    default_namespace: str = ""


class RepositoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    ado_project: str
    ado_repo: str
    chart_path: str
    values_dir: str
    default_namespace: str
    created_at: datetime


class AuthResult(BaseModel):
    ok: bool
    message: str


class ResourceBundle(BaseModel):
    namespace: str
    counts: dict[str, int]
    resources: dict[str, list[dict]]
