from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database import get_db
from app.models.dataset import Dataset
from app.models.project import Project
from app.models.user import User
from app.schemas.dataset import DatasetResponse


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