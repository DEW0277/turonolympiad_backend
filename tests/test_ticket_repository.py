"""Tests for TicketRepository.

This module contains comprehensive tests for the TicketRepository class,
validating all database operations for ticket management.
"""

import pytest
import pytest_asyncio
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.user import User
from app.models.test import Test
from app.models.ticket import Ticket
from app.models.level import Level
from app.models.subject import Subject
from app.repositories.ticket_repository import TicketRepository
from app.services.password_service import PasswordService


@pytest_asyncio.fixture
async def ticket_repo(test_db):
    """Create a TicketRepository instance."""
    async with test_db() as session:
        yield TicketRepository(session)


@pytest_asyncio.fixture
async def test_user(test_db):
    """Create a test user."""
    async with test_db() as session:
        password_service = PasswordService()
        user = User(
            email="testuser@example.com",
            hashed_password=password_service.hash_password("password123"),
            is_verified=True,
            is_admin=False
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest_asyncio.fixture
async def test_subject(test_db):
    """Create a test subject."""
    async with test_db() as session:
        subject = Subject(name="Mathematics")
        session.add(subject)
        await session.commit()
        await session.refresh(subject)
        return subject


@pytest_asyncio.fixture
async def test_level(test_db, test_subject):
    """Create a test level."""
    async with test_db() as session:
        level = Level(
            subject_id=test_subject.id,
            name="Level 1"
        )
        session.add(level)
        await session.commit()
        await session.refresh(level)
        return level


@pytest_asyncio.fixture
async def test_test(test_db, test_level):
    """Create a test."""
    async with test_db() as session:
        test = Test(
            level_id=test_level.id,
            name_en="Test 1",
            name_ru="Тест 1",
            name_uz="Test 1",
            price=Decimal("50.00"),
            start_date=None,
            end_date=None
        )
        session.add(test)
        await session.commit()
        await session.refresh(test)
        return test


class TestTicketRepositoryCreate:
    """Tests for TicketRepository.create() method."""
    
    @pytest.mark.asyncio
    async def test_create_ticket_with_valid_data(self, test_db, test_user, test_test):
        """Test creating a ticket with valid data."""
        async with test_db() as session:
            repo = TicketRepository(session)
            
            ticket = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                payment_amount=Decimal("50.00"),
                payment_provider="payme",
                payment_transaction_id="txn_12345"
            )
            
            assert ticket.id is not None
            assert ticket.user_id == test_user.id
            assert ticket.test_id == test_test.id
            assert ticket.payment_amount == Decimal("50.00")
            assert ticket.payment_provider == "payme"
            assert ticket.payment_transaction_id == "txn_12345"
            assert ticket.purchased_at is not None
            assert ticket.created_at is not None
    
    @pytest.mark.asyncio
    async def test_create_ticket_with_click_provider(self, test_db, test_user, test_test):
        """Test creating a ticket with Click payment provider."""
        async with test_db() as session:
            repo = TicketRepository(session)
            
            ticket = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                payment_amount=Decimal("75.50"),
                payment_provider="click",
                payment_transaction_id="click_txn_67890"
            )
            
            assert ticket.payment_provider == "click"
            assert ticket.payment_amount == Decimal("75.50")
    
    @pytest.mark.asyncio
    async def test_create_ticket_with_zero_amount(self, test_db, test_user, test_test):
        """Test creating a ticket with zero payment amount."""
        async with test_db() as session:
            repo = TicketRepository(session)
            
            ticket = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                payment_amount=Decimal("0.00"),
                payment_provider="payme",
                payment_transaction_id="txn_free"
            )
            
            assert ticket.payment_amount == Decimal("0.00")
    
    @pytest.mark.asyncio
    async def test_create_ticket_with_large_amount(self, test_db, test_user, test_test):
        """Test creating a ticket with large payment amount."""
        async with test_db() as session:
            repo = TicketRepository(session)
            
            ticket = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                payment_amount=Decimal("9999999.99"),
                payment_provider="payme",
                payment_transaction_id="txn_large"
            )
            
            assert ticket.payment_amount == Decimal("9999999.99")
    
    @pytest.mark.asyncio
    async def test_create_ticket_timestamps_are_set(self, test_db, test_user, test_test):
        """Test that timestamps are automatically set on creation."""
        async with test_db() as session:
            repo = TicketRepository(session)
            before_create = datetime.now(timezone.utc)
            
            ticket = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                payment_amount=Decimal("50.00"),
                payment_provider="payme",
                payment_transaction_id="txn_timestamp"
            )
            
            after_create = datetime.now(timezone.utc)
            
            assert before_create <= ticket.purchased_at <= after_create
            assert before_create <= ticket.created_at <= after_create


