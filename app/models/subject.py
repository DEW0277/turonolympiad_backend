"""Subject database model.

This module defines the Subject SQLAlchemy model for organizing tests by academic discipline.
"""

from datetime import datetime
from sqlalchemy import String, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Subject(Base):
    """Subject model for organizing tests by academic discipline.
    
    Represents a top-level category such as Mathematics, Biology, or Physics.
    Subjects contain multiple Levels, which in turn contain Tests and Questions.
    
    Attributes:
        id: Primary key, auto-incrementing integer
        name: Unique subject name (1-100 characters), indexed for fast lookups
        created_at: Timestamp when subject was created
        updated_at: Timestamp when subject was last updated
        levels: One-to-many relationship with Level model (cascade delete)
    """
    
    __tablename__ = "subjects"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    levels: Mapped[list["Level"]] = relationship(
        "Level",
        back_populates="subject",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    def __repr__(self) -> str:
        """String representation of Subject."""
        return f"<Subject(id={getattr(self, 'id', None)}, name={getattr(self, 'name', None)})>"


# Import Level here to avoid circular imports
from app.models.level import Level  # noqa: E402, F401
