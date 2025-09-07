#!/usr/bin/env python3
"""
Setup script for Smart System Health Monitor
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def create_directories():
    """Create necessary directories"""
    directories = ['logs', 'models', 'config']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def setup_virtual_environment():
    """Setup virtual environment"""
    if not Path("venv").exists():
        if not run_command("python -m venv venv", "Creating virtual environment"):
            return False
    
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip"):
        return False
    
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies"):
        return False
    
    return True

def setup_environment_file():
    """Setup environment configuration file"""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file with your configuration")
    elif env_file.exists():
        print("✅ .env file already exists")
    else:
        print("⚠️  No .env file found. Please create one manually")

def train_initial_models():
    """Train initial ML models"""
    print("🤖 Training initial ML models...")
    try:
        # Import and train models
        sys.path.append(str(Path(__file__).parent / "src"))
        from src.ml_predictor import MLPredictor
        
        predictor = MLPredictor()
        results = predictor.train_models()
        
        if results['success']:
            print("✅ ML models trained successfully")
            return True
        else:
            print(f"⚠️  ML model training failed: {results['message']}")
            return False
    except Exception as e:
        print(f"⚠️  ML model training failed: {e}")
        return False

def setup_cron_job():
    """Setup cron job for monitoring"""
    if os.name == 'nt':  # Windows
        print("⚠️  Windows detected. Please set up Task Scheduler manually")
        print("   Command: python monitor_enhanced.py")
        print("   Schedule: Every 5 minutes")
        return True
    
    # Unix/Linux/macOS
    cron_command = f"*/5 * * * * cd {Path.cwd()} && python monitor_enhanced.py"
    
    print("📅 Setting up cron job...")
    print(f"   Command: {cron_command}")
    print("   Please add this to your crontab with: crontab -e")
    
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up Smart System Health Monitor...")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Setup virtual environment
    if not setup_virtual_environment():
        print("❌ Virtual environment setup failed")
        sys.exit(1)
    
    # Setup environment file
    setup_environment_file()
    
    # Train initial models (optional)
    train_initial_models()
    
    # Setup cron job
    setup_cron_job()
    
    print("=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your configuration")
    print("2. Set up Telegram bot (optional)")
    print("3. Configure email settings (optional)")
    print("4. Run: streamlit run src/dashboard.py")
    print("5. Set up monitoring cron job")
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main()
