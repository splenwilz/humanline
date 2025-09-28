#!/bin/bash

# Humanline Backend Startup Script
# This script sets up and starts the FastAPI application

set -e  # Exit on any error

echo "🚀 Starting Humanline Backend Application..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source .venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp env.example .env
    echo "📝 Please edit .env file with your configuration before running again."
    exit 1
fi

# Run database migrations
echo "🗄️  Running database migrations..."
alembic upgrade head

# Start the application
echo "🌟 Starting FastAPI application..."
echo "📖 API Documentation will be available at: http://localhost:8000/docs"
echo "🔍 Alternative docs at: http://localhost:8000/redoc"
echo ""

# Run with uvicorn directly for better control
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
