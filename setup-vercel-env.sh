#!/bin/bash

# Vercel Environment Variables Setup Script for Humanline

set -e

echo "🔧 Setting up Vercel environment variables for Humanline..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}🔧 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if Vercel CLI is installed and user is logged in
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI is not installed. Install it with: npm install -g vercel"
    exit 1
fi

if ! vercel whoami &> /dev/null; then
    echo "❌ You are not logged in to Vercel. Run: vercel login"
    exit 1
fi

echo "Setting up environment variables for production deployment..."
echo ""

# Database Configuration
print_status "Setting up database configuration..."
vercel env add DATABASE_URL production <<< "postgresql+asyncpg://neondb_owner:npg_kI3fwr8TZDyF@ep-lingering-meadow-admipln5-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"
print_success "Database URL configured"

# Redis Configuration  
print_status "Setting up Redis configuration..."
vercel env add REDIS_URL production <<< "redis://default:ATYSAAIncDJmNDk5ZWY4MjVkOTk0OThhOThiYjZhNzVmYWJjM2Y3NXAyMTM4NDI@apt-hamster-13842.upstash.io:6379"
print_success "Redis URL configured"

# Security Configuration (you'll need to provide these)
print_status "Setting up security configuration..."
echo "Please enter a secure SECRET_KEY (32+ characters):"
vercel env add SECRET_KEY production

echo "Please enter a secure NEXTAUTH_SECRET:"
vercel env add NEXTAUTH_SECRET production

# Environment
print_status "Setting up environment..."
vercel env add ENVIRONMENT production <<< "production"
vercel env add NODE_ENV production <<< "production"
vercel env add ALGORITHM production <<< "HS256"
vercel env add ACCESS_TOKEN_EXPIRE_MINUTES production <<< "30"
vercel env add LOG_LEVEL production <<< "info"

print_success "Environment variables configured"

# URLs (will be updated after first deployment)
print_status "Setting up URLs (you can update these after deployment)..."
echo "Please enter your domain (e.g., your-app.vercel.app):"
read -r DOMAIN

vercel env add NEXT_PUBLIC_API_URL production <<< "https://$DOMAIN"
vercel env add NEXT_PUBLIC_APP_URL production <<< "https://$DOMAIN"
vercel env add NEXTAUTH_URL production <<< "https://$DOMAIN"
vercel env add ALLOWED_ORIGINS production <<< "https://$DOMAIN"

print_success "URLs configured"

echo ""
print_success "All environment variables have been configured!"
echo ""
echo "📋 Summary of configured variables:"
echo "✅ DATABASE_URL - Neon PostgreSQL"
echo "✅ REDIS_URL - Upstash Redis"
echo "✅ SECRET_KEY - Your secure key"
echo "✅ NEXTAUTH_SECRET - Your NextAuth secret"
echo "✅ Environment settings"
echo "✅ Domain URLs: https://$DOMAIN"
echo ""
echo "🚀 Ready to deploy! Run: ./deploy-vercel.sh"
echo ""
echo "💡 After deployment, you can update environment variables at:"
echo "   https://vercel.com/dashboard (select your project > Settings > Environment Variables)"