class TestTicketRepositoryGetById:
    """Tests for TicketRepository.get_by_id() method."""
    
    @pytest.mark.asyncio
    async def test_get_ticket_by_id_success(self, test_db, test_user, test_test):
        """Test retrieving a ticket by ID."""
        async with test_db() as session:
            repo = TicketRepository(session)
            
            created_ticket = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                payment_amount=Decimal("50.00"),
                payment_provider="payme",
                payment_transaction_id="txn_get_by_id"
            )
            
            retrieved_ticket = await repo.get_by_id(created_ticket.id)
            
            assert retrieved_ticket is not None
            assert retrieved_ticket.id == created_ticket.id
            assert retrieved_ticket.user_id == test_user.id
            assert retrieved_ticket.test_id == test_test.id
    
    @pytest.mark.asyncio
    async def test_get_ticket_by_id_not_found(self, test_db):
        """Test retrieving a non-existent ticket."""
        async with test_db() as session:
            repo = TicketRepository(session)
            
            ticket = await repo.get_by_id(99999)
            
            assert ticket is None
    
    @pytest.mark.asyncio
    async def test_get_ticket_by_id_loads_relationships(self, test_db, test_user, test_test):
        """Test that get_by_id loads user and test relationships."""
        async with test_db() as session:
            repo = TicketRepository(session)
            
            created_ticket = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                payment_amount=Decimal("50.00"),
                payment_provider="payme",
                payment_transaction_id="txn_relationships"
            )
            
            retrieved_ticket = await repo.get_by_id(created_ticket.id)
            
            # Verify relationships are loaded
            assert retrieved_ticket.user is not None
            assert retrieved_ticket.user.id == test_user.id
            assert retrieved_ticket.test is not None
            assert retrieved_ticket.test.id == test_test.id


class TestTicketRepositoryGetUserTicketForTest:
    """Tests for TicketRepository.get_user_ticket_for_test() method."""
    
    @pytest.mark.asyncio
    async def test_get_user_ticket_for_test_success(self, test_db, test_user, test_test):
        """Test retrieving a user's ticket for a specific test."""
        async with test_db() as session:
            repo = TicketRepository(session)
            
            created_ticket = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                payment_amount=Decimal("50.00"),
                payment_provider="payme",
                payment_transaction_id="txn_user_test"
            )
            
            retrieved_ticket = await repo.get_user_ticket_for_test(test_user.id, test_test.id)
            
            assert retrieved_ticket is not None
            assert retrieved_ticket.id == created_ticket.id
            assert retrieved_ticket.user_id == test_user.id
            assert retrieved_ticket.test_id == test_test.id
    
    @pytest.mark.asyncio
    async def test_get_user_ticket_for_test_not_found(self, test_db, test_user, test_test):
        """Test retrieving a ticket that doesn't exist."""
        async with test_db() as session:
            repo = TicketRepository(session)
            
            ticket = await repo.get_user_ticket_for_test(test_user.id, test_test.id)
            
            assert ticket is None
    
    @pytest.mark.asyncio
    async def test_get_user_ticket_for_test_different_user(self, test_db, test_user, test_test):
        """Test that ticket for different user is not returned."""
        async with test_db() as session:
            repo = TicketRepository(session)
            
            # Create ticket for test_user
            await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                payment_amount=Decimal("50.00"),
                payment_provider="payme",
                payment_transaction_id="txn_user1"
            )
            
            # Create another user
            password_service = PasswordService()
            other_user = User(
                email="otheruser@example.com",
                hashed_password=password_service.hash_password("password123"),
                is_verified=True,
                is_admin=False
            )
            session.add(other_user)
            await session.commit()
            await session.refresh(other_user)
            
            # Try to get ticket for other user
            ticket = await repo.get_user_ticket_for_test(other_user.id, test_test.id)
            
            assert ticket is None
    
    @pytest.mark.asyncio
    async def test_get_user_ticket_for_test_different_test(self, test_db, test_user, test_test, test_level):
        """Test that ticket for different test is not returned."""
        async with test_db() as session:
            repo = TicketRepository(session)
            
            # Create ticket for test_test
            await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                payment_amount=Decimal("50.00"),
                payment_provider="payme",
                payment_transaction_id="txn_test1"
            )
            
            # Create another test
            other_test = Test(
                level_id=test_level.id,
                name_en="Test 2",
                name_ru="Тест 2",
                name_uz="Test 2",
                price=Decimal("60.00"),
                start_date=None,
                end_date=None
            )
            session.add(other_test)
            await session.commit()
            await session.refresh(other_test)
            
            # Try to get ticket for other test
            ticket = await repo.get_user_ticket_for_test(test_user.id, other_test.id)
            
            assert ticket is None


