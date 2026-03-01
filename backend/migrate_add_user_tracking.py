"""
Database Migration: Add User Tracking to Transactions
=====================================================
Adds created_by_user_id and created_by_username columns to the transactions table.

Run this script once to upgrade your database:
    python migrate_add_user_tracking.py
"""

import sqlite3
from pathlib import Path

def migrate():
    db_path = Path(__file__).parent / "fraud_detection.db"

    if not db_path.exists():
        print("❌ Database not found. It will be created automatically on first run.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(transactions)")
        columns = [col[1] for col in cursor.fetchall()]

        migrations_needed = []

        if "created_by_user_id" not in columns:
            migrations_needed.append("created_by_user_id")

        if "created_by_username" not in columns:
            migrations_needed.append("created_by_username")

        if not migrations_needed:
            print("✅ Database is already up to date. No migration needed.")
            return

        print(f"📝 Adding columns: {', '.join(migrations_needed)}")

        # Add columns if they don't exist
        if "created_by_user_id" in migrations_needed:
            cursor.execute("""
                ALTER TABLE transactions
                ADD COLUMN created_by_user_id INTEGER
            """)
            print("   ✓ Added created_by_user_id column")

        if "created_by_username" in migrations_needed:
            cursor.execute("""
                ALTER TABLE transactions
                ADD COLUMN created_by_username TEXT
            """)
            print("   ✓ Added created_by_username column")

        conn.commit()
        print("\n✅ Migration completed successfully!")
        print("   Old transactions will show 'Unknown' for tested_by field.")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("="*60)
    print("  Database Migration: Add User Tracking")
    print("="*60)
    print()
    migrate()
    print()
