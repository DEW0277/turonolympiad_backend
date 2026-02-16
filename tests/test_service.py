import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.modules.auth.models.orm import User, UserRole
from app.modules.auth.repository.auth_repository import AuthRepository
from app.modules.auth.service.auth_service import AuthService
from app.modules.auth.service.otp_service import OtpService
from app.modules.redis import redis_service


# Test database setup
DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture
async def engine():
    """Create test database engine"""
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(engine):
    """Create test database session"""
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture
async def auth_repository(db_session):
    """Create auth repository"""
    return AuthRepository(db_session)


@pytest.fixture
async def auth_service(db_session):
    """Create auth service"""
    return AuthService(db_session)


@pytest.fixture
async def otp_service_instance():
    """Create OTP service with in-memory mock Redis"""
    # In-memory mock Redis store
    redis_store = {}
    
    class MockRedis:
        async def get(self, key):
            value = redis_store.get(key)
            # Simulate Redis byte strings
            return value.encode() if value else None
        
        async def setex(self, key, ttl, value):
            redis_store[key] = str(value)
            return True
        
        async def set(self, key, value):
            redis_store[key] = str(value)
            return True
        
        async def delete(self, key):
            redis_store.pop(key, None)
            return 1
        
        async def ttl(self, key):
            # Return 60 if key exists (simulating cooldown), -2 if not
            return 60 if key in redis_store else -2
    
    mock_redis = MockRedis()
    return OtpService(mock_redis)


# Dummy data fixtures
@pytest.fixture
def dummy_user_data():
    """Dummy user data for registration"""
    return {
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+998501234567",
        "password": "SecurePassword123"
    }


@pytest.fixture
def dummy_admin_data():
    """Dummy admin user data"""
    return {
        "first_name": "Admin",
        "last_name": "User",
        "phone_number": "+998901234567",
        "password": "AdminPassword123"
    }


