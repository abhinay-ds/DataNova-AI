from datetime import datetime, timezone
import logging
import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database import get_db
from app.models.analysis import Analysis
from app.models.dataset import Dataset
from app.models.project import Project
from app.models.user import User
from app.services.file_service import FileService
from app.services.report_export_service import ReportExportService
from app.services.report_service import ReportService


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/projects",
    tags=["Reports"],
)


class ReportGenerateRequest(BaseModel):
    dataset_id: Optional[int] = None


class ReportResponse(BaseModel):
    id: int
    project_id: int
    title: str
    filename: str
    url: str
    created_at: datetime
    dataset_name: Optional[str] = None


def get_owned_project(
    project_id: int,
    current_user: User,
    db: Session,
) -> Project:
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.owner_id == current_user.id,
        )
        .first()
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    return project


@router.post(
    "/{project_id}/reports/generate",
    status_code=status.HTTP_201_CREATED,
)
def generate_project_report(
    project_id: int,
    payload: Optional[ReportGenerateRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = get_owned_project(project_id, current_user, db)

    # Determine which dataset to generate report for
    target_dataset_id = payload.dataset_id if payload else None

    if target_dataset_id:
        dataset = (
            db.query(Dataset)
            .filter(
                Dataset.id == target_dataset_id,
                Dataset.project_id == project.id,
            )
            .first()
        )
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found in this project.",
            )
    else:
        # Pick the most recent dataset in the project
        dataset = (
            db.query(Dataset)
            .filter(Dataset.project_id == project.id)
            .order_by(Dataset.created_at.desc())
            .first()
        )
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No dataset available in this project to generate a report from. Please upload a dataset first.",
            )

    # Load dataframe safely
    if not dataset.storage_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset storage path is missing for '{dataset.filename}'.",
        )

    file_path = dataset.storage_path
    if not os.path.isabs(file_path):
        backend_dir = Path(__file__).resolve().parent.parent.parent
        file_path = str(backend_dir / file_path)

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset file '{dataset.filename}' is missing from storage.",
        )

    try:
        df = FileService.load_dataframe(file_path)
    except Exception as err:
        logger.error("Failed to load dataset file for report: %s", err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load and parse dataset file.",
        )

    if df is None or df.empty:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dataset contains no data rows.",
        )

    # Generate raw report structure
    report_res = ReportService.generate(df)
    if not report_res.success or not report_res.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=report_res.message or "Failed to analyze dataset for report.",
        )

    # Export to HTML
    export_res = ReportExportService.export_html(report_res.data)
    if not export_res.success or not export_res.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=export_res.message or "Failed to export report to HTML.",
        )

    filename = export_res.data.get("filename")
    file_path = export_res.data.get("file_path")

    # Persist in Analysis table (reusing existing schema without resetting db)
    analysis_entry = Analysis(
        project_id=project.id,
        title=f"Report: {dataset.filename}",
        question=f"Comprehensive Report for {dataset.filename}",
        result=filename,
    )
    db.add(analysis_entry)
    db.commit()
    db.refresh(analysis_entry)

    report_view_url = f"/projects/{project.id}/reports/{analysis_entry.id}/view"
    report_download_url = f"/projects/{project.id}/reports/{analysis_entry.id}/download"

    return {
        "success": True,
        "message": "Report generated successfully.",
        "report": {
            "id": analysis_entry.id,
            "project_id": project.id,
            "title": analysis_entry.title,
            "filename": filename,
            "url": report_view_url,
            "download_url": report_download_url,
            "created_at": analysis_entry.created_at.isoformat(),
            "dataset_name": dataset.filename,
        },
    }


@router.get(
    "/{project_id}/reports",
)
def list_project_reports(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = get_owned_project(project_id, current_user, db)

    # Query analyses where result ends with .html or title starts with 'Report:'
    analyses = (
        db.query(Analysis)
        .filter(
            Analysis.project_id == project.id,
            (Analysis.title.like("Report:%")) | (Analysis.result.like("%.html")),
        )
        .order_by(Analysis.created_at.desc())
        .all()
    )

    reports = []
    for a in analyses:
        filename = a.result or ""
        reports.append({
            "id": a.id,
            "project_id": project.id,
            "title": a.title,
            "filename": filename,
            "url": f"/projects/{project.id}/reports/{a.id}/view" if filename else None,
            "download_url": f"/projects/{project.id}/reports/{a.id}/download" if filename else None,
            "created_at": a.created_at.isoformat(),
            "dataset_name": a.question.replace("Comprehensive Report for ", "") if a.question and "Comprehensive Report for " in a.question else None,
        })

    return reports


@router.get(
    "/{project_id}/reports/{report_id}/view",
)
def view_project_report(
    project_id: int,
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from fastapi.responses import HTMLResponse

    project = get_owned_project(project_id, current_user, db)

    analysis = (
        db.query(Analysis)
        .filter(
            Analysis.id == report_id,
            Analysis.project_id == project.id,
        )
        .first()
    )

    if not analysis or not analysis.result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found.",
        )

    # Sanitize filename
    filename = Path(analysis.result).name
    report_path = (
        Path(__file__).resolve().parent.parent.parent
        / "static"
        / "reports"
        / filename
    )

    if not report_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file does not exist on disk.",
        )

    return HTMLResponse(
        content=report_path.read_text(encoding="utf-8"),
        status_code=200,
    )


@router.get(
    "/{project_id}/reports/{report_id}/download",
)
def download_project_report(
    project_id: int,
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from fastapi.responses import FileResponse

    project = get_owned_project(project_id, current_user, db)

    analysis = (
        db.query(Analysis)
        .filter(
            Analysis.id == report_id,
            Analysis.project_id == project.id,
        )
        .first()
    )

    if not analysis or not analysis.result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found.",
        )

    filename = Path(analysis.result).name
    report_path = (
        Path(__file__).resolve().parent.parent.parent
        / "static"
        / "reports"
        / filename
    )

    if not report_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file does not exist on disk.",
        )

    return FileResponse(
        path=str(report_path),
        filename=filename,
        media_type="text/html",
    )
