from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class FaceEmbedding(Base):

    __tablename__ = "face_embeddings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    embedding: Mapped[list[float]] = mapped_column(
        ARRAY(Float),
        nullable=False
    )

    model_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="face_recognition"
    )

    model_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="v1"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    student = relationship(
        "Student",
        back_populates="face_embeddings"
    )