# Repository Tests
class TestAuthRepository:
    """Test AuthRepository methods"""

    @pytest.mark.asyncio
    async def test_create_user(self, auth_repository, dummy_user_data):
        """Test creating a user"""
        user = await auth_repository.create_user(
            phone_number=dummy_user_data["phone_number"],
            hashed_password="hashed_password_123",
            first_name=dummy_user_data["first_name"],
            last_name=dummy_user_data["last_name"]
        )
        
        assert user is not None
        assert user.phone_number == dummy_user_data["phone_number"]
        assert user.first_name == dummy_user_data["first_name"]
        assert user.role == UserRole.ORDINARY
        print(f"✓ User created: {user.id}")

    @pytest.mark.asyncio
    async def test_get_user_by_phone(self, auth_repository, dummy_user_data):
        """Test getting user by phone number"""
        # Create user first
        await auth_repository.create_user(
            phone_number=dummy_user_data["phone_number"],
            hashed_password="hashed_password_123",
            first_name=dummy_user_data["first_name"],
            last_name=dummy_user_data["last_name"]
        )
        
        # Get user
        user = await auth_repository.get_user_by_phone(dummy_user_data["phone_number"])
        
        assert user is not None
        assert user.phone_number == dummy_user_data["phone_number"]
        print(f"✓ User retrieved by phone: {user.phone_number}")

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, auth_repository, dummy_user_data):
        """Test getting user by ID"""
        # Create user first
        created_user = await auth_repository.create_user(
            phone_number=dummy_user_data["phone_number"],
            hashed_password="hashed_password_123",
            first_name=dummy_user_data["first_name"],
            last_name=dummy_user_data["last_name"]
        )
        
        # Get user by ID
        user = await auth_repository.get_user_by_id(created_user.id)
        
        assert user is not None
        assert user.id == created_user.id
        print(f"✓ User retrieved by ID: {user.id}")

    @pytest.mark.asyncio
    async def test_update_user_role(self, auth_repository, dummy_user_data):
        """Test updating user role"""
        # Create user
        user = await auth_repository.create_user(
            phone_number=dummy_user_data["phone_number"],
            hashed_password="hashed_password_123",
            first_name=dummy_user_data["first_name"],
            last_name=dummy_user_data["last_name"]
        )
        
        # Update role to admin
        updated_user = await auth_repository.update_user_role(user.id, UserRole.ADMIN)
        
        assert updated_user.role == UserRole.ADMIN
        print(f"✓ User role updated to: {updated_user.role.value}")

    @pytest.mark.asyncio
    async def test_update_user_status(self, auth_repository, dummy_user_data):
        """Test updating user status"""
        # Create user
        user = await auth_repository.create_user(
            phone_number=dummy_user_data["phone_number"],
            hashed_password="hashed_password_123",
            first_name=dummy_user_data["first_name"],
            last_name=dummy_user_data["last_name"]
        )
        
        # Deactivate user
        updated_user = await auth_repository.update_user_status(user.id, False)
        
        assert updated_user.is_active is False
        print(f"✓ User status updated to: {updated_user.is_active}")

    @pytest.mark.asyncio
    async def test_delete_user(self, auth_repository, dummy_user_data):
        """Test deleting a user"""
        # Create user
        user = await auth_repository.create_user(
            phone_number=dummy_user_data["phone_number"],
            hashed_password="hashed_password_123",
            first_name=dummy_user_data["first_name"],
            last_name=dummy_user_data["last_name"]
        )
        
        # Delete user
        deleted = await auth_repository.delete_user(user.id)
        
        assert deleted is True
        
        # Verify user is deleted
        retrieved_user = await auth_repository.get_user_by_id(user.id)
        assert retrieved_user is None
        print(f"✓ User deleted successfully")

    @pytest.mark.asyncio
    async def test_get_all_users(self, auth_repository, dummy_user_data):
        """Test getting all users with pagination"""
        # Create multiple users
        for i in range(5):
            await auth_repository.create_user(
                phone_number=f"+998501234{i:03d}",
                hashed_password="hashed_password_123",
                first_name=f"User{i}",
                last_name="Test"
            )
        
        # Get all users
        result = await auth_repository.get_all_users(skip=0, limit=10)
        
        assert result["total"] == 5
        assert len(result["items"]) == 5
        print(f"✓ Retrieved {result['total']} users")

    @pytest.mark.asyncio
    async def test_get_admins(self, auth_repository, dummy_user_data, dummy_admin_data):
        """Test getting all admin users"""
        # Create ordinary user
        user1 = await auth_repository.create_user(
            phone_number=dummy_user_data["phone_number"],
            hashed_password="hashed_password_123",
            first_name=dummy_user_data["first_name"],
            last_name=dummy_user_data["last_name"]
        )
        
        # Create admin user
        user2 = await auth_repository.create_user(
            phone_number=dummy_admin_data["phone_number"],
            hashed_password="hashed_password_123",
            first_name=dummy_admin_data["first_name"],
            last_name=dummy_admin_data["last_name"],
            role=UserRole.ADMIN
        )
        
        # Get admins
        admins = await auth_repository.get_admins()
        
        assert len(admins) == 1
        assert admins[0].role == UserRole.ADMIN
        print(f"✓ Retrieved {len(admins)} admin(s)")

    @pytest.mark.asyncio
    async def test_get_admin_count(self, auth_repository, dummy_user_data, dummy_admin_data):
        """Test getting admin count"""
        # Create users
        await auth_repository.create_user(
            phone_number=dummy_user_data["phone_number"],
            hashed_password="hashed_password_123",
            first_name=dummy_user_data["first_name"],
            last_name=dummy_user_data["last_name"]
        )
        
        await auth_repository.create_user(
            phone_number=dummy_admin_data["phone_number"],
            hashed_password="hashed_password_123",
            first_name=dummy_admin_data["first_name"],
            last_name=dummy_admin_data["last_name"],
            role=UserRole.ADMIN
        )
        
        # Get admin count
        count = await auth_repository.get_admin_count()
        
        assert count == 1
        print(f"✓ Admin count: {count}")


# OTP Service Tests
class TestOTPService:
    """Test OTP service methods"""

    @pytest.mark.asyncio
    async def test_create_otp(self, otp_service_instance):
        """Test creating OTP"""
        phone_number = "+998501234567"
        otp = await otp_service_instance.create_otp(phone_number)
        
        assert otp is not None
        assert len(otp) == 6
        assert otp.isdigit()
        print(f"✓ OTP created: {otp}")

    @pytest.mark.asyncio
    async def test_verify_otp_valid(self, otp_service_instance):
        """Test verifying valid OTP"""
        phone_number = "+998501234567"
        otp = await otp_service_instance.create_otp(phone_number)
        
        is_valid = await otp_service_instance.verify_otp(phone_number, otp)
        
        assert is_valid is True
        print(f"✓ Valid OTP verified")

    @pytest.mark.asyncio
    async def test_verify_otp_invalid(self, otp_service_instance):
        """Test verifying invalid OTP"""
        phone_number = "+998501234567"
        await otp_service_instance.create_otp(phone_number)
        
        is_valid = await otp_service_instance.verify_otp(phone_number, "000000")
        
        assert is_valid is False
        print(f"✓ Invalid OTP rejected")

    @pytest.mark.asyncio
    async def test_get_cooldown(self, otp_service_instance):
        """Test getting cooldown"""
        phone_number = "+998501234567"
        
        # Create OTP
        await otp_service_instance.create_otp(phone_number)
        
        # Get cooldown
        cooldown = await otp_service_instance.get_cooldown(phone_number)
        
        assert cooldown > 0
        assert cooldown <= 60
        print(f"✓ Cooldown: {cooldown} seconds")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
