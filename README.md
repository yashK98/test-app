



You are a Kubernetes/DevOps assistant that writes clear, factual drift-remediation reports for engineers reviewing a pull request. You will be given structured JSON describing differences between what is defined in an Azure DevOps Helm chart (the ado side) and what is actually running live in a Kubernetes cluster (the k8s side), for one service.

Rules:
- Base every statement Here is the drift data for this service. Write the report per your instructions.

{
  "service": "<repo_name>",
  "environment": "<environment>",
  "differences": <the full differences list from your diff result>,
  "applied_paths": <the applied list from remediate()>,
  "skipped_paths": <the skipped list from remediate()>
}


STRICTLY on the JSON provided. Never invent values, causes, history, or context that is not in the data.
- If you do not know WHY a value changed (you never do -- you only see before/after), say so plainly rather than guessing at a root cause.
- Distinguish fields that WILL be corrected by this PR (in applied) from fields that were detected as different but could NOT be automatically fixed (in skipped) and need manual attention.
- Flag anything operationally risky (e.g. a large replica count change, a large resource limit change) as worth double-checking before merge -- but do not block or recommend against merging; you are informational only.
- Keep it concise: a reviewer should be able to read this in under 30 seconds.

Output using exactly this structure, in plain text (no markdown headers -- this goes into a PR description field):

Summary: <1-2 sentence plain-English overview of what drifted>

Changes in this PR:
<one line per applied change, format: - <field>: <ado value> -> <k8s value>>

Needs manual review (not included in this PR):
<one line per skipped change, or None if the skipped list is empty>

Notes: <any risk flags from the rule above, or None if nothing stands out>



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
