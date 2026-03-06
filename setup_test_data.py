#!/usr/bin/env python3
"""
Setup script to create test data for the question creation test.
Creates a subject, level, and test with ID 2 for testing.
"""

import asyncio
import sys
from sqlalchemy.exc import IntegrityError

from app.database import AsyncSessionLocal
from app.repositories.subject_repository import SubjectRepository
from app.repositories.level_repository import LevelRepository
from app.repositories.test_repository import TestRepository
from app.services.subject_service import SubjectService
from app.services.level_service import LevelService
from app.services.test_service import TestService


async def create_test_data():
    """Create test data for question creation testing."""
    try:
        async with AsyncSessionLocal() as session:
            # Create repositories and services
            subject_repo = SubjectRepository(session)
            level_repo = LevelRepository(session)
            test_repo = TestRepository(session)
            
            subject_service = SubjectService(subject_repo)
            level_service = LevelService(level_repo, subject_repo)
            test_service = TestService(test_repo, level_repo)
            
            # Check if test with ID 2 already exists
            existing_test = await test_repo.get_by_id(2)
            if existing_test:
                print(f"✓ Test with ID 2 already exists: {existing_test.name}")
                return True
            
            # Create or get subject
            try:
                subject = await subject_service.create_subject("Test Subject")
                await session.commit()
                await session.refresh(subject)
                print(f"✓ Created subject: {subject.name} (ID: {subject.id})")
            except IntegrityError:
                # Subject might already exist, get it
                await session.rollback()
                from sqlalchemy import select
                from app.models.subject import Subject
                stmt = select(Subject).where(Subject.name == "Test Subject")
                result = await session.execute(stmt)
                subject = result.scalar_one()
                print(f"✓ Using existing subject: {subject.name} (ID: {subject.id})")
            
            # Create or get level
            try:
                level = await level_service.create_level(subject.id, "Test Level")
                await session.commit()
                await session.refresh(level)
                print(f"✓ Created level: {level.name} (ID: {level.id})")
            except IntegrityError:
                # Level might already exist, get it
                await session.rollback()
                from sqlalchemy import select
                from app.models.level import Level
                stmt = select(Level).where(Level.name == "Test Level", Level.subject_id == subject.id)
                result = await session.execute(stmt)
                level = result.scalar_one()
                print(f"✓ Using existing level: {level.name} (ID: {level.id})")
            
            # Create test
            test = await test_service.create_test(level.id, "5-Option Question Test")
            await session.commit()
            await session.refresh(test)
            print(f"✓ Created test: {test.name} (ID: {test.id})")
            
            return True
            
    except Exception as e:
        print(f"✗ Error creating test data: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main entry point."""
    print("Creating test data for question creation testing...")
    success = await create_test_data()
    if success:
        print("✓ Test data setup completed successfully")
    else:
        print("✗ Test data setup failed")
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())