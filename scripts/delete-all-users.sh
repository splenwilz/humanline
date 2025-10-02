#!/bin/bash
#
# Delete All Users Script
# 
# This script deletes all users from the Humanline database.
# Useful for development and testing purposes.
#
# Usage: ./scripts/delete-all-users.sh
#

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🗑️  Deleting all users from Humanline database...${NC}"
echo ""

# Change to backend directory
cd "$(dirname "$0")/../backend"

# Run the delete script using uv
uv run python -c "
import asyncio
from sqlalchemy import delete
from core.database import AsyncSessionLocal
from models.user import User

async def delete_all_users():
    async with AsyncSessionLocal() as session:
        try:
            # Delete all users
            result = await session.execute(delete(User))
            await session.commit()
            print(f'✅ Deleted {result.rowcount} users from database')
            return result.rowcount
        except Exception as e:
            await session.rollback()
            print(f'❌ Error deleting users: {e}')
            return 0

count = asyncio.run(delete_all_users())
"

echo ""
echo -e "${GREEN}✅ Database cleanup completed!${NC}"
echo -e "${YELLOW}💡 Tip: You can run this script anytime with: ./scripts/delete-all-users.sh${NC}"
