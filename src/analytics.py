"""
Advanced Analytics and Anomaly Detection Module
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from scipy import stats
from scipy.signal import find_peaks
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple, Any
import logging
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

class AdvancedAnalytics:
    """Advanced analytics and anomaly detection for system monitoring"""
    
    def __init__(self):
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.anomaly_threshold = 0.1
        
    def detect_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect anomalies in system metrics"""
        try:
            if len(df) < 10:
                return {'anomalies': [], 'anomaly_score': 0, 'message': 'Insufficient data for anomaly detection'}
            
            # Prepare features for anomaly detection
            features = ['cpu_usage', 'ram_usage', 'disk_usage', 'network_rx_kb', 'network_tx_kb']
            available_features = [f for f in features if f in df.columns]
            
            if not available_features:
                return {'anomalies': [], 'anomaly_score': 0, 'message': 'No suitable features for anomaly detection'}
            
            # Scale features
            X = df[available_features].fillna(method='ffill').fillna(method='bfill')
            X_scaled = self.scaler.fit_transform(X)
            
            # Detect anomalies
            anomaly_scores = self.anomaly_detector.fit_predict(X_scaled)
            anomaly_scores_cont = self.anomaly_detector.decision_function(X_scaled)
            
            # Find anomaly indices
            anomaly_indices = np.where(anomaly_scores == -1)[0]
            
            # Create anomaly details
            anomalies = []
            for idx in anomaly_indices:
                if idx < len(df):
                    anomaly_data = {
                        'timestamp': df.iloc[idx]['timestamp'],
                        'anomaly_score': float(anomaly_scores_cont[idx]),
                        'metrics': {feature: float(df.iloc[idx][feature]) for feature in available_features},
                        'severity': 'High' if anomaly_scores_cont[idx] < -0.5 else 'Medium'
                    }
                    anomalies.append(anomaly_data)
            
            # Calculate overall anomaly score
            overall_score = len(anomalies) / len(df) if len(df) > 0 else 0
            
            return {
                'anomalies': anomalies,
                'anomaly_score': overall_score,
                'total_anomalies': len(anomalies),
                'features_analyzed': available_features,
                'message': f'Detected {len(anomalies)} anomalies in {len(df)} data points'
            }
            
        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
            return {'anomalies': [], 'anomaly_score': 0, 'message': f'Anomaly detection failed: {str(e)}'}
    
    def detect_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect patterns and trends in system metrics"""
        try:
            if len(df) < 20:
                return {'patterns': [], 'message': 'Insufficient data for pattern detection'}
            
            patterns = []
            
            # Time-based patterns
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['is_weekend'] = df['day_of_week'].isin([5, 6])
            
            # Analyze CPU patterns
            if 'cpu_usage' in df.columns:
                cpu_patterns = self._analyze_metric_patterns(df, 'cpu_usage')
                patterns.extend(cpu_patterns)
            
            # Analyze RAM patterns
            if 'ram_usage' in df.columns:
                ram_patterns = self._analyze_metric_patterns(df, 'ram_usage')
                patterns.extend(ram_patterns)
            
            # Peak detection
            peak_patterns = self._detect_peaks(df)
            patterns.extend(peak_patterns)
            
            # Trend analysis
            trend_patterns = self._analyze_trends(df)
            patterns.extend(trend_patterns)
            
            return {
                'patterns': patterns,
                'total_patterns': len(patterns),
                'message': f'Detected {len(patterns)} patterns in the data'
            }
            
        except Exception as e:
            logger.error(f"Error in pattern detection: {e}")
            return {'patterns': [], 'message': f'Pattern detection failed: {str(e)}'}
    
    def _analyze_metric_patterns(self, df: pd.DataFrame, metric: str) -> List[Dict]:
        """Analyze patterns for a specific metric"""
        patterns = []
        
        try:
            # Hourly patterns
            hourly_avg = df.groupby('hour')[metric].mean()
            peak_hour = hourly_avg.idxmax()
            low_hour = hourly_avg.idxmin()
            
            if hourly_avg[peak_hour] > hourly_avg.mean() * 1.2:
                patterns.append({
                    'type': 'hourly_pattern',
                    'metric': metric,
                    'description': f'{metric.replace("_", " ").title()} peaks at {peak_hour}:00',
                    'value': float(hourly_avg[peak_hour]),
                    'significance': 'High' if hourly_avg[peak_hour] > hourly_avg.mean() * 1.5 else 'Medium'
                })
            
            # Weekend vs weekday patterns
            if len(df[df['is_weekend'] == True]) > 0 and len(df[df['is_weekend'] == False]) > 0:
                weekend_avg = df[df['is_weekend'] == True][metric].mean()
                weekday_avg = df[df['is_weekend'] == False][metric].mean()
                
                if abs(weekend_avg - weekday_avg) > weekday_avg * 0.2:
                    pattern_type = 'weekend_higher' if weekend_avg > weekday_avg else 'weekday_higher'
                    patterns.append({
                        'type': 'weekend_pattern',
                        'metric': metric,
                        'description': f'{metric.replace("_", " ").title()} is {"higher" if weekend_avg > weekday_avg else "lower"} on weekends',
                        'weekend_avg': float(weekend_avg),
                        'weekday_avg': float(weekday_avg),
                        'difference': float(abs(weekend_avg - weekday_avg)),
                        'significance': 'High' if abs(weekend_avg - weekday_avg) > weekday_avg * 0.3 else 'Medium'
                    })
            
        except Exception as e:
            logger.error(f"Error analyzing {metric} patterns: {e}")
        
        return patterns
    
    def _detect_peaks(self, df: pd.DataFrame) -> List[Dict]:
        """Detect peaks in system metrics"""
        patterns = []
        
        try:
            for metric in ['cpu_usage', 'ram_usage']:
                if metric in df.columns:
                    values = df[metric].values
                    if len(values) > 10:
                        # Find peaks
                        peaks, properties = find_peaks(values, height=np.mean(values) + np.std(values))
                        
                        if len(peaks) > 0:
                            # Analyze peak characteristics
                            peak_values = values[peaks]
                            avg_peak = np.mean(peak_values)
                            peak_frequency = len(peaks) / len(values)
                            
                            patterns.append({
                                'type': 'peak_detection',
                                'metric': metric,
                                'description': f'{len(peaks)} peaks detected in {metric.replace("_", " ").title()}',
                                'peak_count': len(peaks),
                                'avg_peak_value': float(avg_peak),
                                'peak_frequency': float(peak_frequency),
                                'significance': 'High' if peak_frequency > 0.1 else 'Medium'
                            })
        
        except Exception as e:
            logger.error(f"Error in peak detection: {e}")
        
        return patterns
    
    def _analyze_trends(self, df: pd.DataFrame) -> List[Dict]:
        """Analyze trends in system metrics"""
        patterns = []
        
        try:
            for metric in ['cpu_usage', 'ram_usage', 'disk_usage']:
                if metric in df.columns and len(df) > 5:
                    values = df[metric].values
                    
                    # Linear trend analysis
                    x = np.arange(len(values))
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
                    
                    if abs(slope) > 0.1 and p_value < 0.05:  # Significant trend
                        trend_direction = 'increasing' if slope > 0 else 'decreasing'
                        trend_strength = 'strong' if abs(r_value) > 0.7 else 'moderate'
                        
                        patterns.append({
                            'type': 'trend_analysis',
                            'metric': metric,
                            'description': f'{metric.replace("_", " ").title()} shows {trend_strength} {trend_direction} trend',
                            'slope': float(slope),
                            'r_squared': float(r_value**2),
                            'p_value': float(p_value),
                            'significance': 'High' if abs(r_value) > 0.8 else 'Medium'
                        })
        
        except Exception as e:
            logger.error(f"Error in trend analysis: {e}")
        
        return patterns
    
    def generate_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive insights from system data"""
        try:
            insights = {
                'anomalies': self.detect_anomalies(df),
                'patterns': self.detect_patterns(df),
                'summary': self._generate_summary(df),
                'recommendations': self._generate_recommendations(df)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return {'error': str(e)}
    
    def _generate_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary statistics"""
        if df.empty:
            return {'message': 'No data available for summary'}
        
        summary = {
            'data_period': {
                'start': df['timestamp'].min().strftime('%Y-%m-%d %H:%M:%S'),
                'end': df['timestamp'].max().strftime('%Y-%m-%d %H:%M:%S'),
                'duration_days': (df['timestamp'].max() - df['timestamp'].min()).days
            },
            'metrics_summary': {}
        }
        
        for metric in ['cpu_usage', 'ram_usage', 'disk_usage']:
            if metric in df.columns:
                values = df[metric]
                summary['metrics_summary'][metric] = {
                    'mean': float(values.mean()),
                    'median': float(values.median()),
                    'std': float(values.std()),
                    'min': float(values.min()),
                    'max': float(values.max()),
                    'current': float(values.iloc[-1]) if len(values) > 0 else 0
                }
        
        return summary
    
    def _generate_recommendations(self, df: pd.DataFrame) -> List[Dict[str, str]]:
        """Generate actionable recommendations"""
        recommendations = []
        
        try:
            if df.empty:
                return [{'type': 'info', 'message': 'No data available for recommendations'}]
            
            latest = df.iloc[-1]
            
            # CPU recommendations
            if 'cpu_usage' in latest and latest['cpu_usage'] > 80:
                recommendations.append({
                    'type': 'warning',
                    'category': 'Performance',
                    'message': 'High CPU usage detected. Consider closing unnecessary applications or upgrading hardware.',
                    'priority': 'High'
                })
            elif 'cpu_usage' in latest and latest['cpu_usage'] > 60:
                recommendations.append({
                    'type': 'info',
                    'category': 'Performance',
                    'message': 'CPU usage is moderate. Monitor for potential performance issues.',
                    'priority': 'Medium'
                })
            
            # RAM recommendations
            if 'ram_usage' in latest and latest['ram_usage'] > 85:
                recommendations.append({
                    'type': 'warning',
                    'category': 'Memory',
                    'message': 'High RAM usage detected. Consider adding more memory or optimizing applications.',
                    'priority': 'High'
                })
            
            # Disk recommendations
            if 'disk_usage' in latest and latest['disk_usage'] > 90:
                recommendations.append({
                    'type': 'critical',
                    'category': 'Storage',
                    'message': 'Disk space critically low. Free up space immediately to prevent system issues.',
                    'priority': 'Critical'
                })
            elif 'disk_usage' in latest and latest['disk_usage'] > 80:
                recommendations.append({
                    'type': 'warning',
                    'category': 'Storage',
                    'message': 'Disk space running low. Consider cleaning up temporary files.',
                    'priority': 'High'
                })
            
            # Trend-based recommendations
            if len(df) > 10:
                cpu_trend = df['cpu_usage'].tail(10).mean() - df['cpu_usage'].head(10).mean()
                if cpu_trend > 10:
                    recommendations.append({
                        'type': 'info',
                        'category': 'Trend',
                        'message': 'CPU usage is trending upward. Monitor for potential performance degradation.',
                        'priority': 'Medium'
                    })
        
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            recommendations.append({
                'type': 'error',
                'message': f'Error generating recommendations: {str(e)}'
            })
        
        return recommendations
    
    def create_analytics_visualizations(self, df: pd.DataFrame, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Create advanced visualizations for analytics"""
        try:
            visualizations = {}
            
            # Anomaly visualization
            if insights.get('anomalies', {}).get('anomalies'):
                visualizations['anomaly_plot'] = self._create_anomaly_plot(df, insights['anomalies'])
            
            # Pattern visualization
            if insights.get('patterns', {}).get('patterns'):
                visualizations['pattern_plot'] = self._create_pattern_plot(df, insights['patterns'])
            
            # Correlation heatmap
            visualizations['correlation_heatmap'] = self._create_correlation_heatmap(df)
            
            # Trend analysis plot
            visualizations['trend_plot'] = self._create_trend_plot(df)
            
            return visualizations
            
        except Exception as e:
            logger.error(f"Error creating visualizations: {e}")
            return {'error': str(e)}
    
    def _create_anomaly_plot(self, df: pd.DataFrame, anomaly_data: Dict) -> go.Figure:
        """Create anomaly detection visualization"""
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('CPU Usage with Anomalies', 'RAM Usage with Anomalies'),
            vertical_spacing=0.1
        )
        
        # CPU anomalies
        if 'cpu_usage' in df.columns:
            fig.add_trace(
                go.Scatter(x=df['timestamp'], y=df['cpu_usage'], 
                          mode='lines', name='CPU Usage', line=dict(color='blue')),
                row=1, col=1
            )
            
            # Mark anomalies
            for anomaly in anomaly_data.get('anomalies', []):
                if 'cpu_usage' in anomaly.get('metrics', {}):
                    fig.add_trace(
                        go.Scatter(x=[anomaly['timestamp']], y=[anomaly['metrics']['cpu_usage']],
                                  mode='markers', name='CPU Anomaly', 
                                  marker=dict(color='red', size=10, symbol='x')),
                        row=1, col=1
                    )
        
        # RAM anomalies
        if 'ram_usage' in df.columns:
            fig.add_trace(
                go.Scatter(x=df['timestamp'], y=df['ram_usage'], 
                          mode='lines', name='RAM Usage', line=dict(color='green')),
                row=2, col=1
            )
            
            # Mark anomalies
            for anomaly in anomaly_data.get('anomalies', []):
                if 'ram_usage' in anomaly.get('metrics', {}):
                    fig.add_trace(
                        go.Scatter(x=[anomaly['timestamp']], y=[anomaly['metrics']['ram_usage']],
                                  mode='markers', name='RAM Anomaly', 
                                  marker=dict(color='red', size=10, symbol='x')),
                        row=2, col=1
                    )
        
        fig.update_layout(height=600, title_text="Anomaly Detection Results")
        return fig
    
    def _create_pattern_plot(self, df: pd.DataFrame, patterns: List[Dict]) -> go.Figure:
        """Create pattern analysis visualization"""
        fig = go.Figure()
        
        # Add time series
        for metric in ['cpu_usage', 'ram_usage']:
            if metric in df.columns:
                fig.add_trace(
                    go.Scatter(x=df['timestamp'], y=df[metric], 
                              mode='lines', name=metric.replace('_', ' ').title())
                )
        
        # Add pattern annotations
        for pattern in patterns:
            if pattern['type'] == 'peak_detection':
                # Add peak markers
                metric = pattern['metric']
                if metric in df.columns:
                    peaks, _ = find_peaks(df[metric].values, 
                                        height=df[metric].mean() + df[metric].std())
                    for peak in peaks:
                        fig.add_annotation(
                            x=df.iloc[peak]['timestamp'],
                            y=df.iloc[peak][metric],
                            text="Peak",
                            showarrow=True,
                            arrowhead=2,
                            arrowcolor="red"
                        )
        
        fig.update_layout(title="Pattern Analysis", height=400)
        return fig
    
    def _create_correlation_heatmap(self, df: pd.DataFrame) -> go.Figure:
        """Create correlation heatmap"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        correlation_matrix = df[numeric_cols].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.columns,
            colorscale='RdBu',
            zmid=0
        ))
        
        fig.update_layout(title="Metrics Correlation Heatmap", height=500)
        return fig
    
    def _create_trend_plot(self, df: pd.DataFrame) -> go.Figure:
        """Create trend analysis visualization"""
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('CPU Trend', 'RAM Trend', 'Disk Trend'),
            vertical_spacing=0.1
        )
        
        metrics = ['cpu_usage', 'ram_usage', 'disk_usage']
        for i, metric in enumerate(metrics, 1):
            if metric in df.columns:
                # Original data
                fig.add_trace(
                    go.Scatter(x=df['timestamp'], y=df[metric], 
                              mode='lines', name=f'{metric} Original', 
                              line=dict(color='blue', width=1)),
                    row=i, col=1
                )
                
                # Trend line
                if len(df) > 5:
                    x = np.arange(len(df))
                    slope, intercept, _, _, _ = stats.linregress(x, df[metric].values)
                    trend_line = slope * x + intercept
                    
                    fig.add_trace(
                        go.Scatter(x=df['timestamp'], y=trend_line, 
                                  mode='lines', name=f'{metric} Trend', 
                                  line=dict(color='red', width=2, dash='dash')),
                        row=i, col=1
                    )
        
        fig.update_layout(height=600, title_text="Trend Analysis")
        return fig
