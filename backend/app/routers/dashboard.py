from fastapi import APIRouter

from app import state

router = APIRouter()


def _readiness(score: float) -> str:
    if score >= 90:
        return "green"
    if score >= 70:
        return "yellow"
    return "red"


@router.get("/summary")
def dashboard_summary():
    reports = state.scan_history
    if not reports:
        return {
            "avg_parity_score": 100.0,
            "total_apps": 0,
            "drifted_apps": 0,
            "critical_items": 0,
            "high_items": 0,
            "apps": [],
        }

    avg_score = round(sum(r.parity_score for r in reports) / len(reports), 1)
    drifted = [r for r in reports if r.drift_items]
    critical_count = sum(1 for r in reports for i in r.drift_items if i.severity == "critical")
    high_count = sum(1 for r in reports for i in r.drift_items if i.severity == "high")

    apps = [
        {
            "app": r.app,
            "parity_score": r.parity_score,
            "readiness": _readiness(r.parity_score),
            "drift_count": len(r.drift_items),
            "root_cause": r.root_cause,
            "root_cause_confidence": r.root_cause_confidence,
        }
        for r in sorted(reports, key=lambda x: x.parity_score)
    ]

    return {
        "avg_parity_score": avg_score,
        "total_apps": len(reports),
        "drifted_apps": len(drifted),
        "critical_items": critical_count,
        "high_items": high_count,
        "apps": apps,
    }
