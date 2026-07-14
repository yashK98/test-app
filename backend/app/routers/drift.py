from fastapi import APIRouter, HTTPException

from app import state
from app.models import DriftReport

router = APIRouter()


@router.post("/scan", response_model=list[DriftReport])
def trigger_scan():
    """Re-runs drift detection (prod vs dr) across all apps."""
    return state.rescan()


@router.get("/reports", response_model=list[DriftReport])
def get_all_reports():
    return state.scan_history


@router.get("/reports/{app}", response_model=DriftReport)
def get_app_report(app: str):
    report = state.get_report_for_app(app)
    if not report:
        raise HTTPException(status_code=404, detail="No report for app")
    return report


@router.get("/trend/{app}")
def get_trend(app: str):
    if app not in state.trend_history:
        raise HTTPException(status_code=404, detail="App not found")
    return state.trend_history[app]
