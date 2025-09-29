#!/bin/bash

# Detailed Profiling Test Script
echo "🔍 DETAILED PERFORMANCE PROFILING"
echo "=================================="

LOCAL_URL="http://localhost:8000"
RAILWAY_URL="https://humanline-production.up.railway.app"

# Function to test with detailed headers
profile_request() {
    local url=$1
    local endpoint=$2
    local method=$3
    local data=$4
    local description=$5
    
    echo ""
    echo "🔍 Profiling: $description"
    echo "URL: $url$endpoint"
    echo "----------------------------------------"
    
    if [ "$method" = "POST" ]; then
        curl -w "🌐 DNS Lookup: %{time_namelookup}s\n🔗 TCP Connect: %{time_connect}s\n🔒 SSL Handshake: %{time_appconnect}s\n📤 Pre-transfer: %{time_pretransfer}s\n⬇️  First Byte: %{time_starttransfer}s\n⏱️  Total Time: %{time_total}s\n📦 Size: %{size_download} bytes\n🌐 HTTP Code: %{http_code}\n" \
             -s -X POST \
             -H "Content-Type: application/json" \
             -H "Accept: application/json" \
             -d "$data" \
             "$url$endpoint" | head -20
    else
        curl -w "🌐 DNS Lookup: %{time_namelookup}s\n🔗 TCP Connect: %{time_connect}s\n🔒 SSL Handshake: %{time_appconnect}s\n📤 Pre-transfer: %{time_pretransfer}s\n⬇️  First Byte: %{time_starttransfer}s\n⏱️  Total Time: %{time_total}s\n📦 Size: %{size_download} bytes\n🌐 HTTP Code: %{http_code}\n" \
             -s "$url$endpoint" | head -10
    fi
}

echo ""
echo "🏠 LOCAL SERVER PROFILING"
echo "=========================="

# Check if local server is running
if curl -s "$LOCAL_URL/health" > /dev/null 2>&1; then
    echo "✅ Local server is running"
    
    # Profile local health check
    profile_request "$LOCAL_URL" "/health" "GET" "" "Local Health Check"
    
    # Profile local registration
    local_email="profile$(date +%s)@local.com"
    local_data='{"email":"'$local_email'","password":"SecurePassword123!","first_name":"Profile","last_name":"Local"}'
    profile_request "$LOCAL_URL" "/api/v1/auth/register" "POST" "$local_data" "Local User Registration"
    
else
    echo "❌ Local server is not running"
fi

echo ""
echo "☁️  RAILWAY SERVER PROFILING"
echo "============================"

# Profile Railway health check
profile_request "$RAILWAY_URL" "/health" "GET" "" "Railway Health Check"

# Profile Railway registration
railway_email="profile$(date +%s)@railway.com"
railway_data='{"email":"'$railway_email'","password":"SecurePassword123!","first_name":"Profile","last_name":"Railway"}'
profile_request "$RAILWAY_URL" "/api/v1/auth/register" "POST" "$railway_data" "Railway User Registration"

echo ""
echo "📊 NETWORK ANALYSIS"
echo "==================="

echo "Testing Railway network breakdown:"
curl -w "
🌐 DNS Resolution: %{time_namelookup}s
🔗 TCP Connection: %{time_connect}s  
🔒 SSL Handshake: %{time_appconnect}s
📡 Server Processing: %{time_starttransfer}s
📦 Data Transfer: %{time_total}s
" -s -o /dev/null "$RAILWAY_URL/health"

echo ""
echo "🎯 PROFILING COMPLETE!"
echo "Check Railway logs for detailed internal timing breakdown."
