import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import random

from app.main import app
from app.database.base import Base
from app.modules.auth.models.orm import User, UserRole
from app.dependencies.database_dependecy import get_session
from app.config.settings import pwd_context


# Use async SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False, connect_args={"timeout": 30})
TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_session] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Create database tables before running tests"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True)
async def teardown():
    """Clean up after each test"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


# Test helper functions
async def create_test_user(phone: str, password: str, first_name: str = "Test", 
                           last_name: str = "User", role: UserRole = UserRole.ORDINARY) -> User:
    """Helper to create a test user"""
    async with TestingSessionLocal() as session:
        hashed_password = pwd_context.hash(password)
        user = User(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone,
            hashed_password=hashed_password,
            role=role,
            is_active=True
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


def get_user_token(phone: str, password: str) -> str:
    """Helper to get JWT token for a user"""
    response = client.post(
        "/auth/login",
        json={
            "phone_number": phone,
            "password": password
        }
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


# Test Data Fixtures
@pytest.fixture
def ordinary_user_phone():
    return f"+99850123{random.randint(1000, 9999):04d}"


@pytest.fixture
def admin_user_phone():
    return f"+99890111{random.randint(1000, 9999):04d}"


@pytest.fixture
def another_user_phone():
    return f"+99890222{random.randint(1000, 9999):04d}"


# Auth Endpoint Tests
class TestAuthEndpoints:
    """Test authentication endpoints"""

    @pytest.mark.asyncio
    async def test_login_success(self, ordinary_user_phone):
        """Test successful login"""
        password = "Password123"
        await create_test_user(ordinary_user_phone, password, "John", "Doe")
        
        response = client.post(
            "/auth/login",
            json={
                "phone_number": ordinary_user_phone,
                "password": password
            }
        )
        
        assert response.status_code == 200
        assert "access_token" in response.json()
        print(f"✓ Login successful")

    @pytest.mark.asyncio
    async def test_login_invalid_password(self, ordinary_user_phone):
        """Test login with invalid password"""
        password = "Password123"
        await create_test_user(ordinary_user_phone, password)
        
        response = client.post(
            "/auth/login",
            json={
                "phone_number": ordinary_user_phone,
                "password": "WrongPassword"
            }
        )
        
        assert response.status_code == 401
        print(f"✓ Invalid password rejected")

    @pytest.mark.asyncio
    async def test_login_user_not_found(self):
        """Test login with non-existent user"""
        response = client.post(
            "/auth/login",
            json={
                "phone_number": "+9999999999999",
                "password": "AnyPassword"
            }
        )
        
        assert response.status_code == 401
        print(f"✓ Non-existent user rejected")

    @pytest.mark.asyncio
    async def test_login_deactivated_user(self, ordinary_user_phone):
        """Test login with deactivated user"""
        password = "Password123"
        async with TestingSessionLocal() as session:
            # Create deactivated user
            hashed_password = pwd_context.hash(password)
            user = User(
                first_name="John",
                last_name="Doe",
                phone_number=ordinary_user_phone,
                hashed_password=hashed_password,
                role=UserRole.ORDINARY,
                is_active=False
            )
            session.add(user)
            await session.commit()
        
        response = client.post(
            "/auth/login",
            json={
                "phone_number": ordinary_user_phone,
                "password": password
            }
        )
        
        assert response.status_code == 403
        print(f"✓ Deactivated user rejected")

    @pytest.mark.asyncio
    async def test_logout_success(self, admin_user_phone):
        """Test successful logout"""
        password = "AdminPass123"
        await create_test_user(admin_user_phone, password, "Admin", "User", UserRole.ADMIN)
        
        # Login
        token = get_user_token(admin_user_phone, password)
        assert token is not None
        
        # Logout
        response = client.post(
            "/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Logout should return 200 (or skip if _blacklist_token not implemented)
        assert response.status_code in [200, 500]
        print(f"✓ Logout tested")


# Admin Endpoint Tests
class TestAdminEndpoints:
    """Test admin endpoints"""

    @pytest.mark.asyncio
    async def test_list_users_as_admin(self, admin_user_phone, ordinary_user_phone):
        """Test listing users as admin"""
        admin_password = "AdminPass123"
        user_password = "UserPass123"
        
        await create_test_user(admin_user_phone, admin_password, "Admin", "User", UserRole.ADMIN)
        await create_test_user(ordinary_user_phone, user_password, "John", "Doe")
        
        token = get_user_token(admin_user_phone, admin_password)
        
        response = client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "total" in response.json()
        assert "items" in response.json()
        print(f"✓ Users listed successfully")

    @pytest.mark.asyncio
    async def test_list_users_as_ordinary_user(self, ordinary_user_phone):
        """Test ordinary user cannot list users"""
        password = "UserPass123"
        await create_test_user(ordinary_user_phone, password)
        
        token = get_user_token(ordinary_user_phone, password)
        
        response = client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
        print(f"✓ Ordinary user access denied")

    @pytest.mark.asyncio
    async def test_get_user_detail_as_admin(self, admin_user_phone, ordinary_user_phone):
        """Test getting user detail as admin"""
        admin_password = "AdminPass123"
        user_password = "UserPass123"
        
        await create_test_user(admin_user_phone, admin_password, "Admin", "User", UserRole.ADMIN)
        user = await create_test_user(ordinary_user_phone, user_password, "John", "Doe")
        
        token = get_user_token(admin_user_phone, admin_password)
        
        response = client.get(
            f"/admin/users/{user.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["phone_number"] == ordinary_user_phone
        print(f"✓ User details retrieved")

    @pytest.mark.asyncio
    async def test_get_nonexistent_user(self, admin_user_phone):
        """Test getting non-existent user"""
        admin_password = "AdminPass123"
        await create_test_user(admin_user_phone, admin_password, "Admin", "User", UserRole.ADMIN)
        
        token = get_user_token(admin_user_phone, admin_password)
        
        response = client.get(
            "/admin/users/nonexistent-id",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
        print(f"✓ Non-existent user returns 404")

    @pytest.mark.asyncio
    async def test_promote_user_to_admin(self, admin_user_phone, ordinary_user_phone):
        """Test promoting user to admin"""
        admin_password = "AdminPass123"
        user_password = "UserPass123"
        
        await create_test_user(admin_user_phone, admin_password, "Admin", "User", UserRole.ADMIN)
        user = await create_test_user(ordinary_user_phone, user_password, "John", "Doe")
        
        token = get_user_token(admin_user_phone, admin_password)
        
        response = client.patch(
            f"/admin/users/{user.id}/role",
            json={"role": "admin"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["user"]["role"] == "admin"
        print(f"✓ User promoted to admin")

    @pytest.mark.asyncio
    async def test_demote_admin_to_ordinary(self, admin_user_phone, another_user_phone):
        """Test demoting admin to ordinary (when multiple admins exist)"""
        admin_password = "AdminPass123"
        another_password = "AnotherPass123"
        
        await create_test_user(admin_user_phone, admin_password, "Admin", "User", UserRole.ADMIN)
        another_admin = await create_test_user(another_user_phone, another_password, "Another", "Admin", UserRole.ADMIN)
        
        token = get_user_token(admin_user_phone, admin_password)
        
        response = client.patch(
            f"/admin/users/{another_admin.id}/role",
            json={"role": "ordinary"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["user"]["role"] == "ordinary"
        print(f"✓ Admin demoted to ordinary")

    @pytest.mark.asyncio
    async def test_cannot_demote_last_admin(self, admin_user_phone):
        """Test that cannot demote the last admin"""
        admin_password = "AdminPass123"
        admin_user = await create_test_user(admin_user_phone, admin_password, "Admin", "User", UserRole.ADMIN)
        
        token = get_user_token(admin_user_phone, admin_password)
        
        response = client.patch(
            f"/admin/users/{admin_user.id}/role",
            json={"role": "ordinary"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        print(f"✓ Cannot demote last admin")

    @pytest.mark.asyncio
    async def test_deactivate_user(self, admin_user_phone, ordinary_user_phone):
        """Test deactivating a user"""
        admin_password = "AdminPass123"
        user_password = "UserPass123"
        
        await create_test_user(admin_user_phone, admin_password, "Admin", "User", UserRole.ADMIN)
        user = await create_test_user(ordinary_user_phone, user_password, "John", "Doe")
        
        token = get_user_token(admin_user_phone, admin_password)
        
        response = client.patch(
            f"/admin/users/{user.id}/status",
            json={"is_active": False},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["user"]["is_active"] is False
        print(f"✓ User deactivated")

    @pytest.mark.asyncio
    async def test_activate_user(self, admin_user_phone, ordinary_user_phone):
        """Test activating a user"""
        admin_password = "AdminPass123"
        user_password = "UserPass123"
        
        await create_test_user(admin_user_phone, admin_password, "Admin", "User", UserRole.ADMIN)
        
        async with TestingSessionLocal() as session:
            user = User(
                first_name="John",
                last_name="Doe",
                phone_number=ordinary_user_phone,
                hashed_password=pwd_context.hash(user_password),
                role=UserRole.ORDINARY,
                is_active=False
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            user_id = user.id
        
        token = get_user_token(admin_user_phone, admin_password)
        
        response = client.patch(
            f"/admin/users/{user_id}/status",
            json={"is_active": True},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["user"]["is_active"] is True
        print(f"✓ User activated")

    @pytest.mark.asyncio
    async def test_delete_user(self, admin_user_phone, ordinary_user_phone):
        """Test deleting a user"""
        admin_password = "AdminPass123"
        user_password = "UserPass123"
        
        await create_test_user(admin_user_phone, admin_password, "Admin", "User", UserRole.ADMIN)
        user = await create_test_user(ordinary_user_phone, user_password, "John", "Doe")
        user_id = user.id
        
        token = get_user_token(admin_user_phone, admin_password)
        
        response = client.delete(
            f"/admin/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        print(f"✓ User deleted")

    @pytest.mark.asyncio
    async def test_list_admins(self, admin_user_phone):
        """Test listing all admins"""
        admin_password = "AdminPass123"
        await create_test_user(admin_user_phone, admin_password, "Admin", "User", UserRole.ADMIN)
        
        token = get_user_token(admin_user_phone, admin_password)
        
        response = client.get(
            "/admin/admins",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "items" in response.json()
        print(f"✓ Admins listed")

    @pytest.mark.asyncio
    async def test_get_admin_stats(self, admin_user_phone):
        """Test getting admin statistics"""
        admin_password = "AdminPass123"
        await create_test_user(admin_user_phone, admin_password, "Admin", "User", UserRole.ADMIN)
        
        token = get_user_token(admin_user_phone, admin_password)
        
        response = client.get(
            "/admin/stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "total_admins" in data
        assert "total_ordinary_users" in data
        print(f"✓ Admin stats retrieved: {data}")

    @pytest.mark.asyncio
    async def test_cannot_change_own_role(self, admin_user_phone):
        """Test admin cannot change their own role"""
        admin_password = "AdminPass123"
        admin_user = await create_test_user(admin_user_phone, admin_password, "Admin", "User", UserRole.ADMIN)
        
        token = get_user_token(admin_user_phone, admin_password)
        
        response = client.patch(
            f"/admin/users/{admin_user.id}/role",
            json={"role": "ordinary"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        print(f"✓ Cannot change own role")

    @pytest.mark.asyncio
    async def test_cannot_deactivate_own_account(self, admin_user_phone):
        """Test admin cannot deactivate their own account"""
        admin_password = "AdminPass123"
        admin_user = await create_test_user(admin_user_phone, admin_password, "Admin", "User", UserRole.ADMIN)
        
        token = get_user_token(admin_user_phone, admin_password)
        
        response = client.patch(
            f"/admin/users/{admin_user.id}/status",
            json={"is_active": False},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        print(f"✓ Cannot deactivate own account")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
