#!/usr/bin/env python3
"""
Test script to verify that question creation with 5 options (A-E) works correctly.
This test verifies that the 422 error for options beyond D has been fixed.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.services.password_service import PasswordService
from app.repositories.subject_repository import SubjectRepository
from app.repositories.level_repository import LevelRepository
from app.repositories.test_repository import TestRepository
from app.services.subject_service import SubjectService
from app.services.level_service import LevelService
from app.services.test_service import TestService


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


async def setup_test_environment():
    """Set up the test environment with database and admin user."""
    print("Setting up test environment...")
    
    # Create test database
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async def override_get_db():
        async with async_session() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Create admin user
    async with async_session() as session:
        password_service = PasswordService()
        admin_user = User(
            email="admin@example.com",
            hashed_password=password_service.hash_password("adminpass123"),
            is_verified=True,
            is_admin=True
        )
        session.add(admin_user)
        await session.commit()
        await session.refresh(admin_user)
        print(f"Created admin user: {admin_user.email}")
    
    return async_session, admin_user


async def create_test_data(session_factory):
    """Create test subject, level, and test for question creation."""
    print("Creating test data (subject, level, test)...")
    
    async with session_factory() as session:
        # Create repositories and services
        subject_repo = SubjectRepository(session)
        level_repo = LevelRepository(session)
        test_repo = TestRepository(session)
        
        subject_service = SubjectService(subject_repo)
        level_service = LevelService(level_repo, subject_repo)
        test_service = TestService(test_repo, level_repo)
        
        # Create test data
        subject = await subject_service.create_subject("Mathematics")
        await session.commit()
        await session.refresh(subject)
        print(f"Created subject: {subject.name} (ID: {subject.id})")
        
        level = await level_service.create_level(subject.id, "Grade 5")
        await session.commit()
        await session.refresh(level)
        print(f"Created level: {level.name} (ID: {level.id})")
        
        test = await test_service.create_test(level.id, "5-Option Question Test")
        await session.commit()
        await session.refresh(test)
        print(f"Created test: {test.name} (ID: {test.id})")
        
        return test.id


async def login_admin(client: AsyncClient):
    """Login as admin and return the session cookie."""
    print("Logging in as admin...")
    
    login_data = {
        "email": "admin@example.com",
        "password": "adminpass123"
    }
    
    response = await client.post("/api/auth/login", json=login_data)
    print(f"Login response status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return None
    
    print("Login successful!")
    return response.cookies


async def test_question_creation_5_options(client: AsyncClient, test_id: int, cookies):
    """Test creating a question with 5 options (A-E)."""
    print(f"\nTesting question creation with 5 options for test ID: {test_id}")
    
    # Prepare the question data with 5 options (A-E)
    question_data = {
        "text": "What is the capital of France?",
        "correct_answer": "B",
        "options": [
            {"label": "A", "text": "London"},
            {"label": "B", "text": "Paris"},
            {"label": "C", "text": "Berlin"},
            {"label": "D", "text": "Madrid"},
            {"label": "E", "text": "Rome"}
        ]
    }
    
    print("Question data:")
    print(json.dumps(question_data, indent=2))
    
    # Make the POST request
    url = f"/api/admin/tests/{test_id}/questions"
    print(f"\nMaking POST request to: {url}")
    
    response = await client.post(
        url,
        json=question_data,
        cookies=cookies
    )
    
    print(f"Response status code: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    
    if response.status_code == 200 or response.status_code == 201:
        print("✅ SUCCESS: Question with 5 options created successfully!")
        response_data = response.json()
        print("Response data:")
        print(json.dumps(response_data, indent=2))
        
        # Verify the response contains all 5 options
        if "options" in response_data and len(response_data["options"]) == 5:
            print("✅ All 5 options are present in the response")
            for option in response_data["options"]:
                print(f"   - {option['label']}: {option['text']}")
        else:
            print("❌ Response doesn't contain all 5 options")
        
        return True
    else:
        print(f"❌ FAILED: Question creation failed with status {response.status_code}")
        try:
            error_data = response.json()
            print("Error response:")
            print(json.dumps(error_data, indent=2))
        except:
            print(f"Error response text: {response.text}")
        
        return False


async def test_question_creation_4_options(client: AsyncClient, test_id: int, cookies):
    """Test creating a question with 4 options (A-D) as a control test."""
    print(f"\nTesting question creation with 4 options (control test) for test ID: {test_id}")
    
    # Prepare the question data with 4 options (A-D)
    question_data = {
        "text": "What is 2 + 2?",
        "correct_answer": "A",
        "options": [
            {"label": "A", "text": "4"},
            {"label": "B", "text": "5"},
            {"label": "C", "text": "3"},
            {"label": "D", "text": "6"}
        ]
    }
    
    print("Question data:")
    print(json.dumps(question_data, indent=2))
    
    # Make the POST request
    url = f"/api/admin/tests/{test_id}/questions"
    print(f"\nMaking POST request to: {url}")
    
    response = await client.post(
        url,
        json=question_data,
        cookies=cookies
    )
    
    print(f"Response status code: {response.status_code}")
    
    if response.status_code == 200 or response.status_code == 201:
        print("✅ SUCCESS: Question with 4 options created successfully!")
        return True
    else:
        print(f"❌ FAILED: Question creation failed with status {response.status_code}")
        try:
            error_data = response.json()
            print("Error response:")
            print(json.dumps(error_data, indent=2))
        except:
            print(f"Error response text: {response.text}")
        
        return False


async def main():
    """Main test function."""
    print("🧪 Testing Question Creation with 5 Options (A-E)")
    print("=" * 60)
    
    try:
        # Setup test environment
        session_factory, admin_user = await setup_test_environment()
        
        # Create test data
        test_id = await create_test_data(session_factory)
        
        # Create test client
        from httpx import ASGITransport
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Login as admin
            cookies = await login_admin(client)
            if not cookies:
                print("❌ Failed to login as admin")
                return False
            
            # Test 4 options (control test)
            success_4_options = await test_question_creation_4_options(client, test_id, cookies)
            
            # Test 5 options (main test)
            success_5_options = await test_question_creation_5_options(client, test_id, cookies)
            
            print("\n" + "=" * 60)
            print("📊 TEST RESULTS:")
            print(f"4 options (A-D): {'✅ PASS' if success_4_options else '❌ FAIL'}")
            print(f"5 options (A-E): {'✅ PASS' if success_5_options else '❌ FAIL'}")
            
            if success_5_options:
                print("\n🎉 The 422 error for options beyond D has been FIXED!")
                print("The system now correctly accepts questions with 5 options (A-E).")
            else:
                print("\n⚠️  The 422 error still exists or there's another issue.")
                print("The system is not accepting questions with 5 options (A-E).")
            
            return success_5_options
    
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)