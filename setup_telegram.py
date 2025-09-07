#!/usr/bin/env python3
"""
Quick setup script for Telegram notifications
"""
import os
import sys
from pathlib import Path

def setup_telegram():
    """Setup Telegram bot for notifications"""
    print("🤖 Telegram Bot Setup for Smart System Health Monitor")
    print("=" * 60)
    
    print("\n📋 Step 1: Create a Telegram Bot")
    print("1. Open Telegram and search for @BotFather")
    print("2. Send /newbot command")
    print("3. Choose a name for your bot (e.g., 'My System Monitor')")
    print("4. Choose a username (e.g., 'my_system_monitor_bot')")
    print("5. Copy the bot token (looks like: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz)")
    
    bot_token = input("\n🔑 Enter your bot token: ").strip()
    
    print("\n📋 Step 2: Get your Chat ID")
    print("1. Send a message to your bot")
    print("2. Open this URL in your browser:")
    print(f"   https://api.telegram.org/bot{bot_token}/getUpdates")
    print("3. Look for 'chat':{'id': YOUR_CHAT_ID}")
    print("4. Copy the chat ID number")
    
    chat_id = input("\n💬 Enter your chat ID: ").strip()
    
    # Create .env file
    env_content = f"""# Smart System Health Monitor Configuration

# Monitoring Settings
MONITORING_INTERVAL=60
LOG_RETENTION_DAYS=30

# Alert Thresholds
CPU_THRESHOLD=80.0
RAM_THRESHOLD=80.0
DISK_THRESHOLD=90.0
NETWORK_THRESHOLD=500000

# Telegram Notifications
TELEGRAM_BOT_TOKEN={bot_token}
TELEGRAM_CHAT_ID={chat_id}

# Email Notifications (Optional)
EMAIL_ENABLED=false
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_TO=recipient@example.com

# Dashboard Settings
DASHBOARD_PORT=8501
DASHBOARD_HOST=0.0.0.0

# Machine Learning Settings
ML_ENABLED=true
PREDICTION_HORIZON=10
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("\n✅ Configuration saved to .env file!")
    
    # Test the setup
    print("\n🧪 Testing Telegram connection...")
    try:
        import requests
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": "🎉 Smart System Health Monitor is now connected! You'll receive alerts when system resources exceed thresholds."
        }
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            print("✅ Telegram test successful! Check your Telegram for the test message.")
        else:
            print(f"❌ Telegram test failed: {response.text}")
    except Exception as e:
        print(f"❌ Error testing Telegram: {e}")
    
    print("\n🚀 Setup complete! Your system will now send Telegram alerts when:")
    print("   • CPU usage > 80%")
    print("   • RAM usage > 80%") 
    print("   • Disk usage > 90%")
    print("   • Network activity > 500MB")

if __name__ == "__main__":
    setup_telegram()
