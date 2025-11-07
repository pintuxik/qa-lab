#!/bin/bash
#
# Setup script for backend API to run integration tests
# This script handles database setup and backend initialization
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DB_CONTAINER_NAME="qa-lab-postgres"
DB_NAME="taskmanager"
DB_USER="postgres"
DB_PASSWORD="password"
DB_PORT="5432"
BACKEND_PORT="8000"

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if Docker is running
check_docker() {
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker."
        exit 1
    fi
    
    print_info "Docker is available ✓"
}

# Function to check if PostgreSQL container is running
check_postgres_container() {
    if docker ps --format '{{.Names}}' | grep -q "^${DB_CONTAINER_NAME}$"; then
        return 0
    else
        return 1
    fi
}

# Function to start PostgreSQL container
start_postgres() {
    print_step "Starting PostgreSQL database..."
    
    # Check if container exists but is stopped
    if docker ps -a --format '{{.Names}}' | grep -q "^${DB_CONTAINER_NAME}$"; then
        if ! check_postgres_container; then
            print_info "Starting existing PostgreSQL container..."
            docker start ${DB_CONTAINER_NAME}
        else
            print_info "PostgreSQL container is already running"
        fi
    else
        print_info "Creating new PostgreSQL container..."
        docker run -d \
            --name ${DB_CONTAINER_NAME} \
            -e POSTGRES_DB=${DB_NAME} \
            -e POSTGRES_USER=${DB_USER} \
            -e POSTGRES_PASSWORD=${DB_PASSWORD} \
            -p ${DB_PORT}:5432 \
            postgres:15
    fi
    
    # Wait for PostgreSQL to be ready
    print_info "Waiting for PostgreSQL to be ready..."
    for i in {1..30}; do
        if docker exec ${DB_CONTAINER_NAME} pg_isready -U ${DB_USER} >/dev/null 2>&1; then
            print_info "PostgreSQL is ready ✓"
            return 0
        fi
        sleep 1
    done
    
    print_error "PostgreSQL failed to start"
    exit 1
}

# Function to initialize database
init_database() {
    print_step "Initializing database..."
    
    cd backend
    
    # Set environment variables
    export DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@localhost:${DB_PORT}/${DB_NAME}"
    export SECRET_KEY="test-secret-key-for-integration-tests"
    export FRONTEND_URL="http://localhost:5001"
    
    # Install dependencies if needed
    if [ ! -d ".venv" ]; then
        print_info "Installing backend dependencies..."
        uv sync --extra test
    fi
    
    # Initialize database (creates tables and admin user)
    print_info "Creating database tables and admin user..."
    uv run python app/init_db.py
    
    print_info "Database initialized ✓"
    cd ..
}

# Function to start backend API
start_backend() {
    print_step "Starting backend API..."
    
    # Check if backend is already running BEFORE changing directory
    if curl -sf http://localhost:${BACKEND_PORT}/health >/dev/null 2>&1; then
        print_info "Backend API is already running on port ${BACKEND_PORT} ✓"
        print_info "Health check: http://localhost:${BACKEND_PORT}/health"
        return 0
    fi
    
    cd backend
    
    # Set environment variables
    export DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@localhost:${DB_PORT}/${DB_NAME}"
    export SECRET_KEY="test-secret-key-for-integration-tests"
    export FRONTEND_URL="http://localhost:5001"
    
    print_info "Starting backend API on port ${BACKEND_PORT}..."
    print_info "Running: uv run uvicorn app.main:app --host 0.0.0.0 --port ${BACKEND_PORT}"
    
    # Start backend in background
    nohup uv run uvicorn app.main:app --host 0.0.0.0 --port ${BACKEND_PORT} > ../backend.log 2>&1 &
    BACKEND_PID=$!
    
    echo ${BACKEND_PID} > ../backend.pid
    
    # Wait for backend to be ready
    print_info "Waiting for backend API to be ready..."
    for i in {1..30}; do
        if curl -sf http://localhost:${BACKEND_PORT}/health >/dev/null 2>&1; then
            print_info "Backend API is ready ✓"
            print_info "Backend PID: ${BACKEND_PID} (saved to backend.pid)"
            print_info "Backend logs: backend.log"
            cd ..
            return 0
        fi
        
        # Check if process is still running
        if ! ps -p ${BACKEND_PID} > /dev/null 2>&1; then
            print_error "Backend process died unexpectedly"
            print_error "Check backend.log for details:"
            if [ -f ../backend.log ]; then
                tail -20 ../backend.log
            fi
            cd ..
            exit 1
        fi
        
        sleep 1
    done
    
    print_error "Backend API failed to start within 30 seconds"
    print_error "Check backend.log for details:"
    if [ -f ../backend.log ]; then
        tail -20 ../backend.log
    fi
    cd ..
    exit 1
}

