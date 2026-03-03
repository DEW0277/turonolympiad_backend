"""Level database model.

This module defines the Level SQLAlchemy model for organizing tests by grade or proficiency level.
"""

from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Level(Base):
    """Level model for organizing tests by grade or proficiency level.
    
    Represents a subdivision within a Subject, such as Grade 5 or Grade 6.
    Levels contain multiple Tests, which in turn contain Questions.
    
    Attributes:
        id: Primary key, auto-incrementing integer
        subject_id: Foreign key to Subject, indexed for fast lookups
        name: Level name (1-100 characters), indexed for fast lookups
        created_at: Timestamp when level was created
        updated_at: Timestamp when level was last updated
        subject: Many-to-one relationship with Subject model
        tests: One-to-many relationship with Test model (cascade delete)
    """
    
    __tablename__ = "levels"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    subject_id: Mapped[int] = mapped_column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    subject: Mapped["Subject"] = relationship(
        "Subject",
        back_populates="levels",
        lazy="select"
    )
    tests: Mapped[list["Test"]] = relationship(
        "Test",
        back_populates="level",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("subject_id", "name", name="uq_level_subject_name"),
        Index("idx_level_subject_id", "subject_id"),
        Index("idx_level_name", "name"),
        Index("idx_level_subject_name", "subject_id", "name"),
    )
    
    def __repr__(self) -> str:
        """String representation of Level."""
        return f"<Level(id={getattr(self, 'id', None)}, subject_id={getattr(self, 'subject_id', None)}, name={getattr(self, 'name', None)})>"


# Import Subject and Test here to avoid circular imports
from app.models.subject import Subject  # noqa: E402, F401
from app.models.test import Test  # noqa: E402, F401
