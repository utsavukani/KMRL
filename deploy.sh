#!/bin/bash
# KMRL System Deployment Script
# SIH25081 - Automated deployment and verification

set -e  # Exit on any error

echo "🚄 KMRL Train Optimization System - Deployment Script"
echo "===================================================="
echo "SIH25081 - Smart India Hackathon 2024"
echo

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check if Python is installed
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_status "Python found: $PYTHON_VERSION"
    else
        print_error "Python 3 is required but not installed"
        exit 1
    fi
}

# Check if Node.js is installed (optional for development)
check_node() {
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_status "Node.js found: $NODE_VERSION"
    else
        print_warning "Node.js not found (optional for development)"
    fi
}

# Create virtual environment
create_venv() {
    print_info "Creating Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_status "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
}

# Activate virtual environment and install dependencies
install_dependencies() {
    print_info "Installing Python dependencies..."
    
    # Activate virtual environment
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    if [ -f "deployment/requirements.txt" ]; then
        pip install -r deployment/requirements.txt
        print_status "Dependencies installed from requirements.txt"
    else
        print_warning "requirements.txt not found, installing core dependencies..."
        pip install fastapi uvicorn pandas numpy scikit-learn xgboost ortools aiofiles aiosqlite
    fi
}

# Generate synthetic data
generate_data() {
    print_info "Generating synthetic training data..."
    
    cd data
    python generate_synthetic_data.py
    
    if [ -f "synthetic_trains.csv" ]; then
        print_status "Synthetic data generated successfully"
        echo "  - $(wc -l < synthetic_trains.csv) train records"
        echo "  - $(wc -l < synthetic_historical_performance.csv) historical records"
    else
        print_error "Failed to generate synthetic data"
        exit 1
    fi
    
    cd ..
}

# Test system components
test_system() {
    print_info "Running system tests..."
    
    # Run integration tests
    python integration_test.py
    
    if [ $? -eq 0 ]; then
        print_status "All tests passed"
    else
        print_error "Some tests failed"
        echo "Check test_report.json for details"
        exit 1
    fi
}

# Start backend server
start_backend() {
    print_info "Starting backend server..."
    
    cd backend
    
    # Check if server is already running
    if curl -s http://localhost:8000/health &> /dev/null; then
        print_warning "Backend server already running on port 8000"
    else
        # Start server in background
        nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
        
        # Wait for server to start
        for i in {1..10}; do
            if curl -s http://localhost:8000/health &> /dev/null; then
                print_status "Backend server started on http://localhost:8000"
                break
            fi
            sleep 2
        done
        
        if ! curl -s http://localhost:8000/health &> /dev/null; then
            print_error "Failed to start backend server"
            exit 1
        fi
    fi
    
    cd ..
}

# Start frontend server (simple HTTP server)
start_frontend() {
    print_info "Starting frontend server..."
    
    cd frontend
    
    # Check if port 3000 is available
    if lsof -Pi :3000 -sTCP:LISTEN -t &> /dev/null; then
        print_warning "Frontend server already running on port 3000"
    else
        # Start simple HTTP server
        if command -v python3 &> /dev/null; then
            nohup python3 -m http.server 3000 > ../frontend.log 2>&1 &
            print_status "Frontend server started on http://localhost:3000"
        elif command -v python &> /dev/null; then
            nohup python -m SimpleHTTPServer 3000 > ../frontend.log 2>&1 &
            print_status "Frontend server started on http://localhost:3000"
        else
            print_warning "Could not start frontend server - Python not found"
        fi
    fi
    
    cd ..
}

# Display system status
show_status() {
    echo
    print_info "System Status:"
    echo "=============="
    
    # Check backend
    if curl -s http://localhost:8000/health &> /dev/null; then
        print_status "Backend API: http://localhost:8000"
        echo "  - Health: http://localhost:8000/health"
        echo "  - API Docs: http://localhost:8000/docs"
    else
        print_error "Backend API: Not responding"
    fi
    
    # Check frontend
    if curl -s http://localhost:3000 &> /dev/null; then
        print_status "Frontend Dashboard: http://localhost:3000"
    else
        print_warning "Frontend: Not accessible"
    fi
    
    echo
    print_info "Log Files:"
    echo "=========="
    echo "  - Backend: backend.log"
    echo "  - Frontend: frontend.log"
    echo "  - Tests: test_report.json"
    
    echo
    print_info "Quick Test Commands:"
    echo "==================="
    echo "  curl http://localhost:8000/health"
    echo "  python integration_test.py"
    echo
}

# Stop servers
stop_servers() {
    print_info "Stopping servers..."
    
    # Stop backend
    pkill -f "uvicorn main:app" && print_status "Backend stopped" || print_warning "Backend not running"
    
    # Stop frontend
    pkill -f "python.*http.server" && print_status "Frontend stopped" || print_warning "Frontend not running"
}

# Cleanup function
cleanup() {
    print_info "Cleaning up temporary files..."
    
    # Remove log files
    [ -f "backend.log" ] && rm backend.log
    [ -f "frontend.log" ] && rm frontend.log
    
    # Remove test reports
    [ -f "test_report.json" ] && rm test_report.json
    
    print_status "Cleanup completed"
}

# Main deployment function
deploy() {
    echo "Starting deployment process..."
    echo
    
    # Pre-deployment checks
    check_python
    check_node
    
    # Setup environment
    create_venv
    install_dependencies
    
    # Generate data
    generate_data
    
    # Test system
    test_system
    
    # Start services
    start_backend
    start_frontend
    
    # Show status
    show_status
    
    print_status "Deployment completed successfully!"
    echo
    echo "🌟 KMRL Train Optimization System is now running!"
    echo "📊 Open http://localhost:3000 to view the dashboard"
    echo "🔧 API documentation available at http://localhost:8000/docs"
    echo
}

# Command line argument handling
case "${1:-deploy}" in
    "deploy"|"start")
        deploy
        ;;
    "stop")
        stop_servers
        ;;
    "restart")
        stop_servers
        sleep 2
        deploy
        ;;
    "test")
        python integration_test.py
        ;;
    "clean")
        cleanup
        ;;
    "status")
        show_status
        ;;
    "help"|"--help"|"-h")
        echo "KMRL Deployment Script - Usage:"
        echo
        echo "  ./deploy.sh [command]"
        echo
        echo "Commands:"
        echo "  deploy, start  - Deploy and start the system (default)"
        echo "  stop          - Stop all services"
        echo "  restart       - Stop and restart all services"
        echo "  test          - Run integration tests"
        echo "  status        - Show system status"
        echo "  clean         - Clean up temporary files"
        echo "  help          - Show this help message"
        echo
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use './deploy.sh help' for usage information"
        exit 1
        ;;
esac