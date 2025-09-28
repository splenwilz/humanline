#!/bin/bash

# Vercel Deployment Script for Humanline Full Stack Application

set -e

echo "🚀 Deploying Humanline to Vercel..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}ℹ️  $1${NC}"
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

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    print_error "Vercel CLI is not installed"
    echo "Install it with: npm install -g vercel"
    exit 1
fi

# Check if user is logged in to Vercel
if ! vercel whoami &> /dev/null; then
    print_warning "You are not logged in to Vercel"
    echo "Please run: vercel login"
    exit 1
fi

print_status "Checking project structure..."

# Ensure we're in the project root
if [ ! -f "vercel.json" ]; then
    print_error "vercel.json not found. Make sure you're in the project root."
    exit 1
fi

if [ ! -f "frontend/package.json" ]; then
    print_error "Frontend package.json not found"
    exit 1
fi

if [ ! -f "backend/main.py" ]; then
    print_error "Backend main.py not found"
    exit 1
fi

print_success "Project structure looks good"

# Install frontend dependencies
print_status "Installing frontend dependencies..."
cd frontend
npm ci
cd ..
print_success "Frontend dependencies installed"

# Build frontend (optional, Vercel will do this)
print_status "Testing frontend build..."
cd frontend
npm run build
cd ..
print_success "Frontend builds successfully"

# Deploy to Vercel
print_status "Deploying to Vercel..."
vercel --prod

print_success "Deployment completed!"

echo ""
echo "🎉 Your Humanline application has been deployed to Vercel!"
echo ""
echo "📋 Next steps:"
echo "1. Set up your production database (Neon, Supabase, or Vercel Postgres)"
echo "2. Set up Redis (Upstash or Vercel KV)"
echo "3. Configure environment variables in Vercel dashboard"
echo "4. Update CORS origins in production environment"
echo "5. Test all functionality on the live site"
echo ""
echo "🔧 To configure environment variables:"
echo "   vercel env add <VARIABLE_NAME>"
echo "   Or use the Vercel dashboard: https://vercel.com/dashboard"
echo ""
echo "📖 Deployment documentation:"
echo "   https://vercel.com/docs"
