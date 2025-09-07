@echo off
REM Smart System Health Monitor Deployment Script for Windows

echo 🚀 Deploying Smart System Health Monitor...

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)
echo ✅ Docker is installed

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    docker compose version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Docker Compose is not available. Please install Docker Compose first.
        pause
        exit /b 1
    )
)
echo ✅ Docker Compose is available

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found. Creating from template...
    if exist "env.example" (
        copy env.example .env
        echo ⚠️  Please edit .env file with your configuration before continuing
        pause
    ) else (
        echo ❌ env.example file not found. Please create .env file manually.
        pause
        exit /b 1
    )
)

REM Deploy with Docker Compose
echo 🐳 Deploying with Docker Compose...
docker-compose up -d --build

if %errorlevel% equ 0 (
    echo ✅ Services started successfully!
    echo 📊 Dashboard available at: http://localhost:8501
    echo 📋 View logs with: docker-compose logs -f
    echo 🛑 Stop services with: docker-compose down
) else (
    echo ❌ Deployment failed. Check the error messages above.
)

pause
