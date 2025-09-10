#!/bin/bash

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Creating .env file from template..."
    cp env.example .env
    echo "📝 Please edit .env file with your Supabase credentials:"
    echo "   - SUPABASE_URL"
    echo "   - SUPABASE_ANON_KEY" 
    echo "   - SUPABASE_SERVICE_KEY"
    echo ""
    echo "Get these from: https://app.supabase.com/project/YOUR_PROJECT/settings/api"
    echo ""
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies if needed
if [ ! -d ".venv/lib/python*/site-packages/fastapi" ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Start the server
echo "🚀 Starting FastAPI server on http://localhost:8000"
echo "📚 API docs: http://localhost:8000/docs"
echo ""
uvicorn main:app --reload --port 8000
