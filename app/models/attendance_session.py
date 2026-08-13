from datetime import datetime

from sqlalchemy import DateTime, String, ForeignKey, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base



class AttendanceSession(Base):

    __tablename__ = "attendance_sessions"

    # --------------------------------------------------------
    # Primary Key
    # --------------------------------------------------------

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    # --------------------------------------------------------
    # Foreign Key to Teacher
    # --------------------------------------------------------

    teacher_id = Column(
        Integer,
        ForeignKey("teachers.id"),
        nullable=False,
        index=True,
    )

    # --------------------------------------------------------
    # Session Status
    # ACTIVE / COMPLETED / CANCELLED
    # --------------------------------------------------------

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="ACTIVE"
    )

    # --------------------------------------------------------
    # Session Start Time
    # --------------------------------------------------------

    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # --------------------------------------------------------
    # Session End Time
    # NULL while session is active
    # --------------------------------------------------------

    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    # --------------------------------------------------------
    # Created At
    # --------------------------------------------------------

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # --------------------------------------------------------
    # Relationship
    # --------------------------------------------------------

    attendance_records = relationship(
        "AttendanceRecord",
        back_populates="session",
        cascade="all, delete-orphan"
    )