class TestTicketRepositoryGetUserTickets:
    """Tests for TicketRepository.get_user_tickets() method."""
    
    @pytest.mark.asyncio
    async def test_get_user_tickets_empty(self, test_db, test_user):
        """Test retrieving tickets for user with no tickets."""
        async with test_db() as session:
            repo = TicketRepository(session)
            
            tickets = await repo.get_user_tickets(test_user.id)
            
            assert tickets == []
    
    @pytest.mark.asyncio
    async def test_get_user_tickets_single(self, test_db, test_user, test_test):
        """Test retrieving a single ticket for user."""
        async with test_db() as session:
            repo = TicketRepository(session)
            
            created_ticket = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                payment_amount=Decimal("50.00"),
                payment_provider="payme",
                payment_transaction_id="txn_single"
            )
            
            tickets = await repo.get_user_tickets(test_user.id)
            
            assert len(tickets) == 1
            assert tickets[0].id == created_ticket.id
    
    @pytest.mark.asyncio
    async def test_get_user_tickets_multiple(self, test_db, test_user, test_test, test_level):
        """Test retrieving multiple tickets for user."""
        async with test_db() as session:
            repo = TicketRepository(session)
            
            # Create first ticket
            ticket1 = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                payment_amount=Decimal("50.00"),
                payment_provider="payme",
                payment_transaction_id="txn_multi_1"
            )
            
            # Create second test
            test2 = Test(
                level_id=test_level.id,
                name_en="Test 2",
                name_ru="Тест 2",
                name_uz="Test 2",
                price=Decimal("60.00"),
                start_date=None,
                end_date=None
            )
            session.add(test2)
            await session.commit()
            await session.refresh(test2)
            
            # Create second ticket
            ticket2 = await repo.create(
                user_id=test_user.id,
                test_id=test2.id,
                payment_amount=Decimal("60.00"),
                payment_provider="click",
                payment_transaction_id="txn_multi_2"
            )
            
            tickets = await repo.get_user_tickets(test_user.id)
            
            assert len(tickets) == 2
            ticket_ids = {t.id for t in tickets}
            assert ticket1.id in ticket_ids
            assert ticket2.id in ticket_ids
    
    @pytest.mark.asyncio
    async def test_get_user_tickets_pagination_skip(self, test_db, test_user, test_test, test_level):
        """Test pagination with skip parameter."""
        async with test_db() as session:
            repo = TicketRepository(session)
            
            # Create 3 tickets
            for i in range(3):
                await repo.create(
                    user_id=test_user.id,
                    test_id=test_test.id,
                    payment_amount=Decimal("50.00"),
                    payment_provider="payme",
                    payment_transaction_id=f"txn_skip_{i}"
                )
            
            # Get with skip=1
            tickets = await repo.get_user_tickets(test_user.id, skip=1, limit=100)
            
            assert len(tickets) == 2
    
    @pytest.mark.asyncio
    async def test_get_user_tickets_pagination_limit(self, test_db, test_user, test_test):
        """Test pagination with limit parameter."""
        async with test_db() as session:
            repo = TicketRepository(session)
            
            # Create 5 tickets
            for i in range(5):
                await repo.create(
                    user_id=test_user.id,
                    test_id=test_test.id,
                    payment_amount=Decimal("50.00"),
                    payment_provider="payme",
                    payment_transaction_id=f"txn_limit_{i}"
                )
            
            # Get with limit=2
            tickets = await repo.get_user_tickets(test_user.id, skip=0, limit=2)
            
            assert len(tickets) == 2
    
    @pytest.mark.asyncio
    async def test_get_user_tickets_ordered_by_purchased_at(self, test_db, test_user, test_test):
        """Test that tickets are ordered by purchased_at descending."""
        async with test_db() as session:
            repo = TicketRepository(session)
            
            # Create tickets
            ticket1 = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                payment_amount=Decimal("50.00"),
                payment_provider="payme",
                payment_transaction_id="txn_order_1"
            )
            
            ticket2 = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                payment_amount=Decimal("50.00"),
                payment_provider="payme",
                payment_transaction_id="txn_order_2"
            )
            
            tickets = await repo.get_user_tickets(test_user.id)
            
            # Most recent should be first
            assert tickets[0].id == ticket2.id
            assert tickets[1].id == ticket1.id
    
    @pytest.mark.asyncio
    async def test_get_user_tickets_loads_test_relationship(self, test_db, test_user, test_test):
        """Test that get_user_tickets loads test relationship."""
        async with test_db() as session:
            repo = TicketRepository(session)
            
            await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                payment_amount=Decimal("50.00"),
                payment_provider="payme",
                payment_transaction_id="txn_rel"
            )
            
            tickets = await repo.get_user_tickets(test_user.id)
            
            assert len(tickets) == 1
            assert tickets[0].test is not None
            assert tickets[0].test.id == test_test.id


