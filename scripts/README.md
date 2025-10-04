# Scripts Directory

This directory contains utility scripts for managing the Humanline application.

## Available Scripts

### 🧹 Database Management

#### `clear-all-tables.py` / `clear-all-tables.sh`
Clears all data from database tables while preserving the schema structure.

**Usage:**
```bash
# Python version (recommended) - using uv
cd backend && uv run python ../scripts/clear-all-tables.py              # Interactive mode
cd backend && uv run python ../scripts/clear-all-tables.py --confirm    # Skip confirmation

# Alternative Python usage
python3 scripts/clear-all-tables.py              # Interactive mode
python3 scripts/clear-all-tables.py --confirm    # Skip confirmation

# Shell version (automatically detects uv/python3/python)
./scripts/clear-all-tables.sh                   # Interactive mode  
./scripts/clear-all-tables.sh --confirm         # Skip confirmation
```

**Features:**
- ✅ Safe deletion with confirmation prompts
- ✅ Handles foreign key constraints properly
- ✅ Preserves table structure and indexes
- ✅ Detailed feedback and verification
- ✅ Supports both interactive and automated usage

**Tables cleared:**
- `users` - All user accounts and authentication data
- `onboarding` - All company onboarding information

#### `delete-all-users.sh`
Legacy script for deleting user data (consider using `clear-all-tables.py` instead).

## 🚀 Usage Examples

### Development Workflow
```bash
# Reset database for fresh development
./scripts/clear-all-tables.sh

# Run migrations to recreate schema
cd backend && uv run alembic upgrade head

# Start fresh development server
cd backend && uv run uvicorn main:app --reload
```

### Testing Workflow
```bash
# Clear database before running tests (using shell script)
./scripts/clear-all-tables.sh --confirm

# Or using Python directly
cd backend && uv run python ../scripts/clear-all-tables.py --confirm

# Run test suite
cd backend && uv run pytest
```

### CI/CD Integration
```bash
# Automated cleanup (no prompts)
./scripts/clear-all-tables.sh --confirm
```

## 🛡️ Safety Features

All scripts include safety measures:

- **Confirmation prompts** - Prevent accidental data loss
- **Error handling** - Graceful failure with clear messages  
- **Transaction safety** - Atomic operations where possible
- **Detailed logging** - Clear feedback on operations
- **Help documentation** - Built-in usage instructions

## 📝 Adding New Scripts

When adding new scripts to this directory:

1. **Make them executable**: `chmod +x script-name.sh`
2. **Add help documentation**: Support `--help` flag
3. **Include safety measures**: Confirmation prompts for destructive operations
4. **Update this README**: Document the new script
5. **Follow naming convention**: Use kebab-case for script names

## 🔧 Requirements

- **Python scripts**: Require Python 3.8+ and backend dependencies
- **Shell scripts**: Require bash and standard Unix utilities
- **Database access**: Scripts need valid database connection (check `.env` file)

## ⚠️ Important Notes

- **Backup data** before running destructive operations
- **Test scripts** in development environment first
- **Use `--confirm` flag** carefully in production environments
- **Check database URL** in environment variables before running
