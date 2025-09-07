"""
AI-Powered Insights and Recommendations Engine
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Insight:
    """Data class for insights"""
    title: str
    description: str
    category: str
    priority: str
    confidence: float
    actionable: bool
    recommendation: str = ""
    impact: str = ""

class AIInsightsEngine:
    """AI-powered insights and recommendations engine"""
    
    def __init__(self):
        self.insight_templates = self._load_insight_templates()
        self.thresholds = {
            'cpu_critical': 90,
            'cpu_warning': 80,
            'ram_critical': 95,
            'ram_warning': 85,
            'disk_critical': 95,
            'disk_warning': 85,
            'network_high': 1000000,  # 1GB
            'temperature_high': 80
        }
    
    def _load_insight_templates(self) -> Dict[str, List[Dict]]:
        """Load insight templates for different scenarios"""
        return {
            'performance': [
                {
                    'condition': lambda data: data['cpu_usage'] > 90,
                    'title': 'Critical CPU Usage',
                    'description': 'CPU usage is critically high and may cause system instability',
                    'priority': 'Critical',
                    'confidence': 0.95,
                    'recommendation': 'Immediately close resource-intensive applications or consider hardware upgrade'
                },
                {
                    'condition': lambda data: data['cpu_usage'] > 80,
                    'title': 'High CPU Usage',
                    'description': 'CPU usage is elevated and may impact system performance',
                    'priority': 'High',
                    'confidence': 0.85,
                    'recommendation': 'Monitor running processes and consider optimizing resource usage'
                },
                {
                    'condition': lambda data: data['ram_usage'] > 95,
                    'title': 'Critical Memory Usage',
                    'description': 'Memory usage is critically high and may cause system crashes',
                    'priority': 'Critical',
                    'confidence': 0.95,
                    'recommendation': 'Free up memory immediately or add more RAM'
                }
            ],
            'capacity': [
                {
                    'condition': lambda data: data['disk_usage'] > 95,
                    'title': 'Critical Disk Space',
                    'description': 'Disk space is critically low and may cause system failures',
                    'priority': 'Critical',
                    'confidence': 0.98,
                    'recommendation': 'Free up disk space immediately or expand storage'
                },
                {
                    'condition': lambda data: data['disk_usage'] > 85,
                    'title': 'Low Disk Space',
                    'description': 'Disk space is running low and should be addressed soon',
                    'priority': 'High',
                    'confidence': 0.80,
                    'recommendation': 'Clean up temporary files and consider storage expansion'
                }
            ],
            'trends': [
                {
                    'condition': lambda data: data.get('cpu_trend', 0) > 5,
                    'title': 'CPU Usage Trending Up',
                    'description': 'CPU usage is showing an upward trend over time',
                    'priority': 'Medium',
                    'confidence': 0.75,
                    'recommendation': 'Investigate the cause of increasing CPU usage'
                },
                {
                    'condition': lambda data: data.get('ram_trend', 0) > 3,
                    'title': 'Memory Usage Trending Up',
                    'description': 'Memory usage is gradually increasing over time',
                    'priority': 'Medium',
                    'confidence': 0.70,
                    'recommendation': 'Monitor for potential memory leaks'
                }
            ],
            'patterns': [
                {
                    'condition': lambda data: data.get('peak_frequency', 0) > 0.1,
                    'title': 'Frequent Performance Peaks',
                    'description': 'System is experiencing frequent performance spikes',
                    'priority': 'Medium',
                    'confidence': 0.65,
                    'recommendation': 'Investigate what causes these performance peaks'
                }
            ]
        }
    
    def generate_insights(self, df: pd.DataFrame, analytics_data: Dict[str, Any]) -> List[Insight]:
        """Generate AI-powered insights from system data and analytics"""
        insights = []
        
        try:
            if df.empty:
                return [Insight(
                    title="No Data Available",
                    description="No system data available for analysis",
                    category="System",
                    priority="Info",
                    confidence=1.0,
                    actionable=False
                )]
            
            # Get latest system state
            latest = df.iloc[-1]
            
            # Calculate trends
            trends = self._calculate_trends(df)
            
            # Calculate patterns
            patterns = self._calculate_patterns(df, analytics_data)
            
            # Generate insights for each category
            insights.extend(self._generate_performance_insights(latest, trends))
            insights.extend(self._generate_capacity_insights(latest, trends))
            insights.extend(self._generate_trend_insights(trends))
            insights.extend(self._generate_pattern_insights(patterns))
            insights.extend(self._generate_anomaly_insights(analytics_data))
            insights.extend(self._generate_optimization_insights(df, latest))
            
            # Sort insights by priority and confidence
            insights.sort(key=lambda x: (self._priority_score(x.priority), -x.confidence))
            
            return insights[:10]  # Return top 10 insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return [Insight(
                title="Analysis Error",
                description=f"Error generating insights: {str(e)}",
                category="System",
                priority="Error",
                confidence=0.0,
                actionable=False
            )]
    
    def _calculate_trends(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate trends for different metrics"""
        trends = {}
        
        try:
            if len(df) < 10:
                return trends
            
            # Calculate trends for key metrics
            for metric in ['cpu_usage', 'ram_usage', 'disk_usage']:
                if metric in df.columns:
                    values = df[metric].values
                    if len(values) > 5:
                        # Simple linear trend
                        x = np.arange(len(values))
                        slope, _, _, _, _ = np.polyfit(x, values, 1)
                        trends[f'{metric}_trend'] = float(slope)
                        
                        # Calculate trend strength
                        recent_avg = values[-5:].mean()
                        early_avg = values[:5].mean()
                        trends[f'{metric}_change'] = float(recent_avg - early_avg)
        
        except Exception as e:
            logger.error(f"Error calculating trends: {e}")
        
        return trends
    
    def _calculate_patterns(self, df: pd.DataFrame, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate patterns from analytics data"""
        patterns = {}
        
        try:
            # Extract patterns from analytics
            if 'patterns' in analytics_data and 'patterns' in analytics_data['patterns']:
                for pattern in analytics_data['patterns']['patterns']:
                    if pattern['type'] == 'peak_detection':
                        patterns['peak_frequency'] = pattern.get('peak_frequency', 0)
                    elif pattern['type'] == 'hourly_pattern':
                        patterns['hourly_peak'] = pattern.get('value', 0)
                    elif pattern['type'] == 'weekend_pattern':
                        patterns['weekend_difference'] = pattern.get('difference', 0)
        
        except Exception as e:
            logger.error(f"Error calculating patterns: {e}")
        
        return patterns
    
    def _generate_performance_insights(self, latest: pd.Series, trends: Dict[str, float]) -> List[Insight]:
        """Generate performance-related insights"""
        insights = []
        
        # CPU insights
        if 'cpu_usage' in latest:
            cpu_usage = latest['cpu_usage']
            cpu_trend = trends.get('cpu_usage_trend', 0)
            
            if cpu_usage > 90:
                insights.append(Insight(
                    title="Critical CPU Usage",
                    description=f"CPU usage is critically high at {cpu_usage:.1f}%",
                    category="Performance",
                    priority="Critical",
                    confidence=0.95,
                    actionable=True,
                    recommendation="Immediately close resource-intensive applications or consider hardware upgrade",
                    impact="System instability and potential crashes"
                ))
            elif cpu_usage > 80:
                insights.append(Insight(
                    title="High CPU Usage",
                    description=f"CPU usage is elevated at {cpu_usage:.1f}%",
                    category="Performance",
                    priority="High",
                    confidence=0.85,
                    actionable=True,
                    recommendation="Monitor running processes and consider optimizing resource usage",
                    impact="Reduced system performance"
                ))
            
            # CPU trend insights
            if cpu_trend > 2:
                insights.append(Insight(
                    title="CPU Usage Trending Up",
                    description="CPU usage is showing a concerning upward trend",
                    category="Performance",
                    priority="Medium",
                    confidence=0.75,
                    actionable=True,
                    recommendation="Investigate what's causing the increasing CPU usage",
                    impact="Potential future performance issues"
                ))
        
        # RAM insights
        if 'ram_usage' in latest:
            ram_usage = latest['ram_usage']
            ram_trend = trends.get('ram_usage_trend', 0)
            
            if ram_usage > 95:
                insights.append(Insight(
                    title="Critical Memory Usage",
                    description=f"Memory usage is critically high at {ram_usage:.1f}%",
                    category="Performance",
                    priority="Critical",
                    confidence=0.95,
                    actionable=True,
                    recommendation="Free up memory immediately or add more RAM",
                    impact="System crashes and data loss"
                ))
            elif ram_usage > 85:
                insights.append(Insight(
                    title="High Memory Usage",
                    description=f"Memory usage is high at {ram_usage:.1f}%",
                    category="Performance",
                    priority="High",
                    confidence=0.80,
                    actionable=True,
                    recommendation="Monitor memory usage and consider adding more RAM",
                    impact="Reduced system performance"
                ))
            
            # RAM trend insights
            if ram_trend > 1:
                insights.append(Insight(
                    title="Memory Usage Trending Up",
                    description="Memory usage is gradually increasing over time",
                    category="Performance",
                    priority="Medium",
                    confidence=0.70,
                    actionable=True,
                    recommendation="Monitor for potential memory leaks",
                    impact="Gradual performance degradation"
                ))
        
        return insights
    
    def _generate_capacity_insights(self, latest: pd.Series, trends: Dict[str, float]) -> List[Insight]:
        """Generate capacity-related insights"""
        insights = []
        
        # Disk space insights
        if 'disk_usage' in latest:
            disk_usage = latest['disk_usage']
            disk_trend = trends.get('disk_usage_trend', 0)
            
            if disk_usage > 95:
                insights.append(Insight(
                    title="Critical Disk Space",
                    description=f"Disk space is critically low at {disk_usage:.1f}% used",
                    category="Capacity",
                    priority="Critical",
                    confidence=0.98,
                    actionable=True,
                    recommendation="Free up disk space immediately or expand storage",
                    impact="System failures and data loss"
                ))
            elif disk_usage > 85:
                insights.append(Insight(
                    title="Low Disk Space",
                    description=f"Disk space is running low at {disk_usage:.1f}% used",
                    category="Capacity",
                    priority="High",
                    confidence=0.80,
                    actionable=True,
                    recommendation="Clean up temporary files and consider storage expansion",
                    impact="Potential system issues"
                ))
            
            # Disk trend insights
            if disk_trend > 0.5:
                insights.append(Insight(
                    title="Disk Usage Growing",
                    description="Disk usage is steadily increasing",
                    category="Capacity",
                    priority="Medium",
                    confidence=0.70,
                    actionable=True,
                    recommendation="Plan for storage expansion or cleanup",
                    impact="Future capacity constraints"
                ))
        
        return insights
    
    def _generate_trend_insights(self, trends: Dict[str, float]) -> List[Insight]:
        """Generate trend-based insights"""
        insights = []
        
        # Overall system health trend
        negative_trends = sum(1 for trend in trends.values() if trend > 0)
        if negative_trends > 2:
            insights.append(Insight(
                title="System Health Declining",
                description="Multiple system metrics are trending in concerning directions",
                category="Trends",
                priority="High",
                confidence=0.80,
                actionable=True,
                recommendation="Conduct comprehensive system analysis and optimization",
                impact="Overall system performance degradation"
            ))
        
        return insights
    
    def _generate_pattern_insights(self, patterns: Dict[str, Any]) -> List[Insight]:
        """Generate pattern-based insights"""
        insights = []
        
        # Peak frequency insights
        if patterns.get('peak_frequency', 0) > 0.1:
            insights.append(Insight(
                title="Frequent Performance Peaks",
                description="System is experiencing frequent performance spikes",
                category="Patterns",
                priority="Medium",
                confidence=0.65,
                actionable=True,
                recommendation="Investigate what causes these performance peaks",
                impact="Inconsistent system performance"
            ))
        
        # Weekend patterns
        if patterns.get('weekend_difference', 0) > 10:
            insights.append(Insight(
                title="Weekend Usage Pattern",
                description="System usage differs significantly between weekdays and weekends",
                category="Patterns",
                priority="Low",
                confidence=0.60,
                actionable=True,
                recommendation="Consider optimizing system resources based on usage patterns",
                impact="Resource utilization optimization"
            ))
        
        return insights
    
    def _generate_anomaly_insights(self, analytics_data: Dict[str, Any]) -> List[Insight]:
        """Generate anomaly-based insights"""
        insights = []
        
        try:
            if 'anomalies' in analytics_data and analytics_data['anomalies'].get('anomalies'):
                anomaly_count = len(analytics_data['anomalies']['anomalies'])
                anomaly_score = analytics_data['anomalies'].get('anomaly_score', 0)
                
                if anomaly_score > 0.1:
                    insights.append(Insight(
                        title="System Anomalies Detected",
                        description=f"Detected {anomaly_count} anomalies in recent system behavior",
                        category="Anomalies",
                        priority="High" if anomaly_score > 0.2 else "Medium",
                        confidence=0.85,
                        actionable=True,
                        recommendation="Investigate the detected anomalies for potential issues",
                        impact="Potential system instability"
                    ))
        
        except Exception as e:
            logger.error(f"Error generating anomaly insights: {e}")
        
        return insights
    
    def _generate_optimization_insights(self, df: pd.DataFrame, latest: pd.Series) -> List[Insight]:
        """Generate optimization recommendations"""
        insights = []
        
        try:
            # Resource optimization insights
            if len(df) > 20:
                # Check for resource waste
                cpu_avg = df['cpu_usage'].mean()
                ram_avg = df['ram_usage'].mean()
                
                if cpu_avg < 30 and ram_avg < 50:
                    insights.append(Insight(
                        title="Underutilized Resources",
                        description="System resources are underutilized",
                        category="Optimization",
                        priority="Low",
                        confidence=0.70,
                        actionable=True,
                        recommendation="Consider running additional workloads or downsizing",
                        impact="Cost optimization opportunity"
                    ))
                
                # Check for consistent high usage
                if cpu_avg > 70 and ram_avg > 70:
                    insights.append(Insight(
                        title="High Resource Utilization",
                        description="System is consistently running at high resource utilization",
                        category="Optimization",
                        priority="Medium",
                        confidence=0.75,
                        actionable=True,
                        recommendation="Consider upgrading hardware or optimizing applications",
                        impact="Better performance and reliability"
                    ))
        
        except Exception as e:
            logger.error(f"Error generating optimization insights: {e}")
        
        return insights
    
    def _priority_score(self, priority: str) -> int:
        """Convert priority to numeric score for sorting"""
        priority_map = {
            'Critical': 1,
            'High': 2,
            'Medium': 3,
            'Low': 4,
            'Info': 5,
            'Error': 6
        }
        return priority_map.get(priority, 5)
    
    def format_insights_for_display(self, insights: List[Insight]) -> Dict[str, Any]:
        """Format insights for dashboard display"""
        formatted = {
            'total_insights': len(insights),
            'critical_count': sum(1 for i in insights if i.priority == 'Critical'),
            'high_count': sum(1 for i in insights if i.priority == 'High'),
            'medium_count': sum(1 for i in insights if i.priority == 'Medium'),
            'insights': []
        }
        
        for insight in insights:
            formatted['insights'].append({
                'title': insight.title,
                'description': insight.description,
                'category': insight.category,
                'priority': insight.priority,
                'confidence': f"{insight.confidence:.0%}",
                'actionable': insight.actionable,
                'recommendation': insight.recommendation,
                'impact': insight.impact,
                'icon': self._get_priority_icon(insight.priority),
                'color': self._get_priority_color(insight.priority)
            })
        
        return formatted
    
    def _get_priority_icon(self, priority: str) -> str:
        """Get icon for priority level"""
        icons = {
            'Critical': '🚨',
            'High': '⚠️',
            'Medium': '📊',
            'Low': '💡',
            'Info': 'ℹ️',
            'Error': '❌'
        }
        return icons.get(priority, 'ℹ️')
    
    def _get_priority_color(self, priority: str) -> str:
        """Get color for priority level"""
        colors = {
            'Critical': 'red',
            'High': 'orange',
            'Medium': 'yellow',
            'Low': 'blue',
            'Info': 'green',
            'Error': 'red'
        }
        return colors.get(priority, 'blue')
