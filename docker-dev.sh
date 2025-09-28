#!/bin/bash

# Unified Development Docker Script for Humanline Full Stack Application
# This script manages the development environment with hot reloading for both frontend and backend

set -e  # Exit on any error

COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

echo "🚀 Humanline Full Stack - Development Mode"

# Function to show usage
show_usage() {
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  start [services]  - Start development environment (default: backend only)"
    echo "  stop              - Stop development environment"
    echo "  restart [services]- Restart development environment"
    echo "  logs [service]    - Show logs"
    echo "  build [services]  - Build development images"
    echo "  clean             - Clean up development environment"
    echo "  shell [service]   - Open shell in container (default: backend)"
    echo "  db                - Open database shell"
    echo "  migrate           - Run database migrations"
    echo "  test [service]    - Run tests"
    echo "  full              - Start full stack (frontend + backend + nginx)"
    echo ""
    echo "Services: backend, frontend, postgres, redis, nginx"
    echo ""
    echo "Examples:"
    echo "  $0 start                    # Start backend only"
    echo "  $0 start backend frontend   # Start backend and frontend"
    echo "  $0 full                     # Start complete stack with nginx"
    echo "  $0 logs backend             # Show backend logs"
    echo "  $0 shell frontend           # Open frontend container shell"
    echo ""
}

# Check if .env exists and configure for development
check_env() {
    if [ ! -f "$ENV_FILE" ]; then
        echo "📝 Creating development environment file..."
        cp env.dev "$ENV_FILE"
        echo "✅ Created $ENV_FILE - configured for development mode"
    else
        # Check if it's already configured for development
        if ! grep -q "ENVIRONMENT=development" "$ENV_FILE"; then
            echo "⚠️  Warning: $ENV_FILE exists but may not be configured for development"
            echo "💡 Make sure ENVIRONMENT=development is set in $ENV_FILE"
            echo "💡 Or run: cp env.dev $ENV_FILE"
        fi
    fi
}

# Start development environment
start_dev() {
    echo "🔧 Starting development environment..."
    check_env
    
    local services="${@:-backend postgres redis}"
    echo "🚀 Starting services: $services"
    
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d $services
    
    echo "⏳ Waiting for services to be ready..."
    sleep 10
    
    echo "🌟 Development environment started!"
    echo ""
    echo "📊 Service URLs:"
    if [[ "$services" == *"backend"* ]]; then
        echo "   - Backend API: http://localhost:8000"
        echo "   - API Documentation: http://localhost:8000/docs"
        echo "   - Health Check: http://localhost:8000/health"
    fi
    if [[ "$services" == *"frontend"* ]]; then
        echo "   - Frontend App: http://localhost:3001"
    fi
    if [[ "$services" == *"nginx"* ]]; then
        echo "   - Nginx Proxy: http://localhost:8080"
    fi
    echo "   - Database: localhost:5433"
    echo "   - Redis: localhost:6380"
    echo ""
    echo "🔍 View logs: $0 logs [service]"
    echo "🛑 Stop: $0 stop"
}

# Start full stack
start_full() {
    echo "🌟 Starting full stack development environment..."
    check_env
    
    echo "🚀 Starting full stack services..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" --profile frontend up -d backend frontend postgres redis
    
    echo "⏳ Waiting for services to be ready..."
    sleep 15
    
    echo "🌟 Full stack development environment started!"
    echo ""
    echo "📊 Service URLs:"
    echo "   - Frontend App: http://localhost:3001"
    echo "   - Backend API: http://localhost:8000"
    echo "   - API Documentation: http://localhost:8000/docs"
    echo "   - Health Check: http://localhost:8000/health"
    echo "   - Database: localhost:5433"
    echo "   - Redis: localhost:6380"
    echo ""
    echo "🔍 View logs: ./docker-dev.sh logs [service]"
    echo "🛑 Stop: ./docker-dev.sh stop"
}

# Stop development environment
stop_dev() {
    echo "🛑 Stopping development environment..."
    docker-compose -f "$COMPOSE_FILE" down
    echo "✅ Development environment stopped"
}

# Restart development environment
restart_dev() {
    echo "🔄 Restarting development environment..."
    stop_dev
    start_dev "$@"
}

# Show logs
show_logs() {
    local service="${1:-backend}"
    echo "📋 Showing logs for: $service"
    docker-compose -f "$COMPOSE_FILE" logs -f "$service"
}

# Build development images
build_dev() {
    echo "🔨 Building development images..."
    check_env
    local services="${@:-backend frontend}"
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build --no-cache $services
    echo "✅ Development images built"
}

# Clean up development environment
clean_dev() {
    echo "🧹 Cleaning up development environment..."
    docker-compose -f "$COMPOSE_FILE" down -v --remove-orphans
    docker system prune -f
    echo "✅ Development environment cleaned"
}

# Open shell in container
container_shell() {
    local service="${1:-backend}"
    echo "🐚 Opening shell in $service container..."
    docker-compose -f "$COMPOSE_FILE" exec "$service" bash
}

# Open database shell
db_shell() {
    echo "🗄️ Opening database shell..."
    docker-compose -f "$COMPOSE_FILE" exec postgres psql -U humanline_user -d humanline_dev
}

# Run migrations
run_migrations() {
    echo "🔄 Running database migrations..."
    docker-compose -f "$COMPOSE_FILE" exec backend alembic upgrade head
    echo "✅ Migrations completed"
}

# Run tests
run_tests() {
    local service="${1:-backend}"
    echo "🧪 Running tests for $service..."
    case "$service" in
        "backend")
            docker-compose -f "$COMPOSE_FILE" exec backend python -m pytest
            ;;
        "frontend")
            docker-compose -f "$COMPOSE_FILE" exec frontend npm test
            ;;
        *)
            echo "❌ Unknown service: $service"
            exit 1
            ;;
    esac
}

# Main command handler
case "${1:-start}" in
    "start")
        shift
        start_dev "$@"
        ;;
    "full")
        start_full
        ;;
    "stop")
        stop_dev
        ;;
    "restart")
        shift
        restart_dev "$@"
        ;;
    "logs")
        show_logs "${2:-backend}"
        ;;
    "build")
        shift
        build_dev "$@"
        ;;
    "clean")
        clean_dev
        ;;
    "shell")
        container_shell "${2:-backend}"
        ;;
    "db")
        db_shell
        ;;
    "migrate")
        run_migrations
        ;;
    "test")
        run_tests "${2:-backend}"
        ;;
    "help"|"-h"|"--help")
        show_usage
        ;;
    *)
        echo "❌ Unknown command: $1"
        show_usage
        exit 1
        ;;
esac
