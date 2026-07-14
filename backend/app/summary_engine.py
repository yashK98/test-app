"""Generates a plain-English summary of a drift report. Template-based NLG:
deterministic, fast, no external API dependency - good fit for a hackathon
demo where reliability matters more than generative flourish."""

from app.models import DriftReport

CAUSE_LABELS = {
    "manual_kubectl_edit": "an unauthorized manual change (kubectl edit) applied directly to the cluster",
    "bad_helm_deploy": "a Helm deployment that shipped an unintended image or resource change",
    "config_drift": "configuration drift from a missing or out-of-sync ConfigMap key",
    "stale_dr_sync": "a Disaster Recovery environment that has fallen behind on recent releases",
}


def generate_summary(report: DriftReport) -> str:
    if not report.drift_items:
        return (
            f"{report.app} is in full parity between {report.baseline_env} and "
            f"{report.target_env}. No action needed."
        )

    by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for item in report.drift_items:
        by_severity[item.severity] = by_severity.get(item.severity, 0) + 1

    severity_bits = [f"{count} {sev}" for sev, count in by_severity.items() if count]
    severity_str = ", ".join(severity_bits)

    lead = (
        f"{report.app} has drifted between {report.baseline_env} and {report.target_env} "
        f"(parity score {report.parity_score}%). Detected {len(report.drift_items)} drift item(s): {severity_str}."
    )

    cause_bit = ""
    if report.root_cause:
        cause_desc = CAUSE_LABELS.get(report.root_cause, report.root_cause)
        conf_pct = round((report.root_cause_confidence or 0) * 100)
        cause_bit = f" Likely cause: {cause_desc} ({conf_pct}% confidence)."

    top_items = sorted(report.drift_items, key=lambda i: {"critical": 0, "high": 1, "medium": 2, "low": 3}[i.severity])[:3]
    detail_bit = " Key differences: " + "; ".join(i.description for i in top_items) + "."

    return lead + cause_bit + detail_bit
