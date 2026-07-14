from datetime import datetime, timedelta

from app.data_generator import generate_state
from app.drift_engine import build_report
from app.ml_engine import root_cause_model
from app.summary_engine import generate_summary
from app.models import DriftReport

cluster_state: dict = {}
ground_truth_causes: dict = {}
scan_history: list[DriftReport] = []
trend_history: dict[str, list[dict]] = {}  # app -> [{date, parity_score}]


def initialize():
    global cluster_state, ground_truth_causes, scan_history, trend_history
    cluster_state, ground_truth_causes = generate_state()
    root_cause_model.train()
    scan_history = []
    trend_history = {app: [] for app in cluster_state}
    _run_full_scan(seed_trend=True)


def _run_full_scan(seed_trend: bool = False):
    """Runs prod-vs-dr comparison for every app, predicts root cause, stores report."""
    global scan_history
    scan_history = []
    for app, envs in cluster_state.items():
        baseline = envs["prod"]
        target = envs["dr"]
        report = build_report(app, baseline, target)

        days_since_modified = (datetime.utcnow() - datetime.fromisoformat(target.last_modified)).total_seconds() / 86400
        cause, confidence = root_cause_model.predict(report.drift_items, target, days_since_modified)
        report.root_cause = cause
        report.root_cause_confidence = confidence
        report.summary = generate_summary(report)

        scan_history.append(report)

        if seed_trend:
            _seed_trend_for_app(app, report.parity_score)


def _seed_trend_for_app(app: str, current_score: float):
    """Creates a plausible 14-day trend ending at current_score for dashboard charts."""
    import random
    rnd = random.Random(hash(app) % 10000)
    points = []
    score = max(50.0, current_score + rnd.uniform(5, 15))
    for i in range(13, -1, -1):
        date = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
        drift = rnd.uniform(-3, 3)
        score = max(0.0, min(100.0, score + drift))
        points.append({"date": date, "parity_score": round(score, 1)})
    points[-1] = {"date": points[-1]["date"], "parity_score": current_score}
    trend_history[app] = points


def rescan():
    _run_full_scan(seed_trend=False)
    for report in scan_history:
        history = trend_history.setdefault(report.app, [])
        history.append({"date": datetime.utcnow().strftime("%Y-%m-%d %H:%M"), "parity_score": report.parity_score})
        trend_history[report.app] = history[-30:]
    return scan_history


def get_report_for_app(app: str) -> DriftReport | None:
    for r in scan_history:
        if r.app == app:
            return r
    return None


def apply_remediation(app: str, action: str) -> bool:
    """Simulates applying a remediation by syncing target(dr)'s relevant field(s) from prod."""
    envs = cluster_state.get(app)
    if not envs:
        return False
    prod = envs["prod"]
    dr = envs["dr"]

    if action == "config_sync":
        dr.config_map_keys = list(prod.config_map_keys)
        dr.env_vars = dict(prod.env_vars)
    elif action == "image_tag_sync":
        dr.containers[0].image_tag = prod.containers[0].image_tag
    elif action == "replica_sync":
        dr.replicas = prod.replicas
    elif action == "full_rollback":
        dr.containers[0].image_tag = prod.containers[0].image_tag
        dr.replicas = prod.replicas
        dr.env_vars = dict(prod.env_vars)
        dr.config_map_keys = list(prod.config_map_keys)
        dr.secret_keys = list(prod.secret_keys)
    else:
        return False

    dr.last_modified = datetime.utcnow().isoformat()
    dr.modified_by = "auto-remediation"
    return True
