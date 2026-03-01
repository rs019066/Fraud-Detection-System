"""
Database Migration Script
==========================
Creates users table and seeds default admin user.

This script:
1. Creates users table if it doesn't exist
2. Seeds a default admin user (admin/admin123)
3. Is safe to run multiple times (idempotent)

Usage:
    python migrate_db.py

For production:
- Change default admin password immediately after first login
- Use proper migration tools like Alembic
"""

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from models.user import UserDB, Base as UserBase
from auth.jwt import hash_password

# Import main Base to ensure TransactionDB table is also created
from main import Base as MainBase


def create_tables(engine):
    """
    Create all database tables.

    Uses SQLAlchemy's create_all() which is idempotent - it won't
    recreate tables that already exist.
    """
    print("Creating database tables...")

    # Create all tables from both Base classes
    MainBase.metadata.create_all(bind=engine)
    UserBase.metadata.create_all(bind=engine)

    print("✅ Tables created successfully")


def seed_admin_user(session):
    """
    Create default admin user if it doesn't exist.

    Default credentials:
    - Username: admin
    - Password: admin123
    - Role: admin
    - Email: admin@fraud-detection.local

    WARNING: Change this password in production!
    """
    print("\nChecking for default admin user...")

    # Check if admin user already exists
    existing_admin = session.query(UserDB).filter(UserDB.username == "admin").first()

    if existing_admin:
        print("⚠️  Admin user already exists. Skipping seed.")
        print(f"   Username: {existing_admin.username}")
        print(f"   Role: {existing_admin.role}")
        print(f"   Created: {existing_admin.created_at}")
        return existing_admin

    # Create admin user
    print("Creating default admin user...")

    admin_user = UserDB(
        username="admin",
        email="admin@fraud-detection.local",
        hashed_password=hash_password("admin123"),
        role="admin",
        is_active=True,
        created_at=datetime.utcnow()
    )

    session.add(admin_user)
    session.commit()
    session.refresh(admin_user)

    print("✅ Admin user created successfully")
    print(f"   Username: admin")
    print(f"   Password: admin123")
    print(f"   Role: admin")
    print(f"   ⚠️  IMPORTANT: Change this password after first login!")

    return admin_user


def seed_test_analyst(session):
    """
    Create a test analyst user for development/testing.

    Credentials:
    - Username: analyst
    - Password: analyst123
    - Role: analyst
    """
    print("\nChecking for test analyst user...")

    existing_analyst = session.query(UserDB).filter(UserDB.username == "analyst").first()

    if existing_analyst:
        print("⚠️  Analyst user already exists. Skipping seed.")
        return existing_analyst

    print("Creating test analyst user...")

    analyst_user = UserDB(
        username="analyst",
        email="analyst@fraud-detection.local",
        hashed_password=hash_password("analyst123"),
        role="analyst",
        is_active=True,
        created_at=datetime.utcnow()
    )

    session.add(analyst_user)
    session.commit()
    session.refresh(analyst_user)

    print("✅ Analyst user created successfully")
    print(f"   Username: analyst")
    print(f"   Password: analyst123")
    print(f"   Role: analyst")

    return analyst_user


def verify_migration(session):
    """
    Verify that migration was successful.

    Checks:
    - Users table exists
    - Admin user exists
    - User count
    """
    print("\n" + "=" * 60)
    print("Migration Verification")
    print("=" * 60)

    # Check users table
    inspector = inspect(session.bind)
    tables = inspector.get_table_names()

    print(f"\n📋 Database tables: {', '.join(tables)}")

    # Check user count
    user_count = session.query(UserDB).count()
    print(f"\n👥 Total users: {user_count}")

    # List all users
    print("\nRegistered users:")
    users = session.query(UserDB).all()
    for user in users:
        print(f"  - {user.username} ({user.role}) - {user.email}")
        print(f"    Active: {user.is_active}, Created: {user.created_at}")

    print("\n✅ Migration verification complete")


def main():
    """
    Main migration function.

    Steps:
    1. Create database connection
    2. Create all tables
    3. Seed default users
    4. Verify migration
    """
    print("=" * 60)
    print("Database Migration Script")
    print("=" * 60)
    print(f"\nDatabase: {Config.DATABASE_URL}")
    print(f"Environment: {Config.ENVIRONMENT}")
    print()

    # Create engine and session
    engine = create_engine(Config.DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    try:
        # Step 1: Create tables
        create_tables(engine)

        # Step 2: Seed admin user
        seed_admin_user(session)

        # Step 3: Seed test analyst (optional, for development)
        if Config.is_development():
            seed_test_analyst(session)

        # Step 4: Verify
        verify_migration(session)

        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
        print("\nDefault login credentials:")
        print("  Admin:")
        print("    Username: admin")
        print("    Password: admin123")
        print("\n  Analyst (development only):")
        print("    Username: analyst")
        print("    Password: analyst123")
        print("\n⚠️  SECURITY WARNING:")
        print("  Change default passwords immediately in production!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
        return 1

    finally:
        session.close()

    return 0


if __name__ == "__main__":
    exit(main())
