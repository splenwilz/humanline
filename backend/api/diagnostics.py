"""
Railway diagnostic endpoint for real-time performance analysis.
"""

import asyncio
import time
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from core.database import get_db, engine
from models.user import User

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])
logger = logging.getLogger(__name__)


@router.get("/connection-speed")
async def test_connection_speed():
    """Test database connection speed."""
    logger.info("🔗 Testing database connection speed...")
    
    start_time = time.perf_counter()
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    connection_time = time.perf_counter() - start_time
    
    return {
        "connection_time": round(connection_time, 3),
        "status": "slow" if connection_time > 0.1 else "normal"
    }


@router.get("/query-performance")
async def test_query_performance(db: AsyncSession = Depends(get_db)):
    """Test the actual slow email query."""
    logger.info("📧 Testing email query performance...")
    
    # Test the exact query that's slow
    start_time = time.perf_counter()
    result = await db.execute(
        text("SELECT id FROM users WHERE email = :email LIMIT 1"),
        {"email": "nonexistent@test.com"}
    )
    query_time = time.perf_counter() - start_time
    
    return {
        "email_query_time": round(query_time, 3),
        "status": "slow" if query_time > 0.1 else "normal",
        "found": result.scalar_one_or_none() is not None
    }


@router.get("/database-indexes")
async def check_database_indexes():
    """Check database indexes."""
    logger.info("📇 Checking database indexes...")
    
    async with engine.begin() as conn:
        # Check indexes on users table
        result = await conn.execute(text("""
            SELECT 
                indexname, 
                indexdef 
            FROM pg_indexes 
            WHERE tablename = 'users'
        """))
        indexes = [{"name": row[0], "definition": row[1]} for row in result.fetchall()]
        
        # Check if email has an index
        email_indexed = any('email' in idx['definition'].lower() for idx in indexes)
        
        return {
            "indexes": indexes,
            "email_indexed": email_indexed,
            "total_indexes": len(indexes)
        }


@router.get("/table-stats")
async def check_table_stats():
    """Check table statistics."""
    logger.info("📊 Checking table statistics...")
    
    async with engine.begin() as conn:
        # Check table size and row count
        result = await conn.execute(text("""
            SELECT 
                pg_size_pretty(pg_total_relation_size('users')) as total_size,
                pg_size_pretty(pg_relation_size('users')) as table_size,
                (SELECT COUNT(*) FROM users) as row_count
        """))
        stats = result.fetchone()
        
        # Check vacuum stats
        result = await conn.execute(text("""
            SELECT 
                last_vacuum,
                last_autovacuum,
                n_dead_tup,
                n_live_tup
            FROM pg_stat_user_tables 
            WHERE relname = 'users'
        """))
        vacuum_stats = result.fetchone()
        
        return {
            "table_size": stats[1] if stats else "unknown",
            "total_size": stats[0] if stats else "unknown",
            "row_count": stats[2] if stats else 0,
            "last_vacuum": str(vacuum_stats[0]) if vacuum_stats and vacuum_stats[0] else "never",
            "last_autovacuum": str(vacuum_stats[1]) if vacuum_stats and vacuum_stats[1] else "never",
            "dead_tuples": vacuum_stats[2] if vacuum_stats else 0,
            "live_tuples": vacuum_stats[3] if vacuum_stats else 0
        }


@router.get("/transaction-performance")
async def test_transaction_performance(db: AsyncSession = Depends(get_db)):
    """Test transaction commit performance."""
    logger.info("💾 Testing transaction performance...")
    
    start_time = time.perf_counter()
    
    await db.execute(text("SELECT 1"))
    await db.commit()
    
    transaction_time = time.perf_counter() - start_time
    
    return {
        "transaction_time": round(transaction_time, 3),
        "status": "slow" if transaction_time > 0.1 else "normal"
    }


@router.get("/query-plan")
async def get_query_plan():
    """Get query execution plan for email lookup."""
    logger.info("🔍 Getting query execution plan...")
    
    async with engine.begin() as conn:
        # Get query plan
        result = await conn.execute(text("""
            EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) 
            SELECT id FROM users WHERE email = 'test@example.com' LIMIT 1
        """))
        
        plan_data = result.scalar()
        
        return {
            "query_plan": plan_data,
            "analysis": "Check for 'Index Scan' vs 'Seq Scan' in execution method"
        }


@router.get("/comprehensive")
async def comprehensive_diagnostics(db: AsyncSession = Depends(get_db)):
    """Run all diagnostics and return comprehensive results."""
    logger.info("🚀 Running comprehensive diagnostics...")
    
    results = {}
    
    # Test connection speed
    start_time = time.perf_counter()
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    results['connection_time'] = round(time.perf_counter() - start_time, 3)
    
    # Test email query
    start_time = time.perf_counter()
    await db.execute(
        text("SELECT id FROM users WHERE email = :email LIMIT 1"),
        {"email": "nonexistent@test.com"}
    )
    results['email_query_time'] = round(time.perf_counter() - start_time, 3)
    
    # Test transaction
    start_time = time.perf_counter()
    await db.execute(text("SELECT 1"))
    await db.commit()
    results['transaction_time'] = round(time.perf_counter() - start_time, 3)
    
    # Overall assessment
    total_time = results['connection_time'] + results['email_query_time'] + results['transaction_time']
    
    bottleneck = "unknown"
    if results['email_query_time'] > 0.5:
        bottleneck = "email_query"
    elif results['connection_time'] > 0.3:
        bottleneck = "connection"
    elif results['transaction_time'] > 0.3:
        bottleneck = "transaction"
    
    results.update({
        "total_estimated_time": round(total_time, 3),
        "primary_bottleneck": bottleneck,
        "status": "problematic" if total_time > 1.0 else "normal"
    })
    
    return results
