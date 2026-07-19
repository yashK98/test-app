# Drift Detector — Backend

FastAPI backend (Python 3.10+). Phase 1: repository CRUD + reading namespace
resources from the cluster via your existing `skectl` / `kubectl` binaries.

## Run

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # Windows: copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Interactive docs at http://localhost:8000/docs. Uses a local SQLite file by
default — no database server required.

## Endpoints

**Repositories**

| Method | Path                      | Purpose            |
|--------|---------------------------|--------------------|
| GET    | `/api/repositories`       | list               |
| POST   | `/api/repositories`       | add                |
| GET    | `/api/repositories/{id}`  | get one            |
| DELETE | `/api/repositories/{id}`  | remove             |

**Cluster**

| Method | Path                                          | Purpose                        |
|--------|-----------------------------------------------|--------------------------------|
| POST   | `/api/cluster/auth`                           | run skectl to get/refresh token|
| GET    | `/api/cluster/{namespace}/resources`          | all five kinds at once         |
| GET    | `/api/cluster/{namespace}/resource/{kind}`    | one kind                       |

`kind` is one of: `configmap`, `deployment`, `secret`, `service`, `ingress`.
Secret values are redacted by default; add `?reveal_secrets=true` to include them.

## How cluster auth works

The backend runs the same binaries you use by hand. Because setups differ in how
`skectl` hands its token to `kubectl`, the behaviour is configured in `.env`:

- **kubeconfig mode (default, `SKECTL_TOKEN_MODE=false`)** — running `skectl`
  updates your kubeconfig, so plain `kubectl` calls are authenticated afterwards.
  Either leave `SKECTL_CMD` blank and authenticate yourself in a terminal first,
  or set `SKECTL_CMD` so the backend refreshes via `POST /api/cluster/auth`.
- **token mode (`SKECTL_TOKEN_MODE=true`)** — `SKECTL_CMD` prints a bearer token
  on stdout; the backend caches it (`TOKEN_TTL`) and passes it to kubectl with
  `--token`.

If `skectl` needs interactive SSO (browser/password), run it in your terminal
first and keep `SKECTL_CMD` blank — the backend then just uses the live session.

On Windows, if `kubectl`/`skectl` aren't resolved from PATH, set `KUBECTL_BIN`
(and `SKECTL_BIN`) to the full `.exe` path.

## Next phases (not built yet)

Helm-render + field-level drift compare, and the remediation PR to Azure DevOps.
