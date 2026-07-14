"""Generates synthetic K8s Deployment state for Dev/Prod/DR so the demo
works without a live cluster connection. Injects realistic drift patterns
(image tag mismatch, replica drift, resource drift, env var drift, config
drift) with an associated "true cause" label used to train the ML model.
"""
import random
from datetime import datetime, timedelta

from app.models import ContainerSpec, DeploymentSpec

random.seed(42)

APPS = [
    "payments-api",
    "onboarding-service",
    "fraud-detection",
    "notifications-worker",
    "ledger-service",
    "auth-gateway",
    "customer-portal",
    "reporting-engine",
]

ENVIRONMENTS = ["dev", "prod", "dr"]

CAUSES = ["manual_kubectl_edit", "bad_helm_deploy", "config_drift", "stale_dr_sync"]

BASE_IMAGE_TAG = {app: f"v{random.randint(1, 4)}.{random.randint(0, 9)}.{random.randint(0, 9)}" for app in APPS}
BASE_REPLICAS = {app: random.choice([2, 3, 4, 5]) for app in APPS}
BASE_CPU = {app: random.choice(["250m", "500m", "1000m"]) for app in APPS}
BASE_MEM = {app: random.choice(["256Mi", "512Mi", "1Gi"]) for app in APPS}
BASE_ENV_KEYS = {
    app: {
        "LOG_LEVEL": "info",
        "FEATURE_FLAG_NEW_UI": "false",
        "RATE_LIMIT": "1000",
        "TIMEOUT_MS": "3000",
    }
    for app in APPS
}
BASE_CONFIG_KEYS = {app: ["app.properties", "db.connection", "cache.settings"] for app in APPS}
BASE_SECRET_KEYS = {app: ["db-credentials", "api-key", "tls-cert"] for app in APPS}


def _bump_tag(tag: str) -> str:
    major, minor, patch = tag[1:].split(".")
    return f"v{major}.{minor}.{int(patch) + 1}"


def _now_minus(days: int) -> str:
    return (datetime.utcnow() - timedelta(days=days)).isoformat()


def generate_state() -> tuple[dict[str, dict[str, DeploymentSpec]], dict[str, str]]:
    """Returns (state[app][env] -> DeploymentSpec, ground_truth_cause[app] -> cause label)
    Only a subset of apps get drift injected; others stay in parity (prod == dr, dev may
    legitimately differ since dev is expected to move faster).
    """
    state: dict[str, dict[str, DeploymentSpec]] = {}
    ground_truth: dict[str, str] = {}

    drifted_apps = random.sample(APPS, k=5)

    for app in APPS:
        tag = BASE_IMAGE_TAG[app]
        replicas = BASE_REPLICAS[app]
        cpu = BASE_CPU[app]
        mem = BASE_MEM[app]
        env_vars = dict(BASE_ENV_KEYS[app])
        config_keys = list(BASE_CONFIG_KEYS[app])
        secret_keys = list(BASE_SECRET_KEYS[app])

        def make_spec(environment, tag_, replicas_, cpu_, mem_, env_vars_, config_keys_, secret_keys_, modified_by, days_ago):
            return DeploymentSpec(
                app=app,
                environment=environment,
                replicas=replicas_,
                containers=[
                    ContainerSpec(
                        name=f"{app}-container",
                        image=f"registry.internal/{app}",
                        image_tag=tag_,
                        cpu_request=cpu_,
                        cpu_limit=cpu_,
                        memory_request=mem_,
                        memory_limit=mem_,
                    )
                ],
                env_vars=env_vars_,
                config_map_keys=config_keys_,
                secret_keys=secret_keys_,
                service_port=8080,
                last_modified=_now_minus(days_ago),
                modified_by=modified_by,
            )

        dev_spec = make_spec("dev", _bump_tag(tag), replicas, cpu, mem, {**env_vars, "FEATURE_FLAG_NEW_UI": "true"}, config_keys, secret_keys, "ci-pipeline", 1)
        prod_spec = make_spec("prod", tag, replicas, cpu, mem, env_vars, config_keys, secret_keys, "ci-pipeline", 10)
        dr_spec = make_spec("dr", tag, replicas, cpu, mem, env_vars, config_keys, secret_keys, "ci-pipeline", 10)

        if app in drifted_apps:
            cause = random.choice(CAUSES)
            ground_truth[app] = cause

            if cause == "manual_kubectl_edit":
                # someone hand-edited prod: replica count + one env var changed, no matching commit
                prod_spec = make_spec(
                    "prod", tag, replicas + random.choice([-1, 1, 2]), cpu, mem,
                    {**env_vars, "RATE_LIMIT": str(int(env_vars["RATE_LIMIT"]) + 500)},
                    config_keys, secret_keys, "jane.doe (manual)", 1,
                )
            elif cause == "bad_helm_deploy":
                # deploy pushed wrong image tag + resource limits changed, deployed by pipeline recently
                prod_spec = make_spec(
                    "prod", _bump_tag(tag), replicas, "250m" if cpu != "250m" else "500m", mem,
                    env_vars, config_keys, secret_keys, "ci-pipeline", 0,
                )
            elif cause == "config_drift":
                # a configmap key silently removed in prod, values unchanged otherwise
                prod_spec = make_spec(
                    "prod", tag, replicas, cpu, mem, env_vars,
                    [k for k in config_keys if k != "cache.settings"], secret_keys, "ci-pipeline", 15,
                )
            elif cause == "stale_dr_sync":
                # DR wasn't updated in the last few releases: several fields behind
                dr_spec = make_spec(
                    "dr", tag, max(1, replicas - 1), cpu, mem, env_vars,
                    config_keys[:-1] if len(config_keys) > 1 else config_keys,
                    secret_keys, "ci-pipeline (stale)", 60,
                )

        state[app] = {"dev": dev_spec, "prod": prod_spec, "dr": dr_spec}

    return state, ground_truth