class TestTicketRepositoryExistsByTransactionId:
    """Tests for TicketRepository.exists_by_transaction_id() method."""
    
    @pytest.mark.asyncio
    async def test_exists_by_transaction_id_true(self, test_db, test_user, test_test):
        """Test checking if ticket exists for transaction ID."""
        async with test_db() as session:
            repo = TicketRepository(session)
            
            await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                payment_amount=Decimal("50.00"),
                payment_provider="payme",
                payment_transaction_id="txn_exists"
            )
            
            exists = await repo.exists_by_transaction_id("txn_exists")
            
            assert exists is True
    
    @pytest.mark.asyncio
    async def test_exists_by_transaction_id_false(self, test_db):
        """Test checking if ticket exists for non-existent transaction ID."""
        async with test_db() as session:
            repo = TicketRepository(session)
            
            exists = await repo.exists_by_transaction_id("txn_nonexistent")
            
            assert exists is False
    
    @pytest.mark.asyncio
    async def test_exists_by_transaction_id_prevents_duplicates(self, test_db, test_user, test_test):
        """Test that transaction ID uniqueness prevents duplicates."""
        async with test_db() as session:
            repo = TicketRepository(session)
            
            # Create first ticket
            await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                payment_amount=Decimal("50.00"),
                payment_provider="payme",
                payment_transaction_id="txn_unique"
            )
            
            # Verify it exists
            exists = await repo.exists_by_transaction_id("txn_unique")
            assert exists is True
            
            # Try to create duplicate (should fail due to unique constraint)
            with pytest.raises(Exception):  # IntegrityError
                await repo.create(
                    user_id=test_user.id,
                    test_id=test_test.id,
                    payment_amount=Decimal("50.00"),
                    payment_provider="payme",
                    payment_transaction_id="txn_unique"
                )


class TestTicketRepositoryIntegration:
    """Integration tests for TicketRepository."""
    
    @pytest.mark.asyncio
    async def test_complete_ticket_workflow(self, test_db, test_user, test_test):
        """Test complete ticket workflow: create, retrieve, check existence."""
        async with test_db() as session:
            repo = TicketRepository(session)
            
            # Create ticket
            ticket = await repo.create(
                user_id=test_user.id,
                test_id=test_test.id,
                payment_amount=Decimal("50.00"),
                payment_provider="payme",
                payment_transaction_id="txn_workflow"
            )
            
            # Verify it exists by transaction ID
            assert await repo.exists_by_transaction_id("txn_workflow") is True
            
            # Retrieve by ID
            retrieved = await repo.get_by_id(ticket.id)
            assert retrieved is not None
            
            # Check user has ticket for test
            user_ticket = await repo.get_user_ticket_for_test(test_user.id, test_test.id)
            assert user_ticket is not None
            assert user_ticket.id == ticket.id
            
            # Get all user tickets
            all_tickets = await repo.get_user_tickets(test_user.id)
            assert len(all_tickets) == 1
            assert all_tickets[0].id == ticket.id
