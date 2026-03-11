"""Database migration to add ticket-based test access system.

This migration adds two new tables:
1. tickets - Stores purchased tickets for test access control
2. test_solutions - Records user test submissions and results

Migration: Add tickets and test_solutions tables
- Creates tickets table with payment tracking and indexes
- Creates test_solutions table with solution data and scoring
- Adds foreign key relationships to users and tests tables
- Adds composite indexes for query optimization
- Adds check constraints for data validation
"""

import sqlite3
from pathlib import Path


def get_db_path() -> Path:
    """Get the database file path."""
    db_path = Path(__file__).parent.parent.parent / "quiz_auth.db"
    return db_path


def migration_up() -> None:
    """Apply the migration: add tickets and test_solutions tables."""
    db_path = get_db_path()
    
    if not db_path.exists():
        raise FileNotFoundError(f"Database file not found at {db_path}")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        cursor.execute("BEGIN TRANSACTION")
        
        # Check if tickets table already exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='tickets'"
        )
        tickets_exists = cursor.fetchone() is not None
        
        # Check if test_solutions table already exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='test_solutions'"
        )
        test_solutions_exists = cursor.fetchone() is not None
        
        if tickets_exists and test_solutions_exists:
            print("✓ tickets and test_solutions tables already exist, no update needed")
            return
        
        print("Adding ticket-based test access system tables...")
        
        # Create tickets table
        if not tickets_exists:
            print("Creating tickets table...")
            cursor.execute("""
                CREATE TABLE tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    test_id INTEGER NOT NULL,
                    payment_amount REAL NOT NULL,
                    payment_provider VARCHAR(50) NOT NULL,
                    payment_transaction_id VARCHAR(255) NOT NULL UNIQUE,
                    purchased_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE,
                    CONSTRAINT ck_ticket_amount_non_negative CHECK (payment_amount >= 0)
                )
            """)
            print("✓ Created tickets table")
            
            # Create indexes for tickets table
            cursor.execute("CREATE INDEX idx_ticket_user_id ON tickets(user_id)")
            cursor.execute("CREATE INDEX idx_ticket_test_id ON tickets(test_id)")
            cursor.execute("CREATE INDEX idx_ticket_payment_provider ON tickets(payment_provider)")
            cursor.execute("CREATE INDEX idx_ticket_transaction ON tickets(payment_transaction_id)")
            cursor.execute("CREATE INDEX idx_ticket_purchased_at ON tickets(purchased_at)")
            cursor.execute("CREATE INDEX idx_ticket_user_test ON tickets(user_id, test_id)")
            cursor.execute("CREATE INDEX idx_ticket_user_purchased ON tickets(user_id, purchased_at)")
            print("✓ Created indexes for tickets table")
        else:
            print("✓ tickets table already exists, skipping")
        
        # Create test_solutions table
        if not test_solutions_exists:
            print("Creating test_solutions table...")
            cursor.execute("""
                CREATE TABLE test_solutions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    test_id INTEGER NOT NULL,
                    solution_data TEXT NOT NULL,
                    score REAL,
                    submitted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE,
                    CONSTRAINT ck_solution_score_range CHECK (score IS NULL OR (score >= 0 AND score <= 100))
                )
            """)
            print("✓ Created test_solutions table")
            
            # Create indexes for test_solutions table
            cursor.execute("CREATE INDEX idx_solution_user_id ON test_solutions(user_id)")
            cursor.execute("CREATE INDEX idx_solution_test_id ON test_solutions(test_id)")
            cursor.execute("CREATE INDEX idx_solution_submitted_at ON test_solutions(submitted_at)")
            cursor.execute("CREATE INDEX idx_solution_user_test ON test_solutions(user_id, test_id)")
            cursor.execute("CREATE INDEX idx_solution_user_submitted ON test_solutions(user_id, submitted_at)")
            cursor.execute("CREATE INDEX idx_solution_test_submitted ON test_solutions(test_id, submitted_at)")
            print("✓ Created indexes for test_solutions table")
        else:
            print("✓ test_solutions table already exists, skipping")
        
        # Verify the migration
        print("\nVerifying migration...")
        
        # Verify tickets table
        cursor.execute("PRAGMA table_info(tickets)")
        tickets_columns = {row[1]: row for row in cursor.fetchall()}
        
        required_tickets_columns = [
            "id", "user_id", "test_id", "payment_amount", 
            "payment_provider", "payment_transaction_id", 
            "purchased_at", "created_at"
        ]
        
        for col in required_tickets_columns:
            if col not in tickets_columns:
                raise Exception(f"Migration verification failed: tickets.{col} column not found")
        
        print("✓ Verified tickets table structure")
        
        # Verify test_solutions table
        cursor.execute("PRAGMA table_info(test_solutions)")
        solutions_columns = {row[1]: row for row in cursor.fetchall()}
        
        required_solutions_columns = [
            "id", "user_id", "test_id", "solution_data", 
            "score", "submitted_at", "created_at"
        ]
        
        for col in required_solutions_columns:
            if col not in solutions_columns:
                raise Exception(f"Migration verification failed: test_solutions.{col} column not found")
        
        print("✓ Verified test_solutions table structure")
        
        # Verify check constraints
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='tickets'")
        tickets_sql = cursor.fetchone()[0]
        if "ck_ticket_amount_non_negative" not in tickets_sql:
            raise Exception("Migration verification failed: tickets check constraint not found")
        
        print("✓ Verified tickets check constraint")
        
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='test_solutions'")
        solutions_sql = cursor.fetchone()[0]
        if "ck_solution_score_range" not in solutions_sql:
            raise Exception("Migration verification failed: test_solutions check constraint not found")
        
        print("✓ Verified test_solutions check constraint")
        
        # Verify indexes
        cursor.execute("PRAGMA index_list(tickets)")
        tickets_indexes = [row[1] for row in cursor.fetchall()]
        
        required_tickets_indexes = [
            "idx_ticket_user_test", "idx_ticket_user_purchased", 
            "idx_ticket_transaction"
        ]
        
        for idx in required_tickets_indexes:
            if idx not in tickets_indexes:
                raise Exception(f"Migration verification failed: {idx} index not found")
        
        print("✓ Verified tickets indexes")
        
        cursor.execute("PRAGMA index_list(test_solutions)")
        solutions_indexes = [row[1] for row in cursor.fetchall()]
        
        required_solutions_indexes = [
            "idx_solution_user_test", "idx_solution_user_submitted", 
            "idx_solution_test_submitted"
        ]
        
        for idx in required_solutions_indexes:
            if idx not in solutions_indexes:
                raise Exception(f"Migration verification failed: {idx} index not found")
        
        print("✓ Verified test_solutions indexes")
        
        conn.commit()
        print("\n✓ Migration completed successfully")
        print("Ticket-based test access system tables created with all indexes and constraints")
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ Migration failed: {e}")
        raise
    finally:
        conn.close()


