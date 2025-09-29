#!/bin/bash

echo "🚂 RAILWAY RESOURCE ANALYSIS"
echo "============================"

echo ""
echo "📊 System Resources:"
echo "CPU cores: $(nproc)"
echo "Memory: $(free -h | grep '^Mem:' | awk '{print $2}' 2>/dev/null || echo 'N/A')"
echo "Disk: $(df -h / | tail -1 | awk '{print $2}' 2>/dev/null || echo 'N/A')"

echo ""
echo "⚡ Current Load:"
echo "Load average: $(uptime | grep -o 'load average.*' 2>/dev/null || echo 'N/A')"
echo "Memory usage: $(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100.0}' 2>/dev/null || echo 'N/A')"

echo ""
echo "🐘 PostgreSQL Process:"
ps aux | grep postgres | grep -v grep || echo "PostgreSQL process not visible"

echo ""
echo "🔄 Network Connectivity Test:"
echo "Testing internal connectivity..."

# Test internal network speed
echo "Railway internal connectivity:"
time nc -z postgres.railway.internal 5432 2>/dev/null && echo "✅ PostgreSQL reachable" || echo "❌ PostgreSQL not reachable"
time nc -z redis.railway.internal 6379 2>/dev/null && echo "✅ Redis reachable" || echo "❌ Redis not reachable"

echo ""
echo "🌐 Railway Environment Variables:"
echo "PORT: ${PORT:-'Not set'}"
echo "RAILWAY_ENVIRONMENT: ${RAILWAY_ENVIRONMENT:-'Not set'}"
echo "RAILWAY_PROJECT_NAME: ${RAILWAY_PROJECT_NAME:-'Not set'}"
echo "RAILWAY_SERVICE_NAME: ${RAILWAY_SERVICE_NAME:-'Not set'}"

echo ""
echo "📈 Resource Limits (if available):"
cat /sys/fs/cgroup/memory/memory.limit_in_bytes 2>/dev/null | awk '{print "Memory limit: " $1/1024/1024/1024 " GB"}' || echo "Memory limit: Not available"
cat /sys/fs/cgroup/cpu/cpu.shares 2>/dev/null | awk '{print "CPU shares: " $1}' || echo "CPU shares: Not available"

echo ""
echo "🎯 DIAGNOSIS COMPLETE"
