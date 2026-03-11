"""Ticket repository for database operations.

This module provides the TicketRepository class for managing ticket data persistence,
implementing all database operations for the Ticket model with optimized queries.
"""

from typing import Optional, List
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ticket import Ticket
from app.models.user import User
from app.models.test import Test
from app.repositories.base import BaseRepository


class TicketRepository(BaseRepository[Ticket]):
    """Repository for Ticket model database operations.
    
    Handles all database operations for ticket records including creation,
    retrieval, and validation. Uses async database operations and optimized
    queries with proper indexing for high concurrency support.
    
    Requirements:
        - 1.1: Ticket creation and management
        - 1.6: Ticket retrieval and validation
        - 3.1: Ticket ownership validation
        - 3.3: Indexed queries for access validation
        - 5.2: Duplicate prevention via transaction ID
        - 6.4: Transaction idempotency
        - 7.1: Query optimization with indexes
        - 7.3: Efficient pagination
    """
    
    __test__ = False  # Tell pytest this is not a test class
    
    def __init__(self, db: AsyncSession):
        """Initialize TicketRepository with database session.
        
        Args:
            db: Async database session for operations
        """
        super().__init__(Ticket, db)
    
    async def create(
        self,
        user_id: int,
        test_id: int,
        payment_amount: Decimal,
        payment_provider: str,
        payment_transaction_id: str
    ) -> Ticket:
        """Create a new ticket after successful payment.
        
        Creates a ticket record with all required fields. The ticket grants
        the user access to solve the specified test.
        
        Args:
            user_id: ID of the user purchasing the ticket
            test_id: ID of the test the ticket grants access to
            payment_amount: Amount paid for the ticket
            payment_provider: Payment provider used (payme, click, etc)
            payment_transaction_id: Unique transaction ID from payment provider
            
        Returns:
            Created Ticket instance with all fields populated
            
        Raises:
            IntegrityError: If transaction_id already exists (duplicate prevention)
        """
        return await super().create(
            user_id=user_id,
            test_id=test_id,
            payment_amount=payment_amount,
            payment_provider=payment_provider,
            payment_transaction_id=payment_transaction_id
        )
    
    async def get_by_id(self, ticket_id: int) -> Optional[Ticket]:
        """Retrieve ticket by ID with relationships.
        
        Fetches a ticket with eager-loaded user and test relationships
        to minimize database queries.
        
        Args:
            ticket_id: Ticket's primary key ID
            
        Returns:
            Ticket instance if found, None otherwise
        """
        result = await self.db.execute(
            select(Ticket)
            .options(
                selectinload(Ticket.user),
                selectinload(Ticket.test)
            )
            .where(Ticket.id == ticket_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_ticket_for_test(
        self,
        user_id: int,
        test_id: int
    ) -> Optional[Ticket]:
        """Check if user has a ticket for specific test.
        
        Uses the idx_ticket_user_test composite index for fast lookup.
        This is the primary query for access validation.
        
        Args:
            user_id: ID of the user
            test_id: ID of the test
            
        Returns:
            Ticket instance if user has ticket for test, None otherwise
        """
        result = await self.db.execute(
            select(Ticket)
            .where(
                (Ticket.user_id == user_id) & (Ticket.test_id == test_id)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_user_tickets(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Ticket]:
        """Retrieve all tickets for a user with pagination.
        
        Uses the idx_ticket_user_purchased composite index for efficient
        retrieval of user's ticket history ordered by purchase date.
        
        Args:
            user_id: ID of the user
            skip: Number of records to skip for pagination (default: 0)
            limit: Maximum number of records to return (default: 100)
            
        Returns:
            List of Ticket instances for the user, ordered by purchased_at descending
        """
        result = await self.db.execute(
            select(Ticket)
            .where(Ticket.user_id == user_id)
            .options(
                selectinload(Ticket.test)
            )
            .order_by(Ticket.purchased_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def exists_by_transaction_id(
        self,
        transaction_id: str
    ) -> bool:
        """Check if ticket exists for transaction (prevent duplicates).
        
        Uses the idx_ticket_transaction unique index for fast lookup.
        Prevents duplicate ticket creation for the same payment transaction.
        
        Args:
            transaction_id: Payment provider's transaction ID
            
        Returns:
            True if ticket exists for transaction, False otherwise
        """
        result = await self.db.execute(
            select(Ticket).where(Ticket.payment_transaction_id == transaction_id)
        )
        return result.scalar_one_or_none() is not None
