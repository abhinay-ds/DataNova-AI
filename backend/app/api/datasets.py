import logging
import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.memory.session_manager import SessionManager
from app.database import get_db
from app.models.dataset import Dataset
from app.models.project import Project
from app.models.user import User
from app.schemas.dataset import DatasetResponse
from app.services.file_service import FileService


logger = logging.getLogger(__name__)

BACKEND_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

router = APIRouter(
    prefix="/projects",
    tags=["Datasets"],
)


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
    "/{project_id}/datasets",
    response_model=list[DatasetResponse],
)
def list_project_datasets(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    get_owned_project(
        project_id=project_id,
        current_user=current_user,
        db=db,
    )

    return (
        db.query(Dataset)
        .filter(
            Dataset.project_id == project_id
        )
        .order_by(Dataset.created_at.desc())
        .all()
    )


@router.get(
    "/{project_id}/datasets/{dataset_id}",
    response_model=DatasetResponse,
)
def get_project_dataset(
    project_id: int,
    dataset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    get_owned_project(
        project_id=project_id,
        current_user=current_user,
        db=db,
    )

    dataset = (
        db.query(Dataset)
        .filter(
            Dataset.id == dataset_id,
            Dataset.project_id == project_id,
        )
        .first()
    )

    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found.",
        )

    return dataset


@router.get(
    "/{project_id}/datasets/{dataset_id}/analysis",
)
def get_project_dataset_analysis(
    project_id: int,
    dataset_id: int,
    session_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    get_owned_project(
        project_id=project_id,
        current_user=current_user,
        db=db,
    )

    dataset = (
        db.query(Dataset)
        .filter(
            Dataset.id == dataset_id,
            Dataset.project_id == project_id,
        )
        .first()
    )

    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found.",
        )

    if not dataset.storage_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset storage path is missing.",
        )

    storage_path = dataset.storage_path
    if not os.path.isabs(storage_path):
        storage_path = os.path.join(BACKEND_DIR, storage_path)

    if not os.path.exists(storage_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset file does not exist on disk.",
        )

    try:
        dataframe = FileService.load_dataframe(storage_path)
        analysis = FileService.analyze_dataset(storage_path, df=dataframe, include_llm_summary=False)
    except Exception as e:
        logger.exception("Error analyzing dataset %s: %s", dataset_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze dataset file: {str(e)}",
        )

    if session_id:
        try:
            memory = SessionManager.get_memory(session_id)
            memory.dataset.set_dataset(dataframe)
            if isinstance(analysis, dict):
                memory.dataset.set_profile(analysis.get("profile", {}))
                memory.dataset.set_quality(analysis.get("quality", {}))
                memory.dataset.set_insights(analysis.get("insights", {}))
                memory.dataset.set_recommendations(analysis.get("recommendations", {}))
        except Exception as mem_err:
            logger.warning(
                "Could not populate session memory on dataset analysis load: %s",
                mem_err,
            )

    created_at_str = (
        dataset.created_at.isoformat()
        if hasattr(dataset.created_at, "isoformat")
        else str(dataset.created_at)
    )

    return {
        "success": True,
        "id": dataset.id,
        "dataset_id": dataset.id,
        "project_id": dataset.project_id,
        "filename": dataset.filename,
        "file_type": dataset.file_type,
        "rows": dataset.rows,
        "columns": dataset.columns,
        "storage_path": dataset.storage_path,
        "created_at": created_at_str,
        **(analysis if isinstance(analysis, dict) else {}),
    }


@router.delete(
    "/{project_id}/datasets/{dataset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project_dataset(
    project_id: int,
    dataset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    get_owned_project(
        project_id=project_id,
        current_user=current_user,
        db=db,
    )

    dataset = (
        db.query(Dataset)
        .filter(
            Dataset.id == dataset_id,
            Dataset.project_id == project_id,
        )
        .first()
    )

    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found.",
        )

    db.delete(dataset)
    db.commit()

    return None