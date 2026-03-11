"""Ticket database model.

This module defines the Ticket SQLAlchemy model for test access control.
"""

from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import String, DateTime, Integer, ForeignKey, Index, CheckConstraint, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Ticket(Base):
    """Ticket model for test access control.
    
    Represents a purchased ticket that grants a user access to solve a specific test.
    Each ticket is created after successful payment processing through payment providers
    (Payme, Click, or future providers like Visa Direct).
    
    Attributes:
        id: Primary key, auto-incrementing integer
        user_id: Foreign key to User, indexed for fast lookups
        test_id: Foreign key to Test, indexed for fast lookups
        payment_amount: Amount paid for ticket as decimal (10 digits, 2 decimal places)
        payment_provider: Payment provider used (payme, click, etc), indexed
        payment_transaction_id: Unique transaction identifier from payment provider
        purchased_at: Timestamp when ticket was purchased, indexed
        created_at: Timestamp when record was created
        user: Many-to-one relationship with User model
        test: Many-to-one relationship with Test model
    """
    
    __tablename__ = "tickets"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    test_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("tests.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    payment_amount: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2), 
        nullable=False
    )
    payment_provider: Mapped[str] = mapped_column(
        String(50), 
        nullable=False, 
        index=True
    )
    payment_transaction_id: Mapped[str] = mapped_column(
        String(255), 
        nullable=False, 
        unique=True, 
        index=True
    )
    purchased_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="tickets", lazy="select")
    test: Mapped["Test"] = relationship("Test", back_populates="tickets", lazy="select")
    
    # Constraints and Indexes
    __table_args__ = (
        Index("idx_ticket_user_test", "user_id", "test_id"),
        Index("idx_ticket_user_purchased", "user_id", "purchased_at"),
        Index("idx_ticket_transaction", "payment_transaction_id"),
        CheckConstraint("payment_amount >= 0", name="ck_ticket_amount_non_negative"),
    )
    
    def __repr__(self) -> str:
        """String representation of Ticket."""
        return f"<Ticket(id={getattr(self, 'id', None)}, user_id={getattr(self, 'user_id', None)}, test_id={getattr(self, 'test_id', None)}, payment_provider={getattr(self, 'payment_provider', None)})>"


# Import User and Test here to avoid circular imports
from app.models.user import User  # noqa: E402, F401
from app.models.test import Test  # noqa: E402, F401
