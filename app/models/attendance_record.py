from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class AttendanceRecord(Base):

    __tablename__ = "attendance_records"

    # --------------------------------------------------------
    # Primary Key
    # --------------------------------------------------------

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    # --------------------------------------------------------
    # Attendance Session
    # --------------------------------------------------------

    session_id: Mapped[int] = mapped_column(
        ForeignKey(
            "attendance_sessions.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    # --------------------------------------------------------
    # Student
    # --------------------------------------------------------

    student_id: Mapped[int] = mapped_column(
        ForeignKey(
            "students.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    # --------------------------------------------------------
    # Attendance Status
    # ABSENT / PRESENT
    # --------------------------------------------------------

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="ABSENT"
    )

    # --------------------------------------------------------
    # Time when student was marked present
    # NULL while absent
    # --------------------------------------------------------

    marked_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    # --------------------------------------------------------
    # Relationships
    # --------------------------------------------------------

    session = relationship(
        "AttendanceSession",
        back_populates="attendance_records"
    )

    student = relationship(
        "Student",
        back_populates="attendance_records"
    )

    # --------------------------------------------------------
    # Prevent duplicate attendance for the same student
    # in the same session
    # --------------------------------------------------------

    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "student_id",
            name="uq_attendance_session_student"
        ),
    )
