"""
Multi-System Monitoring Support
"""
import json
import requests
import socket
import subprocess
import platform
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path
import threading
import time

logger = logging.getLogger(__name__)

class SystemAgent:
    """Agent for monitoring individual systems"""
    
    def __init__(self, system_id: str, system_name: str, system_type: str = "local"):
        self.system_id = system_id
        self.system_name = system_name
        self.system_type = system_type
        self.last_seen = datetime.now()
        self.status = "online"
        self.metrics = {}
        
    def collect_metrics(self) -> Dict[str, Any]:
        """Collect metrics from the system"""
        try:
            if self.system_type == "local":
                return self._collect_local_metrics()
            elif self.system_type == "remote":
                return self._collect_remote_metrics()
            elif self.system_type == "docker":
                return self._collect_docker_metrics()
            else:
                return {}
        except Exception as e:
            logger.error(f"Error collecting metrics for {self.system_id}: {e}")
            return {}
    
    def _collect_local_metrics(self) -> Dict[str, Any]:
        """Collect metrics from local system"""
        try:
            # Basic system info
            system_info = {
                'system_id': self.system_id,
                'system_name': self.system_name,
                'timestamp': datetime.now().isoformat(),
                'platform': platform.system(),
                'platform_version': platform.version(),
                'architecture': platform.machine(),
                'processor': platform.processor(),
                'hostname': socket.gethostname(),
                'status': 'online'
            }
            
            # CPU metrics
            cpu_info = {
                'cpu_usage': psutil.cpu_percent(interval=1),
                'cpu_count': psutil.cpu_count(),
                'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {},
                'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            }
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_info = {
                'ram_usage': memory.percent,
                'ram_total': memory.total,
                'ram_available': memory.available,
                'ram_used': memory.used,
                'ram_free': memory.free
            }
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_info = {
                'disk_usage': (disk.used / disk.total) * 100,
                'disk_total': disk.total,
                'disk_used': disk.used,
                'disk_free': disk.free
            }
            
            # Network metrics
            network = psutil.net_io_counters()
            network_info = {
                'network_rx_kb': network.bytes_recv / 1024,
                'network_tx_kb': network.bytes_sent / 1024,
                'network_packets_sent': network.packets_sent,
                'network_packets_recv': network.packets_recv
            }
            
            # Process metrics
            process_info = {
                'process_count': len(psutil.pids()),
                'top_processes': self._get_top_processes()
            }
            
            # Temperature (if available)
            temperature_info = {}
            try:
                if hasattr(psutil, "sensors_temperatures"):
                    temps = psutil.sensors_temperatures()
                    if temps:
                        for name, entries in temps.items():
                            if entries:
                                temperature_info[f'temperature_{name}'] = entries[0].current
            except:
                pass
            
            # Combine all metrics
            metrics = {
                **system_info,
                **cpu_info,
                **memory_info,
                **disk_info,
                **network_info,
                **process_info,
                **temperature_info
            }
            
            self.metrics = metrics
            self.last_seen = datetime.now()
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting local metrics: {e}")
            return {'error': str(e), 'status': 'error'}
    
    def _collect_remote_metrics(self) -> Dict[str, Any]:
        """Collect metrics from remote system via API"""
        try:
            # This would typically make an HTTP request to a remote monitoring endpoint
            # For now, return a placeholder
            return {
                'system_id': self.system_id,
                'system_name': self.system_name,
                'timestamp': datetime.now().isoformat(),
                'status': 'remote',
                'error': 'Remote monitoring not implemented yet'
            }
        except Exception as e:
            logger.error(f"Error collecting remote metrics: {e}")
            return {'error': str(e), 'status': 'error'}
    
    def _collect_docker_metrics(self) -> Dict[str, Any]:
        """Collect metrics from Docker container"""
        try:
            # This would use Docker API to collect container metrics
            # For now, return a placeholder
            return {
                'system_id': self.system_id,
                'system_name': self.system_name,
                'timestamp': datetime.now().isoformat(),
                'status': 'docker',
                'error': 'Docker monitoring not implemented yet'
            }
        except Exception as e:
            logger.error(f"Error collecting Docker metrics: {e}")
            return {'error': str(e), 'status': 'error'}
    
    def _get_top_processes(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top processes by CPU usage"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] is not None:
                        processes.append({
                            'pid': proc_info['pid'],
                            'name': proc_info['name'],
                            'cpu_percent': proc_info['cpu_percent'],
                            'memory_percent': proc_info['memory_percent']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage and return top processes
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            return processes[:limit]
            
        except Exception as e:
            logger.error(f"Error getting top processes: {e}")
            return []

class MultiSystemMonitor:
    """Monitor multiple systems simultaneously"""
    
    def __init__(self):
        self.systems: Dict[str, SystemAgent] = {}
        self.monitoring_thread = None
        self.is_monitoring = False
        self.monitoring_interval = 60  # seconds
        self.data_file = Path("logs/multi_system_data.json")
        self.data_file.parent.mkdir(exist_ok=True)
        
    def add_system(self, system_id: str, system_name: str, system_type: str = "local") -> bool:
        """Add a system to monitor"""
        try:
            if system_id in self.systems:
                logger.warning(f"System {system_id} already exists")
                return False
            
            agent = SystemAgent(system_id, system_name, system_type)
            self.systems[system_id] = agent
            
            logger.info(f"Added system: {system_id} ({system_name})")
            return True
            
        except Exception as e:
            logger.error(f"Error adding system {system_id}: {e}")
            return False
    
    def remove_system(self, system_id: str) -> bool:
        """Remove a system from monitoring"""
        try:
            if system_id in self.systems:
                del self.systems[system_id]
                logger.info(f"Removed system: {system_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing system {system_id}: {e}")
            return False
    
    def get_system_list(self) -> List[Dict[str, Any]]:
        """Get list of all monitored systems"""
        systems = []
        for system_id, agent in self.systems.items():
            systems.append({
                'system_id': system_id,
                'system_name': agent.system_name,
                'system_type': agent.system_type,
                'status': agent.status,
                'last_seen': agent.last_seen.isoformat(),
                'metrics_count': len(agent.metrics)
            })
        return systems
    
    def collect_all_metrics(self) -> Dict[str, Any]:
        """Collect metrics from all systems"""
        all_metrics = {
            'timestamp': datetime.now().isoformat(),
            'total_systems': len(self.systems),
            'systems': {}
        }
        
        for system_id, agent in self.systems.items():
            try:
                metrics = agent.collect_metrics()
                all_metrics['systems'][system_id] = metrics
                
                # Update agent status
                if 'error' in metrics:
                    agent.status = 'error'
                else:
                    agent.status = 'online'
                    
            except Exception as e:
                logger.error(f"Error collecting metrics from {system_id}: {e}")
                all_metrics['systems'][system_id] = {
                    'error': str(e),
                    'status': 'error',
                    'timestamp': datetime.now().isoformat()
                }
                agent.status = 'error'
        
        return all_metrics
    
    def start_monitoring(self, interval: int = 60):
        """Start continuous monitoring of all systems"""
        if self.is_monitoring:
            logger.warning("Monitoring is already running")
            return
        
        self.monitoring_interval = interval
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info(f"Started monitoring {len(self.systems)} systems with {interval}s interval")
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        logger.info("Stopped monitoring")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Collect metrics from all systems
                all_metrics = self.collect_all_metrics()
                
                # Save to file
                self._save_metrics(all_metrics)
                
                # Wait for next interval
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)  # Wait a bit before retrying
    
    def _save_metrics(self, metrics: Dict[str, Any]):
        """Save metrics to file"""
        try:
            # Load existing data
            if self.data_file.exists():
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {'metrics': []}
            
            # Add new metrics
            data['metrics'].append(metrics)
            
            # Keep only last 1000 entries
            if len(data['metrics']) > 1000:
                data['metrics'] = data['metrics'][-1000:]
            
            # Save to file
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")
    
    def get_historical_data(self, system_id: Optional[str] = None, hours: int = 24) -> Dict[str, Any]:
        """Get historical data for systems"""
        try:
            if not self.data_file.exists():
                return {'metrics': []}
            
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            # Filter by time
            cutoff_time = datetime.now() - timedelta(hours=hours)
            filtered_metrics = []
            
            for metric_entry in data.get('metrics', []):
                try:
                    entry_time = datetime.fromisoformat(metric_entry['timestamp'])
                    if entry_time >= cutoff_time:
                        if system_id is None or system_id in metric_entry.get('systems', {}):
                            filtered_metrics.append(metric_entry)
                except:
                    continue
            
            return {'metrics': filtered_metrics}
            
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return {'error': str(e)}
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get summary of all systems"""
        summary = {
            'total_systems': len(self.systems),
            'online_systems': 0,
            'error_systems': 0,
            'systems': []
        }
        
        for system_id, agent in self.systems.items():
            system_summary = {
                'system_id': system_id,
                'system_name': agent.system_name,
                'system_type': agent.system_type,
                'status': agent.status,
                'last_seen': agent.last_seen.isoformat(),
                'uptime': (datetime.now() - agent.last_seen).total_seconds()
            }
            
            # Add latest metrics if available
            if agent.metrics:
                system_summary['latest_metrics'] = {
                    'cpu_usage': agent.metrics.get('cpu_usage', 0),
                    'ram_usage': agent.metrics.get('ram_usage', 0),
                    'disk_usage': agent.metrics.get('disk_usage', 0)
                }
            
            summary['systems'].append(system_summary)
            
            # Count statuses
            if agent.status == 'online':
                summary['online_systems'] += 1
            elif agent.status == 'error':
                summary['error_systems'] += 1
        
        return summary
    
    def detect_offline_systems(self, timeout_minutes: int = 5) -> List[str]:
        """Detect systems that haven't reported in recently"""
        offline_systems = []
        cutoff_time = datetime.now() - timedelta(minutes=timeout_minutes)
        
        for system_id, agent in self.systems.items():
            if agent.last_seen < cutoff_time:
                offline_systems.append(system_id)
                agent.status = 'offline'
        
        return offline_systems
    
    def export_system_data(self, system_id: str, format: str = 'json') -> str:
        """Export data for a specific system"""
        try:
            historical_data = self.get_historical_data(system_id)
            
            if format == 'json':
                return json.dumps(historical_data, indent=2)
            elif format == 'csv':
                # Convert to CSV format
                csv_data = []
                for entry in historical_data.get('metrics', []):
                    if system_id in entry.get('systems', {}):
                        system_data = entry['systems'][system_id]
                        csv_data.append({
                            'timestamp': entry['timestamp'],
                            'system_id': system_id,
                            'cpu_usage': system_data.get('cpu_usage', ''),
                            'ram_usage': system_data.get('ram_usage', ''),
                            'disk_usage': system_data.get('disk_usage', ''),
                            'status': system_data.get('status', '')
                        })
                
                # Convert to CSV string
                if csv_data:
                    import pandas as pd
                    df = pd.DataFrame(csv_data)
                    return df.to_csv(index=False)
                else:
                    return "No data available"
            else:
                return "Unsupported format"
                
        except Exception as e:
            logger.error(f"Error exporting data for {system_id}: {e}")
            return f"Error: {str(e)}"
