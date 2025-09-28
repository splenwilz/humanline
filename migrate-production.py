#!/usr/bin/env python3
"""
Production database migration script for Humanline.
This script runs Alembic migrations against the production Neon database.
"""

import os
import sys
from pathlib import Path
import asyncio
import asyncpg
from alembic import command
from alembic.config import Config

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Production database URL (from your Neon setup)
PRODUCTION_DB_URL = "postgresql://neondb_owner:npg_kI3fwr8TZDyF@ep-lingering-meadow-admipln5-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"

async def test_connection():
    """Test connection to production database."""
    try:
        print("🔌 Testing connection to production database...")
        conn = await asyncpg.connect(PRODUCTION_DB_URL)
        result = await conn.fetchval("SELECT version()")
        await conn.close()
        print(f"✅ Connected successfully! PostgreSQL version: {result}")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def run_migrations():
    """Run Alembic migrations against production database."""
    try:
        print("🔄 Running database migrations...")
        
        # Set environment variable for Alembic
        os.environ["DATABASE_URL"] = PRODUCTION_DB_URL
        
        # Load Alembic configuration
        alembic_cfg = Config(str(backend_path / "alembic.ini"))
        alembic_cfg.set_main_option("sqlalchemy.url", PRODUCTION_DB_URL)
        
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        print("✅ Migrations completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

async def main():
    """Main migration function."""
    print("🚀 Humanline Production Database Migration")
    print("=" * 50)
    
    # Test connection first
    if not await test_connection():
        print("❌ Cannot connect to database. Please check your connection string.")
        sys.exit(1)
    
    # Ask for confirmation
    print("\n⚠️  You are about to run migrations against the PRODUCTION database.")
    print("This will modify the database schema. Are you sure you want to continue?")
    
    confirm = input("Type 'yes' to confirm: ").strip().lower()
    if confirm != 'yes':
        print("❌ Migration cancelled.")
        sys.exit(0)
    
    # Run migrations
    if run_migrations():
        print("\n🎉 Production database is ready!")
        print("\n📋 Next steps:")
        print("1. Deploy your application to Vercel")
        print("2. Test all functionality")
        print("3. Monitor database performance")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
