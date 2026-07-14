from datetime import datetime

from app.models import DeploymentSpec, DriftItem, DriftReport

SEVERITY_WEIGHT = {"low": 1, "medium": 3, "high": 6, "critical": 10}


def compare_specs(baseline: DeploymentSpec, target: DeploymentSpec) -> list[DriftItem]:
    """Diffs two DeploymentSpecs (e.g. prod vs dr) and returns a list of drift items."""
    items: list[DriftItem] = []

    b_container = baseline.containers[0]
    t_container = target.containers[0]

    if b_container.image_tag != t_container.image_tag:
        items.append(DriftItem(
            field="image_tag",
            category="image",
            baseline_value=b_container.image_tag,
            target_value=t_container.image_tag,
            severity="high",
            description=f"Image tag mismatch: {baseline.environment}={b_container.image_tag} vs {target.environment}={t_container.image_tag}",
        ))

    if baseline.replicas != target.replicas:
        items.append(DriftItem(
            field="replicas",
            category="replicas",
            baseline_value=str(baseline.replicas),
            target_value=str(target.replicas),
            severity="medium",
            description=f"Replica count differs: {baseline.environment}={baseline.replicas} vs {target.environment}={target.replicas}",
        ))

    if b_container.cpu_limit != t_container.cpu_limit or b_container.memory_limit != t_container.memory_limit:
        items.append(DriftItem(
            field="resource_limits",
            category="resources",
            baseline_value=f"cpu={b_container.cpu_limit}, mem={b_container.memory_limit}",
            target_value=f"cpu={t_container.cpu_limit}, mem={t_container.memory_limit}",
            severity="medium",
            description=f"Resource limits differ between {baseline.environment} and {target.environment}",
        ))

    all_env_keys = set(baseline.env_vars.keys()) | set(target.env_vars.keys())
    for key in sorted(all_env_keys):
        bv = baseline.env_vars.get(key)
        tv = target.env_vars.get(key)
        if bv != tv:
            items.append(DriftItem(
                field=f"env_var:{key}",
                category="env_vars",
                baseline_value=bv,
                target_value=tv,
                severity="low" if key in ("LOG_LEVEL", "FEATURE_FLAG_NEW_UI") else "medium",
                description=f"Env var '{key}' differs: {baseline.environment}={bv} vs {target.environment}={tv}",
            ))

    missing_config = set(baseline.config_map_keys) - set(target.config_map_keys)
    extra_config = set(target.config_map_keys) - set(baseline.config_map_keys)
    for key in missing_config:
        items.append(DriftItem(
            field=f"configmap:{key}",
            category="config",
            baseline_value="present",
            target_value="missing",
            severity="high",
            description=f"ConfigMap key '{key}' present in {baseline.environment} but missing in {target.environment}",
        ))
    for key in extra_config:
        items.append(DriftItem(
            field=f"configmap:{key}",
            category="config",
            baseline_value="missing",
            target_value="present",
            severity="medium",
            description=f"ConfigMap key '{key}' present in {target.environment} but not in {baseline.environment}",
        ))

    missing_secret = set(baseline.secret_keys) - set(target.secret_keys)
    for key in missing_secret:
        items.append(DriftItem(
            field=f"secret:{key}",
            category="secret",
            baseline_value="present",
            target_value="missing",
            severity="critical",
            description=f"Secret '{key}' present in {baseline.environment} but missing in {target.environment}",
        ))

    return items


def compute_parity_score(drift_items: list[DriftItem]) -> float:
    """100 = perfect parity. Each drift item subtracts weighted penalty, floored at 0."""
    if not drift_items:
        return 100.0
    penalty = sum(SEVERITY_WEIGHT.get(item.severity, 1) for item in drift_items)
    score = max(0.0, 100.0 - penalty * 4)
    return round(score, 1)


def build_report(app: str, baseline: DeploymentSpec, target: DeploymentSpec) -> DriftReport:
    drift_items = compare_specs(baseline, target)
    parity = compute_parity_score(drift_items)
    return DriftReport(
        app=app,
        baseline_env=baseline.environment,
        target_env=target.environment,
        parity_score=parity,
        drift_items=drift_items,
        scanned_at=datetime.utcnow().isoformat(),
    )