# Function to display usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Setup backend API for integration tests

OPTIONS:
    -h, --help              Show this help message
    -s, --skip-db           Skip database setup (assumes DB is already running)
    -k, --kill              Kill running backend API
    -c, --clean             Clean up (stop and remove database container)
    -d, --docker-compose    Use docker-compose instead of manual setup

EXAMPLES:
    # Full setup (database + backend)
    $0

    # Skip database setup
    $0 --skip-db

    # Kill running backend
    $0 --kill

    # Clean up everything
    $0 --clean

    # Use docker-compose
    $0 --docker-compose

EOF
    exit 0
}

# Function to kill backend
kill_backend() {
    print_step "Stopping backend API..."
    
    if [ -f backend.pid ]; then
        PID=$(cat backend.pid)
        if ps -p ${PID} > /dev/null 2>&1; then
            kill ${PID}
            print_info "Backend API stopped (PID: ${PID})"
        else
            print_warning "Backend process not found"
        fi
        rm backend.pid
    else
        print_warning "No backend.pid file found"
    fi
}

# Function to clean up
cleanup() {
    print_step "Cleaning up..."
    
    # Stop backend
    kill_backend
    
    # Stop and remove PostgreSQL container
    if docker ps -a --format '{{.Names}}' | grep -q "^${DB_CONTAINER_NAME}$"; then
        print_info "Stopping and removing PostgreSQL container..."
        docker stop ${DB_CONTAINER_NAME} >/dev/null 2>&1 || true
        docker rm ${DB_CONTAINER_NAME} >/dev/null 2>&1 || true
        print_info "PostgreSQL container removed ✓"
    fi
    
    # Remove log file
    if [ -f backend.log ]; then
        rm backend.log
        print_info "Backend log removed"
    fi
    
    print_info "Cleanup complete ✓"
}

# Function to use docker-compose
use_docker_compose() {
    print_step "Using docker-compose..."
    
    if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
        print_error "docker-compose is not available"
        exit 1
    fi
    
    print_info "Starting services with docker-compose..."
    docker compose up -d
    
    print_info "Waiting for backend API to be ready..."
    for i in {1..60}; do
        if curl -sf http://localhost:${BACKEND_PORT}/health >/dev/null 2>&1; then
            print_info "Backend API is ready ✓"
            print_info "View logs: docker compose logs -f backend"
            return 0
        fi
        sleep 1
    done
    
    print_error "Backend API failed to start"
    print_error "Check logs: docker compose logs backend"
    exit 1
}

# Main execution
SKIP_DB=false
USE_DOCKER_COMPOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            ;;
        -s|--skip-db)
            SKIP_DB=true
            shift
            ;;
        -k|--kill)
            kill_backend
            exit 0
            ;;
        -c|--clean)
            cleanup
            exit 0
            ;;
        -d|--docker-compose)
            USE_DOCKER_COMPOSE=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            ;;
    esac
done

# Main setup
print_info "=== Backend Setup for Integration Tests ==="

if [ "$USE_DOCKER_COMPOSE" = true ]; then
    use_docker_compose
    exit 0
fi

# Check Docker
check_docker

# Setup database
if [ "$SKIP_DB" = false ]; then
    start_postgres
    init_database
else
    print_warning "Skipping database setup"
fi

# Start backend
start_backend

# Display summary
echo ""
print_info "=== Setup Complete ==="
print_info "Database: postgresql://localhost:${DB_PORT}/${DB_NAME}"
print_info "Backend API: http://localhost:${BACKEND_PORT}"
print_info "Health Check: http://localhost:${BACKEND_PORT}/health"
echo ""
print_info "You can now run integration tests:"
print_info "  ./run_api_tests.sh"
print_info "  OR"
print_info "  uv run pytest tests/api/ -m integration -v"
echo ""
print_info "To stop the backend: $0 --kill"
print_info "To clean up everything: $0 --clean"
