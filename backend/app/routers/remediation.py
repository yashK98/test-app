from fastapi import APIRouter, HTTPException

from app import state
from app.models import RemediationSuggestion, RemediationResult

router = APIRouter()

# Static, demo-friendly success-likelihood priors per action type, per root cause.
# In a production system this would be learned from historical remediation outcomes.
ACTION_LIKELIHOOD = {
    "manual_kubectl_edit": [("full_rollback", 0.91), ("replica_sync", 0.75)],
    "bad_helm_deploy": [("image_tag_sync", 0.93), ("full_rollback", 0.88)],
    "config_drift": [("config_sync", 0.95)],
    "stale_dr_sync": [("full_rollback", 0.90), ("config_sync", 0.82), ("replica_sync", 0.7)],
}

ACTION_DESCRIPTIONS = {
    "config_sync": "Sync ConfigMap keys and environment variables from prod baseline",
    "image_tag_sync": "Sync container image tag to match prod baseline",
    "replica_sync": "Restore replica count to match prod baseline",
    "full_rollback": "Full rollback of target environment to prod baseline (image, replicas, config, env vars)",
}


@router.get("/suggestions/{app}", response_model=list[RemediationSuggestion])
def get_suggestions(app: str):
    report = state.get_report_for_app(app)
    if not report:
        raise HTTPException(status_code=404, detail="No report for app")
    if not report.drift_items:
        return []

    cause = report.root_cause or "config_drift"
    actions = ACTION_LIKELIHOOD.get(cause, [("config_sync", 0.7)])

    return [
        RemediationSuggestion(
            app=app,
            target_env=report.target_env,
            action=action,
            description=ACTION_DESCRIPTIONS[action],
            success_likelihood=likelihood,
        )
        for action, likelihood in sorted(actions, key=lambda x: -x[1])
    ]


@router.post("/apply/{app}/{action}", response_model=RemediationResult)
def apply(app: str, action: str):
    report = state.get_report_for_app(app)
    if not report:
        raise HTTPException(status_code=404, detail="No report for app")

    ok = state.apply_remediation(app, action)
    if not ok:
        raise HTTPException(status_code=400, detail="Unknown remediation action")

    return RemediationResult(
        app=app,
        target_env=report.target_env,
        action=action,
        status="success",
        message=f"Applied '{action}' to {app} in {report.target_env}. Re-run a scan to confirm parity.",
    )
