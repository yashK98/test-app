# Parity — Kubernetes Environment Drift Detection & Auto-Remediation

Hackathon MVP for the "Environment Drift Detection & Auto-Remediation Tool" problem statement,
scoped to **Kubernetes only** (Prod vs DR). Config comparison, ML-based root cause prediction,
simulated auto-remediation, and a monitoring dashboard.

## What it does

- **Environment Comparison Engine** — diffs synthetic K8s Deployment state (image tags, replicas,
  resource limits, env vars, ConfigMap keys, Secret keys) between Prod and DR for 8 apps.
- **Drift Detection & Alerting** — flags mismatches with severity (low/medium/high/critical) and
  computes a parity score (0–100%) per app.
- **ML Root Cause Engine** — a RandomForest classifier (trained at startup on synthesized labelled
  drift patterns) predicts *why* drift happened: manual kubectl edit, bad Helm deploy, config drift,
  or stale DR sync — with a confidence score.
- **Remediation Recommendations** — ranked fix suggestions (config sync / image tag sync / replica
  sync / full rollback) with a predicted success likelihood, and a simulated one-click "apply".
- **Drift Monitoring Dashboard** — fleet-wide parity score, release readiness (green/yellow/red)
  per app, trend chart, and drilldown into a git-diff-style view of exactly what changed.
- **NLG Summary** — auto-generated plain-English summary of each drift event for non-technical
  stakeholders.

No live cluster is required — the backend seeds realistic synthetic K8s state (with intentionally
injected drift patterns) on startup so the whole flow is demoable offline.

## Run it

### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
API docs at `http://localhost:8000/docs`.

### Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173`. The Vite dev server proxies `/api/*` to `localhost:8000`.

## Demo flow

1. Land on the dashboard — see fleet-wide parity score, drifted app count, and a trend chart for
   the worst-scoring app.
2. Click **"run scan"** to re-run drift detection live.
3. Click into any red/yellow app card to see the exact diff (git-diff style), the ML-predicted
   root cause with confidence, and ranked remediation suggestions.
4. Click **"apply fix"** to simulate remediation — the app re-syncs DR from Prod and the parity
   score updates on next scan.

## Roadmap (not in this scope)

- Extend comparison engine to DB schemas and API/dependency versions (as called out in the
  original problem statement)
- Connect to a real cluster via the Kubernetes API instead of synthetic state
- Replace the synthetic training set with real historical drift/incident data
- Real auto-remediation execution (kubectl apply / Helm rollback) with approval gates
