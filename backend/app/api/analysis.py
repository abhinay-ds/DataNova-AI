from datetime import datetime
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database import get_db
from app.models.analysis import Analysis
from app.models.chart import Chart
from app.models.project import Project
from app.models.user import User


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/projects",
    tags=["Analysis & Charts"],
)


class AnalysisResponse(BaseModel):
    id: int
    project_id: int
    title: str
    question: Optional[str] = None
    result: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChartResponse(BaseModel):
    id: int
    project_id: int
    title: str
    chart_type: Optional[str] = None
    file_path: Optional[str] = None
    url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


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


@router.get(
    "/{project_id}/analyses",
    response_model=List[AnalysisResponse],
)
def list_project_analyses(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = get_owned_project(project_id, current_user, db)

    analyses = (
        db.query(Analysis)
        .filter(Analysis.project_id == project.id)
        .order_by(Analysis.created_at.desc())
        .all()
    )
    return analyses


@router.get(
    "/{project_id}/charts",
)
def list_project_charts(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = get_owned_project(project_id, current_user, db)

    charts = (
        db.query(Chart)
        .filter(Chart.project_id == project.id)
        .order_by(Chart.created_at.desc())
        .all()
    )

    result = []
    for c in charts:
        filename = ""
        if c.file_path:
            filename = c.file_path.replace("\\", "/").split("/")[-1]
        result.append({
            "id": c.id,
            "project_id": c.project_id,
            "title": c.title,
            "chart_type": c.chart_type,
            "file_path": c.file_path,
            "url": f"/charts/{filename}" if filename else None,
            "created_at": c.created_at.isoformat(),
        })

    return result
