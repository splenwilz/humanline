#!/usr/bin/env python3
"""
Clear All Database Tables Script

This script clears all data from database tables while preserving the schema.
Useful for development, testing, and resetting the application state.

Usage:
    python scripts/clear-all-tables.py [--confirm]
    
Options:
    --confirm    Skip confirmation prompt (for automation)
    --help       Show this help message

Safety Features:
- Requires confirmation before proceeding
- Handles foreign key constraints properly
- Preserves table structure and indexes
- Provides detailed feedback on operations
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from core.config import settings
from models import User, Onboarding


async def clear_all_tables(confirm: bool = False) -> None:
    """
    Clear all data from database tables.
    
    Args:
        confirm: If True, skip confirmation prompt
    """
    
    if not confirm:
        print("🚨 WARNING: This will DELETE ALL DATA from the database!")
        print("📊 Tables that will be cleared:")
        print("   - users (all user accounts)")
        print("   - onboarding (all company onboarding data)")
        print()
        
        response = input("Are you sure you want to continue? (type 'yes' to confirm): ")
        if response.lower() != 'yes':
            print("❌ Operation cancelled.")
            return
    
    print("🔄 Connecting to database...")
    
    # Create async engine
    engine = create_async_engine(
        settings.database_url,
        echo=False  # Set to True for SQL debugging
    )
    
    # Create async session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    try:
        async with async_session() as session:
            print("🧹 Starting table cleanup...")
            
            # Disable foreign key checks temporarily (for SQLite)
            # For PostgreSQL, we'll delete in proper order
            if "sqlite" in settings.database_url:
                await session.execute(text("PRAGMA foreign_keys = OFF"))
            
            # Delete data in reverse dependency order to handle foreign keys
            # 1. First delete onboarding (has foreign key to users)
            print("   🗑️  Clearing onboarding table...")
            result = await session.execute(text("DELETE FROM onboarding"))
            onboarding_count = result.rowcount
            
            # 2. Then delete users
            print("   🗑️  Clearing users table...")
            result = await session.execute(text("DELETE FROM users"))
            users_count = result.rowcount
            
            # Re-enable foreign key checks (for SQLite)
            if "sqlite" in settings.database_url:
                await session.execute(text("PRAGMA foreign_keys = ON"))
            
            # Commit the transaction
            await session.commit()
            
            print("✅ Database cleared successfully!")
            print(f"   📊 Deleted {users_count} users")
            print(f"   📊 Deleted {onboarding_count} onboarding records")
            print()
            print("🔄 Database is now empty and ready for fresh data.")
            
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        raise
    finally:
        await engine.dispose()


async def verify_tables_empty() -> None:
    """Verify that all tables are empty after clearing."""
    
    print("🔍 Verifying tables are empty...")
    
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with async_session() as session:
            # Check users table
            result = await session.execute(text("SELECT COUNT(*) FROM users"))
            users_count = result.scalar()
            
            # Check onboarding table
            result = await session.execute(text("SELECT COUNT(*) FROM onboarding"))
            onboarding_count = result.scalar()
            
            if users_count == 0 and onboarding_count == 0:
                print("✅ Verification passed: All tables are empty")
            else:
                print(f"⚠️  Verification failed:")
                print(f"   Users remaining: {users_count}")
                print(f"   Onboarding records remaining: {onboarding_count}")
                
    except Exception as e:
        print(f"❌ Error during verification: {e}")
    finally:
        await engine.dispose()


def main():
    """Main entry point for the script."""
    
    parser = argparse.ArgumentParser(
        description="Clear all data from database tables",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/clear-all-tables.py              # Interactive mode
    python scripts/clear-all-tables.py --confirm    # Skip confirmation
        """
    )
    
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Skip confirmation prompt (for automation)"
    )
    
    args = parser.parse_args()
    
    print("🧹 Database Table Cleaner")
    print("=" * 50)
    
    try:
        # Run the async function
        asyncio.run(clear_all_tables(confirm=args.confirm))
        
        # Verify the operation
        asyncio.run(verify_tables_empty())
        
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Script failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
