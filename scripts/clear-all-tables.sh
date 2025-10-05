#!/bin/bash

# Clear All Database Tables Script
# 
# This script clears all data from database tables while preserving the schema.
# Useful for development, testing, and resetting the application state.
#
# Usage:
#   ./scripts/clear-all-tables.sh [--confirm]
#
# Options:
#   --confirm    Skip confirmation prompt (for automation)
#   --help       Show this help message

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")/backend"

# Function to print colored output
print_status() {
    echo -e "${BLUE}🔄 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to show help
show_help() {
    cat << EOF
🧹 Database Table Cleaner

This script clears all data from database tables while preserving the schema.

Usage:
    $0 [OPTIONS]

Options:
    --confirm    Skip confirmation prompt (for automation)
    --help       Show this help message

Examples:
    $0              # Interactive mode with confirmation
    $0 --confirm    # Skip confirmation prompt

Safety Features:
- Requires confirmation before proceeding (unless --confirm is used)
- Handles foreign key constraints properly
- Preserves table structure and indexes
- Provides detailed feedback on operations

Tables cleared:
- users (all user accounts)
- onboarding (all company onboarding data)
EOF
}

# Parse command line arguments
CONFIRM=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --confirm)
            CONFIRM=true
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information."
            exit 1
            ;;
    esac
done

# Main function
main() {
    echo "🧹 Database Table Cleaner"
    echo "=================================================="
    
    # Check if we're in the right directory
    if [[ ! -d "$BACKEND_DIR" ]]; then
        print_error "Backend directory not found: $BACKEND_DIR"
        print_error "Please run this script from the project root or scripts directory."
        exit 1
    fi
    
    # Change to backend directory
    cd "$BACKEND_DIR"
    
    # Check if Python script exists
    PYTHON_SCRIPT="$SCRIPT_DIR/clear-all-tables.py"
    if [[ ! -f "$PYTHON_SCRIPT" ]]; then
        print_error "Python script not found: $PYTHON_SCRIPT"
        exit 1
    fi
    
    # Show warning if not confirmed
    if [[ "$CONFIRM" != "true" ]]; then
        echo
        print_warning "WARNING: This will DELETE ALL DATA from the database!"
        echo "📊 Tables that will be cleared:"
        echo "   - users (all user accounts)"
        echo "   - onboarding (all company onboarding data)"
        echo
        
        read -p "Are you sure you want to continue? (type 'yes' to confirm): " response
        if [[ "$response" != "yes" ]]; then
            print_error "Operation cancelled."
            exit 1
        fi
    fi
    
    print_status "Running Python script to clear tables..."
    
    # Run the Python script using uv (project's Python manager)
    # Need to run from backend directory to load .env file properly
    if command -v uv &> /dev/null; then
        print_status "Using uv to run Python script..."
        if [[ "$CONFIRM" == "true" ]]; then
            (cd "$BACKEND_DIR" && uv run python "$PYTHON_SCRIPT" --confirm)
        else
            (cd "$BACKEND_DIR" && uv run python "$PYTHON_SCRIPT" --confirm)  # We already confirmed above
        fi
    elif command -v python3 &> /dev/null; then
        print_status "Using python3 to run script..."
        if [[ "$CONFIRM" == "true" ]]; then
            (cd "$BACKEND_DIR" && python3 "$PYTHON_SCRIPT" --confirm)
        else
            (cd "$BACKEND_DIR" && python3 "$PYTHON_SCRIPT" --confirm)  # We already confirmed above
        fi
    elif command -v python &> /dev/null; then
        print_status "Using python to run script..."
        if [[ "$CONFIRM" == "true" ]]; then
            (cd "$BACKEND_DIR" && python "$PYTHON_SCRIPT" --confirm)
        else
            (cd "$BACKEND_DIR" && python "$PYTHON_SCRIPT" --confirm)  # We already confirmed above
        fi
    else
        print_error "No Python interpreter found. Please install Python or uv."
        exit 1
    fi
    
    if [[ $? -eq 0 ]]; then
        print_success "Database cleared successfully!"
        echo
        echo "🔄 Database is now empty and ready for fresh data."
    else
        print_error "Failed to clear database. Check the output above for details."
        exit 1
    fi
}

# Run main function
main "$@"
