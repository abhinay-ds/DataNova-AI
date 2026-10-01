from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # User who owns this project
    owner = relationship(
        "User",
        back_populates="projects",
    )

    # Project datasets
    datasets = relationship(
        "Dataset",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    # Project conversations
    conversations = relationship(
        "Conversation",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    # Saved analyses
    analyses = relationship(
        "Analysis",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    # Saved charts
    charts = relationship(
        "Chart",
        back_populates="project",
        cascade="all, delete-orphan",
    )