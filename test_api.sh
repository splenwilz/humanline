#!/bin/bash

# Test script for Humanline API on Railway
API_URL="https://humanline-production.up.railway.app"

echo "🧪 Testing Humanline API at: $API_URL"
echo "==============================================="

# Test 1: Health Check
echo "1️⃣ Testing Health Endpoint..."
curl -s -w "\nStatus: %{http_code}\n" "$API_URL/health"
echo ""

# Test 2: API Documentation
echo "2️⃣ Testing API Documentation..."
curl -s -w "\nStatus: %{http_code}\n" "$API_URL/docs" | head -5
echo ""

# Test 3: OpenAPI Schema
echo "3️⃣ Testing OpenAPI Schema..."
curl -s -w "\nStatus: %{http_code}\n" "$API_URL/openapi.json" | head -3
echo ""

# Test 4: User Registration (should work)
echo "4️⃣ Testing User Registration..."
curl -s -w "\nStatus: %{http_code}\n" \
  -X POST "$API_URL/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@humanline.com",
    "password": "SecurePassword123!",
    "first_name": "Test",
    "last_name": "User"
  }'
echo ""

echo "✅ API Tests Complete!"
