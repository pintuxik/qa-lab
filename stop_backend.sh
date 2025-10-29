#!/bin/bash
#
# Script to stop backend API and optionally clean up database
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# Function to display usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Stop backend API and optionally clean up database

OPTIONS:
    -h, --help              Show this help message
    -d, --database          Also stop and remove database container
    -c, --clean             Clean up everything (backend + database + logs)
    -f, --force             Force kill processes without confirmation

EXAMPLES:
    # Stop backend only
    $0

    # Stop backend and database
    $0 --database

    # Clean up everything
    $0 --clean

    # Force stop without confirmation
    $0 --force

EOF
    exit 0
}

# Function to stop backend process
stop_backend() {
    print_info "Stopping backend API..."
    
    # Check if backend.pid exists
    if [ -f backend.pid ]; then
        PID=$(cat backend.pid)
        if ps -p ${PID} > /dev/null 2>&1; then
            kill ${PID}
            print_info "Backend API stopped (PID: ${PID})"
        else
            print_warning "Backend process not found (PID: ${PID})"
        fi
        rm backend.pid
    else
        print_warning "No backend.pid file found"
    fi
    
    # Also kill any uvicorn processes
    if pgrep -f "uvicorn app.main:app" > /dev/null; then
        print_info "Killing remaining uvicorn processes..."
        pkill -f "uvicorn app.main:app"
        print_info "All uvicorn processes stopped"
    fi
}

# Function to stop database
stop_database() {
    print_info "Stopping PostgreSQL database..."
    
    if docker ps --format '{{.Names}}' | grep -q "^qa-lab-postgres$"; then
        docker stop qa-lab-postgres
        print_info "PostgreSQL container stopped"
    else
        print_warning "PostgreSQL container not running"
    fi
}

# Function to remove database
remove_database() {
    print_info "Removing PostgreSQL database container..."
    
    if docker ps -a --format '{{.Names}}' | grep -q "^qa-lab-postgres$"; then
        docker rm qa-lab-postgres
        print_info "PostgreSQL container removed"
    else
        print_warning "PostgreSQL container not found"
    fi
}

# Function to clean up logs
cleanup_logs() {
    print_info "Cleaning up log files..."
    
    if [ -f backend.log ]; then
        rm backend.log
        print_info "backend.log removed"
    fi
    
    if [ -f backend.pid ]; then
        rm backend.pid
        print_info "backend.pid removed"
    fi
}

# Function to stop docker-compose services
stop_docker_compose() {
    print_info "Stopping docker-compose services..."
    
    if [ -f docker-compose.yml ]; then
        docker compose down
        print_info "Docker compose services stopped"
    else
        print_warning "docker-compose.yml not found"
    fi
}

# Main execution
STOP_DATABASE=false
CLEAN_ALL=false
FORCE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            ;;
        -d|--database)
            STOP_DATABASE=true
            shift
            ;;
        -c|--clean)
            CLEAN_ALL=true
            shift
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            ;;
    esac
done

# Confirmation if not forced
if [ "$FORCE" = false ] && [ "$CLEAN_ALL" = true ]; then
    echo -e "${YELLOW}WARNING:${NC} This will stop backend, database, and remove all data."
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Operation cancelled"
        exit 0
    fi
fi

print_info "=== Stopping Backend Services ==="

# Stop backend
stop_backend

# Stop database if requested
if [ "$STOP_DATABASE" = true ] || [ "$CLEAN_ALL" = true ]; then
    stop_database
fi

# Clean up if requested
if [ "$CLEAN_ALL" = true ]; then
    remove_database
    cleanup_logs
    
    # Also try to stop docker-compose if it's running
    if docker compose ps 2>/dev/null | grep -q "Up"; then
        stop_docker_compose
    fi
fi

# Display summary
echo ""
print_info "=== Summary ==="
print_info "Backend API: Stopped"

if [ "$STOP_DATABASE" = true ] || [ "$CLEAN_ALL" = true ]; then
    print_info "PostgreSQL: Stopped"
fi

if [ "$CLEAN_ALL" = true ]; then
    print_info "Database container: Removed"
    print_info "Log files: Cleaned"
fi

echo ""
print_info "To start again: ./setup_backend_for_tests.sh"
