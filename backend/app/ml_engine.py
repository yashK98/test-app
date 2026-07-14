"""ML-based root cause classifier for drift events.

Trains a small RandomForest on synthetically generated drift feature
vectors labelled with their true cause. Features are engineered from the
same signals a human would look at: which categories drifted, severity
mix, how recently the target env was modified, and who/what modified it.
This is intentionally lightweight (fits in seconds) so it can train at
FastAPI startup for a hackathon demo, while still being a real trained
model rather than a hardcoded rule table.
"""
import random

import numpy as np
from sklearn.ensemble import RandomForestClassifier

from app.models import DriftItem, DeploymentSpec

CAUSES = ["manual_kubectl_edit", "bad_helm_deploy", "config_drift", "stale_dr_sync"]

FEATURE_NAMES = [
    "n_image_drift",
    "n_replica_drift",
    "n_resource_drift",
    "n_env_var_drift",
    "n_config_drift",
    "n_secret_drift",
    "days_since_modified",
    "modified_by_is_manual",
    "modified_by_is_pipeline",
    "target_is_dr",
]


def _featurize(drift_items: list[DriftItem], target: DeploymentSpec, days_since_modified: float) -> list[float]:
    counts = {"image": 0, "replicas": 0, "resources": 0, "env_vars": 0, "config": 0, "secret": 0}
    for item in drift_items:
        if item.category in counts:
            counts[item.category] += 1
    return [
        counts["image"],
        counts["replicas"],
        counts["resources"],
        counts["env_vars"],
        counts["config"],
        counts["secret"],
        days_since_modified,
        1.0 if "manual" in target.modified_by.lower() else 0.0,
        1.0 if "pipeline" in target.modified_by.lower() and "stale" not in target.modified_by.lower() else 0.0,
        1.0 if target.environment == "dr" else 0.0,
    ]


def _synthesize_training_set(n_per_class: int = 60, seed: int = 7):
    rng = random.Random(seed)
    X, y = [], []

    for _ in range(n_per_class):
        # manual_kubectl_edit: replica + env var drift, modified_by manual, recent, not dr
        X.append([0, rng.choice([1, 1, 2]), 0, rng.choice([1, 2]), 0, 0,
                   rng.uniform(0, 3), 1.0, 0.0, 0.0])
        y.append("manual_kubectl_edit")

    for _ in range(n_per_class):
        # bad_helm_deploy: image + resource drift, modified_by pipeline, very recent
        X.append([1, 0, rng.choice([0, 1]), rng.choice([0, 1]), 0, 0,
                   rng.uniform(0, 1), 0.0, 1.0, 0.0])
        y.append("bad_helm_deploy")

    for _ in range(n_per_class):
        # config_drift: config key missing, no image/replica change, moderate age, not dr
        X.append([0, 0, 0, rng.choice([0, 1]), rng.choice([1, 2]), 0,
                   rng.uniform(5, 20), 0.0, 1.0, 0.0])
        y.append("config_drift")

    for _ in range(n_per_class):
        # stale_dr_sync: multiple categories drifted, target is dr, old modification, "stale" pipeline
        X.append([rng.choice([0, 1]), rng.choice([0, 1]), 0, 0, rng.choice([1, 2]), 0,
                   rng.uniform(30, 90), 0.0, 0.0, 1.0])
        y.append("stale_dr_sync")

    return np.array(X, dtype=float), np.array(y)


class RootCauseModel:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=7)
        self._trained = False

    def train(self):
        X, y = _synthesize_training_set()
        self.model.fit(X, y)
        self._trained = True

    def predict(self, drift_items: list[DriftItem], target: DeploymentSpec, days_since_modified: float):
        if not self._trained:
            self.train()
        if not drift_items:
            return None, None
        features = np.array([_featurize(drift_items, target, days_since_modified)])
        proba = self.model.predict_proba(features)[0]
        classes = self.model.classes_
        best_idx = int(np.argmax(proba))
        return classes[best_idx], round(float(proba[best_idx]), 3)


root_cause_model = RootCauseModel()
