from typing import Any
from pathlib import Path
import logging
import os
import shutil
import uuid

logger = logging.getLogger(__name__)

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Depends,
    status,
)
from sqlalchemy.orm import Session

from app.services.file_service import FileService
from app.core.memory.session_manager import SessionManager

from app.api.dependencies import get_current_user
from app.database import get_db
from app.models.dataset import Dataset
from app.models.project import Project
from app.models.user import User


router = APIRouter(
    prefix="/upload",
    tags=["Upload"],
)


from app.core.config import settings

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
upload_base = settings.DATA_DIR if settings.DATA_DIR else BACKEND_DIR
UPLOAD_FOLDER = os.path.join(upload_base, "uploads")

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True,
)


ALLOWED_EXTENSIONS = {
    ".csv",
    ".xlsx",
    ".xls",
    ".json",
}


@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    session_id: str = "default",
    project_id: int | None = None,
    current_user: Any = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    try:
        if getattr(current_user, "is_guest", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Guest users cannot upload permanent datasets. Please sign in or create an account.",
            )

        # =================================================
        # Validate project
        # =================================================

        if project_id is None:

            raise HTTPException(
                status_code=400,
                detail="project_id is required.",
            )

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
                status_code=404,
                detail="Project not found.",
            )

        # =================================================
        # Validate filename
        # =================================================

        if not file.filename:

            raise HTTPException(
                status_code=400,
                detail="No file provided.",
            )

        extension = Path(
            file.filename
        ).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Only CSV, Excel and JSON "
                    "files are supported."
                ),
            )

        # =================================================
        # Get session memory
        # =================================================

        memory = SessionManager.get_memory(
            session_id
        )

        # =================================================
        # Create unique storage filename
        # =================================================

        safe_basename = Path(file.filename).name
        unique_filename = (
            f"{uuid.uuid4().hex}_"
            f"{safe_basename}"
        )

        file_path = os.path.join(
            UPLOAD_FOLDER,
            unique_filename,
        )

        # =================================================
        # Save uploaded file
        # =================================================

        with open(
            file_path,
            "wb",
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer,
            )

        # =================================================
        # Load dataframe
        # =================================================

        dataframe = FileService.load_dataframe(
            file_path
        )

        # =================================================
        # Store dataset in SESSION memory
        # =================================================

        memory.dataset.set_dataset(
            dataframe
        )

        # =================================================
        # Generate analysis (reuse parsed dataframe, omit slow LLM call)
        # =================================================

        analysis = FileService.analyze_dataset(
            file_path,
            df=dataframe,
            include_llm_summary=False,
        )

        # =================================================
        # Store analysis in SESSION memory
        # =================================================

        if isinstance(analysis, dict):

            memory.dataset.set_profile(
                analysis.get(
                    "profile",
                    {},
                )
            )

            memory.dataset.set_quality(
                analysis.get(
                    "quality",
                    {},
                )
            )

            memory.dataset.set_insights(
                analysis.get(
                    "insights",
                    {},
                )
            )

            memory.dataset.set_recommendations(
                analysis.get(
                    "recommendations",
                    {},
                )
            )

        # =================================================
        # Create persistent Dataset record
        # =================================================

        dataset_record = Dataset(
            project_id=project.id,
            filename=file.filename,
            file_type=extension.lstrip("."),
            rows=int(
                len(dataframe)
            ),
            columns=int(
                len(dataframe.columns)
            ),
            storage_path=file_path,
        )

        db.add(dataset_record)
        db.commit()
        db.refresh(dataset_record)

        # =================================================
        # Return response
        # =================================================

        return {
            "success": True,

            "message": (
                "File uploaded successfully."
            ),

            "session_id": session_id,

            "project_id": project.id,

            "dataset_id": dataset_record.id,

            "dataset": analysis,
        }

    except HTTPException:

        raise

    except Exception as e:

        db.rollback()
        logger.exception("Error processing file upload: %s", e)

        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the uploaded file.",
        )