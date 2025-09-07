#!/bin/bash

# Smart System Health Monitor Deployment Script

set -e

echo "🚀 Deploying Smart System Health Monitor..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is installed
check_docker() {
    if command -v docker &> /dev/null; then
        print_status "Docker is installed"
        return 0
    else
        print_error "Docker is not installed. Please install Docker first."
        return 1
    fi
}

# Check if Docker Compose is installed
check_docker_compose() {
    if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
        print_status "Docker Compose is available"
        return 0
    else
        print_error "Docker Compose is not available. Please install Docker Compose first."
        return 1
    fi
}

# Deploy with Docker Compose
deploy_docker_compose() {
    echo "🐳 Deploying with Docker Compose..."
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from template..."
        if [ -f "env.example" ]; then
            cp env.example .env
            print_warning "Please edit .env file with your configuration before continuing"
            read -p "Press Enter to continue after editing .env file..."
        else
            print_error "env.example file not found. Please create .env file manually."
            exit 1
        fi
    fi
    
    # Build and start services
    docker-compose up -d --build
    
    print_status "Services started successfully!"
    echo "📊 Dashboard available at: http://localhost:8501"
    echo "📋 View logs with: docker-compose logs -f"
    echo "🛑 Stop services with: docker-compose down"
}

# Deploy with Docker
deploy_docker() {
    echo "🐳 Deploying with Docker..."
    
    # Build image
    docker build -f Dockerfile.enhanced -t smart-system-monitor .
    
    # Run container
    docker run -d \
        --name smart-system-monitor \
        -p 8501:8501 \
        -v $(pwd)/logs:/app/logs \
        -v $(pwd)/models:/app/models \
        -v $(pwd)/config:/app/config \
        --env-file .env \
        --restart unless-stopped \
        smart-system-monitor
    
    print_status "Container started successfully!"
    echo "📊 Dashboard available at: http://localhost:8501"
    echo "📋 View logs with: docker logs -f smart-system-monitor"
    echo "🛑 Stop container with: docker stop smart-system-monitor"
}

# Deploy locally
deploy_local() {
    echo "💻 Deploying locally..."
    
    # Check Python version
    python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
    required_version="3.8"
    
    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
        print_status "Python version $python_version is compatible"
    else
        print_error "Python 3.8 or higher is required. Current version: $python_version"
        exit 1
    fi
    
    # Install dependencies
    if [ ! -d "venv" ]; then
        print_warning "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Create directories
    mkdir -p logs models config
    
    # Setup environment file
    if [ ! -f ".env" ]; then
        if [ -f "env.example" ]; then
            cp env.example .env
            print_warning "Please edit .env file with your configuration"
        fi
    fi
    
    print_status "Local deployment ready!"
    echo "🚀 Start dashboard with: streamlit run src/dashboard.py"
    echo "📊 Dashboard will be available at: http://localhost:8501"
}

# Main deployment function
main() {
    echo "Smart System Health Monitor Deployment"
    echo "======================================"
    
    # Check deployment method
    if [ "$1" = "docker-compose" ]; then
        if check_docker && check_docker_compose; then
            deploy_docker_compose
        else
            exit 1
        fi
    elif [ "$1" = "docker" ]; then
        if check_docker; then
            deploy_docker
        else
            exit 1
        fi
    elif [ "$1" = "local" ]; then
        deploy_local
    else
        echo "Usage: $0 {docker-compose|docker|local}"
        echo ""
        echo "Options:"
        echo "  docker-compose  Deploy using Docker Compose (recommended)"
        echo "  docker         Deploy using Docker"
        echo "  local          Deploy locally with Python"
        exit 1
    fi
}

# Run main function with all arguments
main "$@"
