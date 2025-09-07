"""
Configuration management for Smart System Health Monitor
"""
import os
from pathlib import Path
from typing import Dict, Any

class Config:
    """Configuration class for the Smart System Health Monitor"""
    
    # Project paths
    PROJECT_ROOT = Path(__file__).parent
    LOGS_DIR = PROJECT_ROOT / "logs"
    MODELS_DIR = PROJECT_ROOT / "models"
    CONFIG_DIR = PROJECT_ROOT / "config"
    
    # File paths
    LOG_FILE = LOGS_DIR / "system_metrics.csv"
    MODEL_FILE = MODELS_DIR / "cpu_predictor.pkl"
    ENV_FILE = PROJECT_ROOT / ".env"
    
    # Monitoring settings
    MONITORING_INTERVAL = int(os.getenv("MONITORING_INTERVAL", "300"))  # 5 minutes
    LOG_RETENTION_DAYS = int(os.getenv("LOG_RETENTION_DAYS", "30"))
    
    # Alert thresholds
    CPU_THRESHOLD = float(os.getenv("CPU_THRESHOLD", "80.0"))
    RAM_THRESHOLD = float(os.getenv("RAM_THRESHOLD", "80.0"))
    DISK_THRESHOLD = float(os.getenv("DISK_THRESHOLD", "90.0"))
    NETWORK_THRESHOLD = int(os.getenv("NETWORK_THRESHOLD", "500000"))  # KB
    
    # Telegram settings
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    # Email settings (optional)
    EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    EMAIL_TO = os.getenv("EMAIL_TO")
    
    # Dashboard settings
    DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8501"))
    DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "0.0.0.0")
    
    # ML settings
    ML_ENABLED = os.getenv("ML_ENABLED", "true").lower() == "true"
    PREDICTION_HORIZON = int(os.getenv("PREDICTION_HORIZON", "10"))  # minutes
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.LOGS_DIR.mkdir(exist_ok=True)
        cls.MODELS_DIR.mkdir(exist_ok=True)
        cls.CONFIG_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def get_dashboard_config(cls) -> Dict[str, Any]:
        """Get dashboard configuration"""
        return {
            "page_title": "Smart System Health Monitor",
            "page_icon": "💻",
            "layout": "wide",
            "initial_sidebar_state": "expanded"
        }
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration settings"""
        errors = []
        
        if cls.TELEGRAM_BOT_TOKEN and not cls.TELEGRAM_CHAT_ID:
            errors.append("TELEGRAM_CHAT_ID is required when TELEGRAM_BOT_TOKEN is set")
        
        if cls.EMAIL_ENABLED:
            required_email_fields = [cls.SMTP_SERVER, cls.EMAIL_USER, cls.EMAIL_PASSWORD, cls.EMAIL_TO]
            if not all(required_email_fields):
                errors.append("All email settings are required when EMAIL_ENABLED is true")
        
        if errors:
            print("Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True

# Create directories on import
Config.create_directories()
