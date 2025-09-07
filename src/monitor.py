"""
Enhanced system monitoring module with cross-platform support
"""
import platform
import subprocess
import psutil
import time
import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import logging

import sys
from pathlib import Path

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent))

from config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemMonitor:
    """Enhanced system monitor with cross-platform support"""
    
    def __init__(self):
        self.config = Config()
        self.platform = platform.system().lower()
        self._ensure_log_file()
    
    def _ensure_log_file(self):
        """Ensure log file exists with proper headers"""
        if not self.config.LOG_FILE.exists():
            self.config.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config.LOG_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'cpu_usage', 'ram_usage', 'disk_usage', 
                    'network_rx_kb', 'network_tx_kb', 'load_average', 
                    'process_count', 'temperature_c'
                ])
    
    def get_cpu_usage(self) -> float:
        """Get CPU usage percentage"""
        try:
            return psutil.cpu_percent(interval=1)
        except Exception as e:
            logger.error(f"Error getting CPU usage: {e}")
            return 0.0
    
    def get_memory_usage(self) -> float:
        """Get RAM usage percentage"""
        try:
            memory = psutil.virtual_memory()
            return memory.percent
        except Exception as e:
            logger.error(f"Error getting memory usage: {e}")
            return 0.0
    
    def get_disk_usage(self) -> float:
        """Get disk usage percentage"""
        try:
            disk = psutil.disk_usage('/')
            return (disk.used / disk.total) * 100
        except Exception as e:
            logger.error(f"Error getting disk usage: {e}")
            return 0.0
    
    def get_network_usage(self) -> tuple[float, float]:
        """Get network usage in KB (rx, tx)"""
        try:
            net_io = psutil.net_io_counters()
            return net_io.bytes_recv / 1024, net_io.bytes_sent / 1024
        except Exception as e:
            logger.error(f"Error getting network usage: {e}")
            return 0.0, 0.0
    
    def get_load_average(self) -> float:
        """Get system load average"""
        try:
            if self.platform == "linux":
                return os.getloadavg()[0]
            elif self.platform == "darwin":  # macOS
                return os.getloadavg()[0]
            else:  # Windows
                # Windows doesn't have load average, use CPU count as approximation
                return psutil.cpu_count()
        except Exception as e:
            logger.error(f"Error getting load average: {e}")
            return 0.0
    
    def get_process_count(self) -> int:
        """Get number of running processes"""
        try:
            return len(psutil.pids())
        except Exception as e:
            logger.error(f"Error getting process count: {e}")
            return 0
    
    def get_temperature(self) -> Optional[float]:
        """Get CPU temperature if available"""
        try:
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    # Get the first available temperature sensor
                    for name, entries in temps.items():
                        if entries:
                            return entries[0].current
            return None
        except Exception as e:
            logger.error(f"Error getting temperature: {e}")
            return None
    
    def collect_metrics(self) -> Dict[str, Any]:
        """Collect all system metrics"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        network_rx, network_tx = self.get_network_usage()
        temperature = self.get_temperature()
        
        metrics = {
            'timestamp': timestamp,
            'cpu_usage': self.get_cpu_usage(),
            'ram_usage': self.get_memory_usage(),
            'disk_usage': self.get_disk_usage(),
            'network_rx_kb': network_rx,
            'network_tx_kb': network_tx,
            'load_average': self.get_load_average(),
            'process_count': self.get_process_count(),
            'temperature_c': temperature if temperature is not None else 0.0
        }
        
        return metrics
    
    def log_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Log metrics to CSV file"""
        try:
            with open(self.config.LOG_FILE, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    metrics['timestamp'],
                    metrics['cpu_usage'],
                    metrics['ram_usage'],
                    metrics['disk_usage'],
                    metrics['network_rx_kb'],
                    metrics['network_tx_kb'],
                    metrics['load_average'],
                    metrics['process_count'],
                    metrics['temperature_c']
                ])
            return True
        except Exception as e:
            logger.error(f"Error logging metrics: {e}")
            return False
    
    def check_thresholds(self, metrics: Dict[str, Any]) -> list[str]:
        """Check if any metrics exceed thresholds"""
        alerts = []
        
        if metrics['cpu_usage'] > self.config.CPU_THRESHOLD:
            alerts.append(f"🚨 High CPU Usage: {metrics['cpu_usage']:.1f}%")
        
        if metrics['ram_usage'] > self.config.RAM_THRESHOLD:
            alerts.append(f"🚨 High RAM Usage: {metrics['ram_usage']:.1f}%")
        
        if metrics['disk_usage'] > self.config.DISK_THRESHOLD:
            alerts.append(f"🚨 High Disk Usage: {metrics['disk_usage']:.1f}%")
        
        network_total = metrics['network_rx_kb'] + metrics['network_tx_kb']
        if network_total > self.config.NETWORK_THRESHOLD:
            alerts.append(f"🚨 High Network Activity: {network_total:.0f} KB")
        
        return alerts
    
    def cleanup_old_logs(self):
        """Remove log entries older than retention period"""
        try:
            if not self.config.LOG_FILE.exists():
                return
            
            cutoff_date = datetime.now().timestamp() - (self.config.LOG_RETENTION_DAYS * 24 * 3600)
            
            # Read all lines
            with open(self.config.LOG_FILE, 'r') as f:
                lines = f.readlines()
            
            # Keep header and recent lines
            header = lines[0]
            recent_lines = [header]
            
            for line in lines[1:]:
                try:
                    timestamp_str = line.split(',')[0]
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    if timestamp.timestamp() > cutoff_date:
                        recent_lines.append(line)
                except:
                    # Skip malformed lines
                    continue
            
            # Write back filtered lines
            with open(self.config.LOG_FILE, 'w') as f:
                f.writelines(recent_lines)
                
            logger.info(f"Cleaned up old logs, kept {len(recent_lines)-1} recent entries")
            
        except Exception as e:
            logger.error(f"Error cleaning up logs: {e}")
    
    def run_monitoring_cycle(self) -> Dict[str, Any]:
        """Run a complete monitoring cycle"""
        logger.info("Starting monitoring cycle...")
        
        # Collect metrics
        metrics = self.collect_metrics()
        
        # Log metrics
        success = self.log_metrics(metrics)
        if not success:
            logger.error("Failed to log metrics")
        
        # Check thresholds
        alerts = self.check_thresholds(metrics)
        
        # Cleanup old logs (run occasionally)
        if int(time.time()) % 3600 == 0:  # Every hour
            self.cleanup_old_logs()
        
        result = {
            'metrics': metrics,
            'alerts': alerts,
            'logged': success
        }
        
        logger.info(f"Monitoring cycle completed. Alerts: {len(alerts)}")
        return result

def main():
    """Main function for standalone monitoring"""
    monitor = SystemMonitor()
    result = monitor.run_monitoring_cycle()
    
    # Print results
    print(f"Timestamp: {result['metrics']['timestamp']}")
    print(f"CPU: {result['metrics']['cpu_usage']:.1f}%")
    print(f"RAM: {result['metrics']['ram_usage']:.1f}%")
    print(f"Disk: {result['metrics']['disk_usage']:.1f}%")
    print(f"Network: {result['metrics']['network_rx_kb']:.0f} KB RX, {result['metrics']['network_tx_kb']:.0f} KB TX")
    
    if result['alerts']:
        print("\n🚨 ALERTS:")
        for alert in result['alerts']:
            print(f"  {alert}")

if __name__ == "__main__":
    main()
