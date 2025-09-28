-- Database initialization script for Humanline Backend
-- This script runs when the PostgreSQL container starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "citext";

-- Set timezone
SET timezone = 'UTC';

-- Create additional schemas if needed
-- CREATE SCHEMA IF NOT EXISTS analytics;
-- CREATE SCHEMA IF NOT EXISTS audit;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE humanline TO humanline_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO humanline_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO humanline_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO humanline_user;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO humanline_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO humanline_user;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Humanline database initialized successfully at %', NOW();
END $$;