def migration_down() -> None:
    """Rollback the migration: remove tickets and test_solutions tables."""
    db_path = get_db_path()
    
    if not db_path.exists():
        raise FileNotFoundError(f"Database file not found at {db_path}")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        cursor.execute("BEGIN TRANSACTION")
        
        # Check if tables exist
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='tickets'"
        )
        tickets_exists = cursor.fetchone() is not None
        
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='test_solutions'"
        )
        test_solutions_exists = cursor.fetchone() is not None
        
        if not tickets_exists and not test_solutions_exists:
            print("✓ tickets and test_solutions tables don't exist, nothing to rollback")
            return
        
        print("Rolling back ticket-based test access system tables...")
        
        # Drop test_solutions table (drop dependent tables first)
        if test_solutions_exists:
            cursor.execute("DROP TABLE test_solutions")
            print("✓ Dropped test_solutions table")
        
        # Drop tickets table
        if tickets_exists:
            cursor.execute("DROP TABLE tickets")
            print("✓ Dropped tickets table")
        
        # Verify rollback
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('tickets', 'test_solutions')"
        )
        remaining_tables = cursor.fetchall()
        
        if remaining_tables:
            raise Exception(f"Rollback verification failed: tables still exist: {remaining_tables}")
        
        print("✓ Verified tables removed")
        
        conn.commit()
        print("\n✓ Rollback completed successfully")
        print("Ticket-based test access system tables removed")
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ Rollback failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "down":
        migration_down()
    else:
        migration_up()
