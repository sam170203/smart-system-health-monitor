"""
Enhanced alerting system with multiple notification channels
"""
import os
import smtplib
import requests
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

import sys
from pathlib import Path

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent))

from config import Config

logger = logging.getLogger(__name__)

class AlertManager:
    """Enhanced alert manager with multiple notification channels"""
    
    def __init__(self):
        self.config = Config()
        self.alert_history = []
        
        # Reload environment variables to pick up .env changes
        from dotenv import load_dotenv
        load_dotenv()
        
        # Update config with fresh environment variables
        self.config.TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        self.config.TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    def send_telegram_alert(self, message: str, parse_mode: str = "Markdown") -> bool:
        """Send alert via Telegram"""
        if not self.config.TELEGRAM_BOT_TOKEN or not self.config.TELEGRAM_CHAT_ID:
            logger.warning("Telegram credentials not configured")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.config.TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {
                "chat_id": self.config.TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": parse_mode
            }
            
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            
            logger.info("Telegram alert sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
            return False
    
    def send_email_alert(self, subject: str, message: str) -> bool:
        """Send alert via email"""
        if not self.config.EMAIL_ENABLED:
            logger.warning("Email alerts not enabled")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.EMAIL_USER
            msg['To'] = self.config.EMAIL_TO
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'html'))
            
            server = smtplib.SMTP(self.config.SMTP_SERVER, self.config.SMTP_PORT)
            server.starttls()
            server.login(self.config.EMAIL_USER, self.config.EMAIL_PASSWORD)
            
            text = msg.as_string()
            server.sendmail(self.config.EMAIL_USER, self.config.EMAIL_TO, text)
            server.quit()
            
            logger.info("Email alert sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False
    
    def send_webhook_alert(self, webhook_url: str, data: Dict[str, Any]) -> bool:
        """Send alert via webhook"""
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(webhook_url, json=data, headers=headers, timeout=10)
            response.raise_for_status()
            
            logger.info("Webhook alert sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
            return False
    
    def format_alert_message(self, alerts: List[str], metrics: Dict[str, Any]) -> str:
        """Format alert message with system information"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message = f"🚨 **System Health Alert** - {timestamp}\n\n"
        
        # Add system metrics
        message += "📊 **Current System Status:**\n"
        message += f"• CPU: {metrics.get('cpu_usage', 0):.1f}%\n"
        message += f"• RAM: {metrics.get('ram_usage', 0):.1f}%\n"
        message += f"• Disk: {metrics.get('disk_usage', 0):.1f}%\n"
        message += f"• Network: {metrics.get('network_rx_kb', 0):.0f} KB RX, {metrics.get('network_tx_kb', 0):.0f} KB TX\n"
        
        if metrics.get('temperature_c', 0) > 0:
            message += f"• Temperature: {metrics['temperature_c']:.1f}°C\n"
        
        message += f"• Load Average: {metrics.get('load_average', 0):.2f}\n"
        message += f"• Processes: {metrics.get('process_count', 0)}\n\n"
        
        # Add alerts
        message += "⚠️ **Alerts:**\n"
        for alert in alerts:
            message += f"• {alert}\n"
        
        # Add recommendations
        message += "\n💡 **Recommendations:**\n"
        if metrics.get('cpu_usage', 0) > 80:
            message += "• Check for CPU-intensive processes\n"
            message += "• Consider closing unnecessary applications\n"
        
        if metrics.get('ram_usage', 0) > 80:
            message += "• Monitor memory usage with `htop` or `top`\n"
            message += "• Consider restarting memory-heavy applications\n"
        
        if metrics.get('disk_usage', 0) > 90:
            message += "• Clean up temporary files\n"
            message += "• Check for large files with `du -sh *`\n"
        
        return message
    
    def send_alerts(self, alerts: List[str], metrics: Dict[str, Any]) -> Dict[str, bool]:
        """Send alerts through all configured channels"""
        if not alerts:
            return {}
        
        results = {}
        
        # Format message
        message = self.format_alert_message(alerts, metrics)
        subject = f"System Health Alert - {len(alerts)} issue(s) detected"
        
        # Send via Telegram
        results['telegram'] = self.send_telegram_alert(message)
        
        # Send via Email
        results['email'] = self.send_email_alert(subject, message.replace('*', '').replace('`', ''))
        
        # Log alert history
        self.alert_history.append({
            'timestamp': datetime.now(),
            'alerts': alerts,
            'metrics': metrics,
            'results': results
        })
        
        # Keep only last 100 alerts in history
        if len(self.alert_history) > 100:
            self.alert_history = self.alert_history[-100:]
        
        return results
    
    def get_alert_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent alert history"""
        return self.alert_history[-limit:] if self.alert_history else []
    
    def test_notifications(self) -> Dict[str, bool]:
        """Test all configured notification channels"""
        test_message = "🧪 **Test Alert** - Smart System Health Monitor is working correctly!"
        test_metrics = {
            'cpu_usage': 25.0,
            'ram_usage': 45.0,
            'disk_usage': 60.0,
            'network_rx_kb': 1000,
            'network_tx_kb': 500,
            'load_average': 1.2,
            'process_count': 150,
            'temperature_c': 45.0
        }
        
        return self.send_alerts([test_message], test_metrics)

def main():
    """Test the alert system"""
    alert_manager = AlertManager()
    
    print("Testing notification channels...")
    results = alert_manager.test_notifications()
    
    for channel, success in results.items():
        status = "✅ Success" if success else "❌ Failed"
        print(f"{channel.capitalize()}: {status}")

if __name__ == "__main__":
    main()
