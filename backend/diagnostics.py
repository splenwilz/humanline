"""
Comprehensive diagnostic script to identify Railway database performance issues.
"""

import asyncio
import time
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text, inspect
from core.config import settings
from core.database import engine, AsyncSessionLocal
from models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_connection_speed():
    """Test basic database connection speed."""
    logger.info("🔗 Testing database connection speed...")
    
    start_time = time.perf_counter()
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    connection_time = time.perf_counter() - start_time
    
    logger.info(f"📊 Connection + Simple Query: {connection_time:.3f}s")
    return connection_time


async def test_multiple_connections():
    """Test if new connections are slow."""
    logger.info("🔄 Testing multiple connection speed...")
    
    times = []
    for i in range(3):
        start_time = time.perf_counter()
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        connection_time = time.perf_counter() - start_time
        times.append(connection_time)
        logger.info(f"Connection {i+1}: {connection_time:.3f}s")
    
    avg_time = sum(times) / len(times)
    logger.info(f"📊 Average connection time: {avg_time:.3f}s")
    return avg_time


async def check_database_indexes():
    """Check if email column has an index."""
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
        indexes = result.fetchall()
        
        logger.info("📋 Current indexes on users table:")
        for idx in indexes:
            logger.info(f"  - {idx[0]}: {idx[1]}")
        
        # Check if email has an index
        email_indexed = any('email' in str(idx[1]).lower() for idx in indexes)
        logger.info(f"📧 Email column indexed: {email_indexed}")
        
        return indexes, email_indexed


async def test_email_query_performance():
    """Test the actual email query that's slow."""
    logger.info("📧 Testing email query performance...")
    
    async with AsyncSessionLocal() as session:
        # Test the exact query that's slow
        start_time = time.perf_counter()
        
        result = await session.execute(
            text("SELECT id FROM users WHERE email = :email LIMIT 1"),
            {"email": "nonexistent@test.com"}
        )
        
        query_time = time.perf_counter() - start_time
        logger.info(f"📊 Email query time: {query_time:.3f}s")
        
        # Test with EXPLAIN to see query plan
        explain_result = await session.execute(
            text("EXPLAIN (ANALYZE, BUFFERS) SELECT id FROM users WHERE email = :email LIMIT 1"),
            {"email": "nonexistent@test.com"}
        )
        
        logger.info("🔍 Query execution plan:")
        for row in explain_result:
            logger.info(f"  {row[0]}")
        
        return query_time


async def check_table_stats():
    """Check table size and statistics."""
    logger.info("📊 Checking table statistics...")
    
    async with engine.begin() as conn:
        # Check table size
        result = await conn.execute(text("""
            SELECT 
                pg_size_pretty(pg_total_relation_size('users')) as total_size,
                pg_size_pretty(pg_relation_size('users')) as table_size,
                (SELECT COUNT(*) FROM users) as row_count
        """))
        stats = result.fetchone()
        
        logger.info(f"📏 Table size: {stats[1]} (total: {stats[0]})")
        logger.info(f"📊 Row count: {stats[2]}")
        
        # Check if autovacuum is working
        result = await conn.execute(text("""
            SELECT 
                last_vacuum,
                last_autovacuum,
                last_analyze,
                last_autoanalyze,
                n_dead_tup,
                n_live_tup
            FROM pg_stat_user_tables 
            WHERE relname = 'users'
        """))
        vacuum_stats = result.fetchone()
        
        if vacuum_stats:
            logger.info(f"🧹 Last vacuum: {vacuum_stats[0]}")
            logger.info(f"🧹 Last autovacuum: {vacuum_stats[1]}")
            logger.info(f"📊 Dead tuples: {vacuum_stats[4]}")
            logger.info(f"📊 Live tuples: {vacuum_stats[5]}")
        
        return stats, vacuum_stats


async def check_postgresql_config():
    """Check PostgreSQL configuration."""
    logger.info("⚙️  Checking PostgreSQL configuration...")
    
    async with engine.begin() as conn:
        # Check important config settings
        configs_to_check = [
            'shared_buffers',
            'work_mem', 
            'maintenance_work_mem',
            'effective_cache_size',
            'max_connections',
            'checkpoint_completion_target',
            'wal_buffers'
        ]
        
        for config in configs_to_check:
            try:
                result = await conn.execute(text(f"SHOW {config}"))
                value = result.scalar()
                logger.info(f"⚙️  {config}: {value}")
            except Exception as e:
                logger.warning(f"❌ Could not get {config}: {e}")


async def test_transaction_performance():
    """Test transaction commit performance."""
    logger.info("💾 Testing transaction performance...")
    
    async with AsyncSessionLocal() as session:
        # Test simple transaction
        start_time = time.perf_counter()
        
        await session.execute(text("BEGIN"))
        await session.execute(text("SELECT 1"))
        await session.commit()
        
        transaction_time = time.perf_counter() - start_time
        logger.info(f"📊 Simple transaction time: {transaction_time:.3f}s")
        
        return transaction_time


async def run_all_diagnostics():
    """Run all diagnostic tests."""
    logger.info("🚀 Starting comprehensive database diagnostics...")
    logger.info("=" * 60)
    
    results = {}
    
    try:
        # Test 1: Basic connection
        results['connection'] = await test_connection_speed()
        
        # Test 2: Multiple connections  
        results['multi_connection'] = await test_multiple_connections()
        
        # Test 3: Check indexes
        results['indexes'] = await check_database_indexes()
        
        # Test 4: Email query performance
        results['email_query'] = await test_email_query_performance()
        
        # Test 5: Table statistics
        results['table_stats'] = await check_table_stats()
        
        # Test 6: PostgreSQL config
        await check_postgresql_config()
        
        # Test 7: Transaction performance
        results['transaction'] = await test_transaction_performance()
        
    except Exception as e:
        logger.error(f"❌ Diagnostic failed: {e}")
        raise
    
    logger.info("=" * 60)
    logger.info("🎯 DIAGNOSTIC SUMMARY:")
    logger.info(f"📊 Connection time: {results.get('connection', 'N/A'):.3f}s")
    logger.info(f"📊 Email query time: {results.get('email_query', 'N/A'):.3f}s") 
    logger.info(f"📊 Transaction time: {results.get('transaction', 'N/A'):.3f}s")
    logger.info(f"📇 Email indexed: {results.get('indexes', [None, False])[1]}")
    
    return results


if __name__ == "__main__":
    asyncio.run(run_all_diagnostics())
