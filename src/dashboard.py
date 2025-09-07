"""
Enhanced Streamlit dashboard with real-time updates and advanced features
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import time
import os
from pathlib import Path
import logging

import sys
from pathlib import Path

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent))

from config import Config
from src.monitor import SystemMonitor
from src.ml_predictor import MLPredictor
from src.alerts import AlertManager
from src.analytics import AdvancedAnalytics
from src.ai_insights import AIInsightsEngine
from src.multi_system import MultiSystemMonitor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
config = Config()
st.set_page_config(**config.get_dashboard_config())

class Dashboard:
    """Enhanced dashboard with real-time monitoring and ML predictions"""
    
    def __init__(self):
        self.config = config
        self.monitor = SystemMonitor()
        self.predictor = MLPredictor()
        self.alert_manager = AlertManager()
        self.analytics = AdvancedAnalytics()
        self.ai_insights = AIInsightsEngine()
        self.multi_system = MultiSystemMonitor()
        
        # Load models
        self.predictor.load_models()
        
        # Initialize multi-system monitoring with current system
        self.multi_system.add_system("local", "Local System", "local")
        
        # Reload environment variables to pick up .env changes
        from dotenv import load_dotenv
        load_dotenv()
    
    def load_data(self) -> pd.DataFrame:
        """Load monitoring data"""
        try:
            if not self.config.LOG_FILE.exists():
                return pd.DataFrame()
            
            df = pd.read_csv(self.config.LOG_FILE)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df.sort_values('timestamp')
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return pd.DataFrame()
    
    def render_header(self):
        """Render dashboard header"""
        st.title("💻 Smart System Health Monitor")
        st.markdown("Real-time system monitoring with ML predictions and intelligent alerts")
        
        # Auto-refresh toggle
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            auto_refresh = st.checkbox("🔄 Auto Refresh", value=True)
        with col2:
            refresh_interval = st.selectbox("Interval", [5, 10, 30, 60], index=1)
        
        if auto_refresh:
            time.sleep(refresh_interval)
            st.rerun()
    
    def render_current_status(self, df: pd.DataFrame):
        """Render current system status"""
        if df.empty:
            st.warning("No data available. Start monitoring to see system status.")
            return
        
        latest = df.iloc[-1]
        
        st.subheader("📊 Current System Status")
        
        # Create metrics columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            cpu_color = "normal" if latest['cpu_usage'] < 70 else "off" if latest['cpu_usage'] < 90 else "inverse"
            st.metric(
                "CPU Usage", 
                f"{latest['cpu_usage']:.1f}%",
                delta=f"{latest['cpu_usage'] - df.iloc[-2]['cpu_usage']:.1f}%" if len(df) > 1 else None,
                delta_color=cpu_color
            )
        
        with col2:
            ram_color = "normal" if latest['ram_usage'] < 70 else "off" if latest['ram_usage'] < 90 else "inverse"
            st.metric(
                "RAM Usage", 
                f"{latest['ram_usage']:.1f}%",
                delta=f"{latest['ram_usage'] - df.iloc[-2]['ram_usage']:.1f}%" if len(df) > 1 else None,
                delta_color=ram_color
            )
        
        with col3:
            disk_color = "normal" if latest['disk_usage'] < 80 else "off" if latest['disk_usage'] < 95 else "inverse"
            st.metric(
                "Disk Usage", 
                f"{latest['disk_usage']:.1f}%",
                delta=f"{latest['disk_usage'] - df.iloc[-2]['disk_usage']:.1f}%" if len(df) > 1 else None,
                delta_color=disk_color
            )
        
        with col4:
            network_total = latest['network_rx_kb'] + latest['network_tx_kb']
            st.metric(
                "Network Activity", 
                f"{network_total:.0f} KB",
                delta=f"{(network_total - (df.iloc[-2]['network_rx_kb'] + df.iloc[-2]['network_tx_kb'])):.0f} KB" if len(df) > 1 else None
            )
        
        # Additional metrics
        if 'temperature_c' in latest and latest['temperature_c'] > 0:
            col5, col6, col7 = st.columns(3)
            with col5:
                st.metric("Temperature", f"{latest['temperature_c']:.1f}°C")
            with col6:
                st.metric("Load Average", f"{latest['load_average']:.2f}")
            with col7:
                st.metric("Processes", f"{latest['process_count']}")
    
    def render_time_series_charts(self, df: pd.DataFrame):
        """Render time series charts"""
        if df.empty:
            return
        
        st.subheader("📈 System Metrics Over Time")
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('CPU Usage', 'RAM Usage', 'Disk Usage', 'Network Activity', 'Load Average', 'Process Count'),
            vertical_spacing=0.08
        )
        
        # CPU Usage
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['cpu_usage'], name='CPU', line=dict(color='#1f77b4')),
            row=1, col=1
        )
        
        # RAM Usage
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['ram_usage'], name='RAM', line=dict(color='#ff7f0e')),
            row=1, col=2
        )
        
        # Disk Usage
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['disk_usage'], name='Disk', line=dict(color='#2ca02c')),
            row=2, col=1
        )
        
        # Network Activity
        network_total = df['network_rx_kb'] + df['network_tx_kb']
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=network_total, name='Network', line=dict(color='#d62728')),
            row=2, col=2
        )
        
        # Load Average
        if 'load_average' in df.columns:
            fig.add_trace(
                go.Scatter(x=df['timestamp'], y=df['load_average'], name='Load', line=dict(color='#9467bd')),
                row=3, col=1
            )
        
        # Process Count
        if 'process_count' in df.columns:
            fig.add_trace(
                go.Scatter(x=df['timestamp'], y=df['process_count'], name='Processes', line=dict(color='#8c564b')),
                row=3, col=2
            )
        
        fig.update_layout(height=800, showlegend=False, title_text="System Metrics Timeline")
        fig.update_xaxes(title_text="Time")
        fig.update_yaxes(title_text="Value")
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_ml_predictions(self, df: pd.DataFrame):
        """Render ML predictions"""
        if df.empty:
            return
        
        st.subheader("🤖 ML Predictions")
        
        latest = df.iloc[-1]
        metrics = {
            'cpu_usage': latest['cpu_usage'],
            'ram_usage': latest['ram_usage'],
            'disk_usage': latest['disk_usage'],
            'network_rx_kb': latest['network_rx_kb'],
            'network_tx_kb': latest['network_tx_kb'],
            'load_average': latest.get('load_average', 0),
            'process_count': latest.get('process_count', 0),
            'temperature_c': latest.get('temperature_c', 0)
        }
        
        predictions = self.predictor.predict(metrics, self.config.PREDICTION_HORIZON)
        
        if 'error' in predictions:
            st.error(f"Prediction error: {predictions['error']}")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'cpu_usage' in predictions:
                pred = predictions['cpu_usage']
                st.metric(
                    "Predicted CPU Usage",
                    f"{pred['value']:.1f}%",
                    help=f"Confidence: {pred['confidence']} (±{pred['uncertainty']:.1f}%)"
                )
        
        with col2:
            if 'ram_usage' in predictions:
                pred = predictions['ram_usage']
                st.metric(
                    "Predicted RAM Usage",
                    f"{pred['value']:.1f}%",
                    help=f"Confidence: {pred['confidence']} (±{pred['uncertainty']:.1f}%)"
                )
        
        # Model information
        with st.expander("🔍 Model Information"):
            model_info = self.predictor.get_model_info()
            for target, info in model_info.items():
                if info.get('trained'):
                    st.success(f"✅ {target.replace('_', ' ').title()}: {info['type']}")
                else:
                    st.warning(f"⚠️ {target.replace('_', ' ').title()}: Not trained")
    
    def render_health_analysis(self, df: pd.DataFrame):
        """Render system health analysis"""
        if df.empty:
            return
        
        st.subheader("🏥 System Health Analysis")
        
        latest = df.iloc[-1]
        
        # Health score calculation
        health_score = 100
        issues = []
        
        if latest['cpu_usage'] > 80:
            health_score -= 20
            issues.append("High CPU usage")
        elif latest['cpu_usage'] > 60:
            health_score -= 10
        
        if latest['ram_usage'] > 80:
            health_score -= 20
            issues.append("High RAM usage")
        elif latest['ram_usage'] > 60:
            health_score -= 10
        
        if latest['disk_usage'] > 90:
            health_score -= 30
            issues.append("Low disk space")
        elif latest['disk_usage'] > 80:
            health_score -= 15
        
        if latest.get('temperature_c', 0) > 80:
            health_score -= 15
            issues.append("High temperature")
        
        # Display health score
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if health_score >= 80:
                st.success(f"🟢 Health Score: {health_score}/100")
            elif health_score >= 60:
                st.warning(f"🟡 Health Score: {health_score}/100")
            else:
                st.error(f"🔴 Health Score: {health_score}/100")
        
        with col2:
            if issues:
                st.warning("⚠️ Issues detected:")
                for issue in issues:
                    st.write(f"• {issue}")
            else:
                st.success("✅ System is healthy!")
        
        # Recommendations
        st.subheader("💡 Recommendations")
        recommendations = []
        
        if latest['cpu_usage'] > 70:
            recommendations.append("Consider closing unnecessary applications or upgrading CPU")
        
        if latest['ram_usage'] > 70:
            recommendations.append("Monitor memory usage and consider adding more RAM")
        
        if latest['disk_usage'] > 80:
            recommendations.append("Clean up temporary files and consider disk expansion")
        
        if latest.get('load_average', 0) > 2:
            recommendations.append("System load is high, check for resource-intensive processes")
        
        if not recommendations:
            recommendations.append("System is running optimally!")
        
        for rec in recommendations:
            st.info(rec)
    
    def render_alert_history(self):
        """Render alert history"""
        st.subheader("🚨 Alert History")
        
        alert_history = self.alert_manager.get_alert_history(20)
        
        if not alert_history:
            st.info("No alerts in recent history")
            return
        
        for alert in reversed(alert_history):
            with st.expander(f"Alert - {alert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}"):
                st.write("**Alerts:**")
                for alert_msg in alert['alerts']:
                    st.write(f"• {alert_msg}")
                
                st.write("**Metrics at time of alert:**")
                metrics = alert['metrics']
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("CPU", f"{metrics.get('cpu_usage', 0):.1f}%")
                with col2:
                    st.metric("RAM", f"{metrics.get('ram_usage', 0):.1f}%")
                with col3:
                    st.metric("Disk", f"{metrics.get('disk_usage', 0):.1f}%")
    
    def render_sidebar(self):
        """Render sidebar with controls"""
        with st.sidebar:
            st.header("⚙️ Controls")
            
            # Manual refresh
            if st.button("🔄 Refresh Data"):
                st.rerun()
            
            # Refresh configuration
            if st.button("⚙️ Refresh Configuration"):
                with st.spinner("Refreshing configuration..."):
                    # Reload environment variables
                    from dotenv import load_dotenv
                    load_dotenv()
                    
                    # Update config
                    self.config.TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
                    self.config.TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
                    
                    # Recreate alert manager with fresh config
                    self.alert_manager = AlertManager()
                    
                    st.success("✅ Configuration refreshed!")
                    st.info("Telegram settings updated. Try testing notifications again.")
            
            # Test notifications
            if st.button("🧪 Test Notifications"):
                with st.spinner("Testing notifications..."):
                    # Get current system metrics
                    current_metrics = self.monitor.collect_metrics()
                    
                    # Create test alert with current system data
                    test_message = f"🧪 **Test Alert** - Current System Status\n\n"
                    test_message += f"📊 **Live System Metrics:**\n"
                    test_message += f"• CPU: {current_metrics['cpu_usage']:.1f}%\n"
                    test_message += f"• RAM: {current_metrics['ram_usage']:.1f}%\n"
                    test_message += f"• Disk: {current_metrics['disk_usage']:.1f}%\n"
                    test_message += f"• Network: {current_metrics['network_rx_kb']:.0f} KB RX, {current_metrics['network_tx_kb']:.0f} KB TX\n"
                    if current_metrics.get('temperature_c', 0) > 0:
                        test_message += f"• Temperature: {current_metrics['temperature_c']:.1f}°C\n"
                    test_message += f"• Load Average: {current_metrics.get('load_average', 0):.2f}\n"
                    test_message += f"• Processes: {current_metrics.get('process_count', 0)}\n\n"
                    test_message += f"✅ Smart System Health Monitor is working correctly!"
                    
                    # Send test notification
                    results = self.alert_manager.send_alerts([test_message], current_metrics)
                    
                    for channel, success in results.items():
                        if success:
                            st.success(f"✅ {channel.capitalize()} test successful - Check your {channel}!")
                        else:
                            st.error(f"❌ {channel.capitalize()} test failed")
            
            # Setup Telegram button
            if st.button("🤖 Setup Telegram Bot"):
                st.info("""
                **To setup Telegram notifications:**
                1. Run: `python setup_telegram.py`
                2. Follow the instructions to create a bot
                3. Get your bot token and chat ID
                4. Test notifications will be sent automatically
                """)
            
            # View dataset button
            if st.button("📋 View System Dataset"):
                st.subheader("📊 System Monitoring Dataset")
                
                df = self.load_data()
                if df.empty:
                    st.warning("No data available. Generate some data first!")
                else:
                    # Dataset overview
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Records", len(df))
                    with col2:
                        st.metric("Date Range", f"{(df['timestamp'].max() - df['timestamp'].min()).days} days")
                    with col3:
                        st.metric("Latest Update", df['timestamp'].max().strftime("%H:%M:%S"))
                    
                    # Data quality info
                    st.subheader("📈 Data Quality")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Missing Values:**")
                        missing = df.isnull().sum()
                        for col, count in missing.items():
                            if count > 0:
                                st.write(f"• {col}: {count}")
                            else:
                                st.write(f"• {col}: ✅ Complete")
                    
                    with col2:
                        st.write("**Data Statistics:**")
                        st.write(f"• CPU Range: {df['cpu_usage'].min():.1f}% - {df['cpu_usage'].max():.1f}%")
                        st.write(f"• RAM Range: {df['ram_usage'].min():.1f}% - {df['ram_usage'].max():.1f}%")
                        st.write(f"• Disk Range: {df['disk_usage'].min():.1f}% - {df['disk_usage'].max():.1f}%")
                    
                    # Interactive data table
                    st.subheader("📋 Raw Data Table")
                    
                    # Add filters
                    col1, col2 = st.columns(2)
                    with col1:
                        show_last = st.selectbox("Show last N records", [10, 25, 50, 100, "All"], index=0)
                    with col2:
                        sort_by = st.selectbox("Sort by", ["timestamp", "cpu_usage", "ram_usage", "disk_usage"], index=0)
                    
                    # Filter and sort data
                    display_df = df.copy()
                    if show_last != "All":
                        display_df = display_df.tail(show_last)
                    
                    display_df = display_df.sort_values(sort_by, ascending=False)
                    
                    # Format the dataframe for better display
                    display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
                    display_df['cpu_usage'] = display_df['cpu_usage'].round(1)
                    display_df['ram_usage'] = display_df['ram_usage'].round(1)
                    display_df['disk_usage'] = display_df['disk_usage'].round(1)
                    display_df['network_rx_kb'] = display_df['network_rx_kb'].round(0)
                    display_df['network_tx_kb'] = display_df['network_tx_kb'].round(0)
                    
                    # Rename columns for better display
                    display_df = display_df.rename(columns={
                        'timestamp': '📅 Timestamp',
                        'cpu_usage': '🖥️ CPU %',
                        'ram_usage': '💾 RAM %',
                        'disk_usage': '💿 Disk %',
                        'network_rx_kb': '📥 Network RX (KB)',
                        'network_tx_kb': '📤 Network TX (KB)',
                        'load_average': '⚖️ Load Avg',
                        'process_count': '🔄 Processes',
                        'temperature_c': '🌡️ Temp (°C)'
                    })
                    
                    st.dataframe(display_df, use_container_width=True)
                    
                    # Download option
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Dataset as CSV",
                        data=csv,
                        file_name=f"system_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            
            # Generate real data button
            if st.button("📊 Generate Real System Data"):
                with st.spinner("Collecting real system data..."):
                    # Generate real system data
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Collect 5 samples of real data
                    for i in range(5):
                        status_text.text(f"Collecting sample {i+1}/5...")
                        progress_bar.progress((i+1) * 20)
                        
                        # Run monitoring cycle
                        result = self.monitor.run_monitoring_cycle()
                        
                        # Show current metrics
                        metrics = result['metrics']
                        st.write(f"Sample {i+1}: CPU: {metrics['cpu_usage']:.1f}% | RAM: {metrics['ram_usage']:.1f}% | Disk: {metrics['disk_usage']:.1f}%")
                        
                        # Show alerts if any
                        if result['alerts']:
                            st.warning(f"🚨 Alerts: {', '.join(result['alerts'])}")
                            
                            # Send alerts
                            alert_results = self.alert_manager.send_alerts(result['alerts'], result['metrics'])
                            for channel, success in alert_results.items():
                                if success:
                                    st.success(f"✅ Alert sent via {channel}")
                                else:
                                    st.error(f"❌ Failed to send via {channel}")
                        
                        # Wait 2 seconds between samples
                        if i < 4:
                            time.sleep(2)
                    
                    status_text.text("✅ Real system data generated!")
                    progress_bar.progress(100)
                    
                    st.success("🎉 Real system data collected successfully!")
                    st.info("📊 Check the dashboard above to see the new data. The charts will update automatically.")
                    
                    # Clear progress indicators
                    time.sleep(1)
                    progress_bar.empty()
                    status_text.empty()
            
            # Train models
            if st.button("🤖 Retrain Models"):
                with st.spinner("Training models..."):
                    # Show training progress
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("Loading data...")
                    progress_bar.progress(20)
                    
                    status_text.text("Training CPU model...")
                    progress_bar.progress(50)
                    
                    status_text.text("Training RAM model...")
                    progress_bar.progress(80)
                    
                    results = self.predictor.train_models()
                    
                    status_text.text("Saving models...")
                    progress_bar.progress(100)
                    
                    if results['success']:
                        st.success("✅ Models trained successfully!")
                        
                        # Get current system metrics for predictions
                        current_metrics = self.monitor.collect_metrics()
                        
                        # Make predictions with the newly trained models
                        status_text.text("Making predictions...")
                        predictions = self.predictor.predict(current_metrics, self.config.PREDICTION_HORIZON)
                        
                        if 'error' not in predictions:
                            st.subheader("🔮 ML Predictions (Next 10 Minutes)")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if 'cpu_usage' in predictions:
                                    pred = predictions['cpu_usage']
                                    st.metric(
                                        "Predicted CPU Usage",
                                        f"{pred['value']:.1f}%",
                                        help=f"Confidence: {pred['confidence']} (±{pred['uncertainty']:.1f}%)"
                                    )
                            
                            with col2:
                                if 'ram_usage' in predictions:
                                    pred = predictions['ram_usage']
                                    st.metric(
                                        "Predicted RAM Usage",
                                        f"{pred['value']:.1f}%",
                                        help=f"Confidence: {pred['confidence']} (±{pred['uncertainty']:.1f}%)"
                                    )
                            
                            # Show prediction details
                            st.subheader("📊 Prediction Details")
                            for target, pred in predictions.items():
                                st.write(f"**{target.replace('_', ' ').title()}**:")
                                st.write(f"  • Predicted Value: {pred['value']:.1f}%")
                                st.write(f"  • Confidence: {pred['confidence']}")
                                st.write(f"  • Uncertainty: ±{pred['uncertainty']:.1f}%")
                                st.write("")
                        else:
                            st.error(f"❌ Prediction error: {predictions['error']}")
                        
                        # Show training results in expander
                        with st.expander("📈 Training Results (Technical Details)"):
                            for target, metrics in results['results'].items():
                                if 'error' not in metrics:
                                    st.write(f"**{target.replace('_', ' ').title()} Model:**")
                                    st.write(f"  • Mean Absolute Error (MAE): {metrics['mae']:.2f}")
                                    st.write(f"  • R² Score: {metrics['r2']:.3f}")
                                    st.write(f"  • Cross-validation Mean: {metrics['cv_mean']:.3f}")
                                    st.write(f"  • Cross-validation Std: {metrics['cv_std']:.3f}")
                                    st.write("")
                    else:
                        st.error(f"❌ Training failed: {results['message']}")
                    
                    progress_bar.empty()
                    status_text.empty()
            
            # Configuration
            st.header("📋 Configuration")
            st.write(f"**Monitoring Interval:** {self.config.MONITORING_INTERVAL}s")
            st.write(f"**CPU Threshold:** {self.config.CPU_THRESHOLD}%")
            st.write(f"**RAM Threshold:** {self.config.RAM_THRESHOLD}%")
            st.write(f"**Disk Threshold:** {self.config.DISK_THRESHOLD}%")
            
            # Data info
            df = self.load_data()
            if not df.empty:
                st.header("📊 Data Info")
                st.write(f"**Total Records:** {len(df)}")
                st.write(f"**Date Range:** {df['timestamp'].min().strftime('%Y-%m-%d')} to {df['timestamp'].max().strftime('%Y-%m-%d')}")
                st.write(f"**Last Update:** {df['timestamp'].max().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def render_advanced_analytics(self, df: pd.DataFrame):
        """Render advanced analytics and anomaly detection"""
        if df.empty:
            return
        
        st.subheader("🔍 Advanced Analytics & Anomaly Detection")
        
        # Generate analytics
        with st.spinner("Analyzing system data..."):
            insights = self.analytics.generate_insights(df)
        
        # Display analytics summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            anomaly_count = insights.get('anomalies', {}).get('total_anomalies', 0)
            st.metric("Anomalies Detected", anomaly_count)
        
        with col2:
            pattern_count = insights.get('patterns', {}).get('total_patterns', 0)
            st.metric("Patterns Found", pattern_count)
        
        with col3:
            anomaly_score = insights.get('anomalies', {}).get('anomaly_score', 0)
            st.metric("Anomaly Score", f"{anomaly_score:.2%}")
        
        with col4:
            data_points = len(df)
            st.metric("Data Points", data_points)
        
        # Anomaly details
        if anomaly_count > 0:
            st.subheader("🚨 Detected Anomalies")
            anomalies = insights.get('anomalies', {}).get('anomalies', [])
            
            for i, anomaly in enumerate(anomalies[:5]):  # Show top 5
                with st.expander(f"Anomaly {i+1} - {anomaly.get('severity', 'Unknown')} Severity"):
                    st.write(f"**Timestamp:** {anomaly.get('timestamp', 'Unknown')}")
                    st.write(f"**Anomaly Score:** {anomaly.get('anomaly_score', 0):.3f}")
                    st.write("**Metrics at time of anomaly:**")
                    
                    metrics = anomaly.get('metrics', {})
                    for metric, value in metrics.items():
                        st.write(f"• {metric.replace('_', ' ').title()}: {value:.1f}")
        
        # Pattern details
        if pattern_count > 0:
            st.subheader("📊 Detected Patterns")
            patterns = insights.get('patterns', {}).get('patterns', [])
            
            for pattern in patterns[:5]:  # Show top 5
                with st.expander(f"Pattern: {pattern.get('description', 'Unknown')}"):
                    st.write(f"**Type:** {pattern.get('type', 'Unknown')}")
                    st.write(f"**Significance:** {pattern.get('significance', 'Unknown')}")
                    if 'value' in pattern:
                        st.write(f"**Value:** {pattern.get('value', 0):.1f}")
        
        # Analytics visualizations
        if st.button("📈 Generate Analytics Visualizations"):
            with st.spinner("Creating visualizations..."):
                visualizations = self.analytics.create_analytics_visualizations(df, insights)
                
                if 'anomaly_plot' in visualizations:
                    st.plotly_chart(visualizations['anomaly_plot'], use_container_width=True)
                
                if 'correlation_heatmap' in visualizations:
                    st.plotly_chart(visualizations['correlation_heatmap'], use_container_width=True)
                
                if 'trend_plot' in visualizations:
                    st.plotly_chart(visualizations['trend_plot'], use_container_width=True)
    
    def render_ai_insights(self, df: pd.DataFrame):
        """Render AI-powered insights and recommendations"""
        if df.empty:
            return
        
        st.subheader("🤖 AI-Powered Insights & Recommendations")
        
        # Generate AI insights
        with st.spinner("Generating AI insights..."):
            # First get analytics data
            analytics_data = self.analytics.generate_insights(df)
            # Then generate AI insights
            ai_insights = self.ai_insights.generate_insights(df, analytics_data)
            formatted_insights = self.ai_insights.format_insights_for_display(ai_insights)
        
        # Insights summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Insights", formatted_insights['total_insights'])
        
        with col2:
            st.metric("Critical", formatted_insights['critical_count'], delta=None)
        
        with col3:
            st.metric("High Priority", formatted_insights['high_count'], delta=None)
        
        with col4:
            st.metric("Medium Priority", formatted_insights['medium_count'], delta=None)
        
        # Display insights
        if formatted_insights['insights']:
            st.subheader("💡 AI Insights & Recommendations")
            
            for insight in formatted_insights['insights']:
                # Create colored container based on priority
                if insight['priority'] == 'Critical':
                    st.error(f"🚨 **{insight['title']}**")
                elif insight['priority'] == 'High':
                    st.warning(f"⚠️ **{insight['title']}**")
                elif insight['priority'] == 'Medium':
                    st.info(f"📊 **{insight['title']}**")
                else:
                    st.success(f"💡 **{insight['title']}**")
                
                st.write(f"**Description:** {insight['description']}")
                st.write(f"**Category:** {insight['category']} | **Confidence:** {insight['confidence']}")
                
                if insight['actionable'] and insight['recommendation']:
                    st.write(f"**Recommendation:** {insight['recommendation']}")
                
                if insight['impact']:
                    st.write(f"**Impact:** {insight['impact']}")
                
                st.markdown("---")
        else:
            st.info("✅ No significant insights detected. Your system is running normally!")
    
    def render_multi_system_view(self):
        """Render multi-system monitoring view"""
        st.subheader("🖥️ Multi-System Monitoring")
        
        # Get system summary
        summary = self.multi_system.get_system_summary()
        
        # System overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Systems", summary['total_systems'])
        
        with col2:
            st.metric("Online Systems", summary['online_systems'])
        
        with col3:
            st.metric("Systems with Errors", summary['error_systems'])
        
        # System details
        if summary['systems']:
            st.subheader("📋 System Details")
            
            for system in summary['systems']:
                with st.expander(f"{system['system_name']} ({system['system_id']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Type:** {system['system_type']}")
                        st.write(f"**Status:** {system['status']}")
                        st.write(f"**Last Seen:** {system['last_seen']}")
                    
                    with col2:
                        if 'latest_metrics' in system:
                            metrics = system['latest_metrics']
                            st.write(f"**CPU:** {metrics.get('cpu_usage', 0):.1f}%")
                            st.write(f"**RAM:** {metrics.get('ram_usage', 0):.1f}%")
                            st.write(f"**Disk:** {metrics.get('disk_usage', 0):.1f}%")
        
        # Add new system
        st.subheader("➕ Add New System")
        
        with st.form("add_system_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                system_id = st.text_input("System ID", placeholder="server-01")
            
            with col2:
                system_name = st.text_input("System Name", placeholder="Production Server")
            
            with col3:
                system_type = st.selectbox("System Type", ["local", "remote", "docker"])
            
            if st.form_submit_button("Add System"):
                if system_id and system_name:
                    success = self.multi_system.add_system(system_id, system_name, system_type)
                    if success:
                        st.success(f"✅ Added system: {system_name}")
                        st.rerun()
                    else:
                        st.error("❌ Failed to add system")
                else:
                    st.error("Please fill in all fields")
        
        # Multi-system controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Refresh All Systems"):
                with st.spinner("Collecting metrics from all systems..."):
                    all_metrics = self.multi_system.collect_all_metrics()
                    st.success(f"✅ Collected metrics from {all_metrics['total_systems']} systems")
        
        with col2:
            if st.button("📊 Export System Data"):
                st.info("Export functionality will be available in the next update")
        
        with col3:
            if st.button("🔍 Check Offline Systems"):
                offline = self.multi_system.detect_offline_systems()
                if offline:
                    st.warning(f"⚠️ {len(offline)} systems are offline: {', '.join(offline)}")
                else:
                    st.success("✅ All systems are online")
    
    def run(self):
        """Run the dashboard"""
        # Load data
        df = self.load_data()
        
        # Render components
        self.render_header()
        self.render_sidebar()
        self.render_current_status(df)
        self.render_time_series_charts(df)
        self.render_ml_predictions(df)
        self.render_health_analysis(df)
        self.render_alert_history()
        self.render_advanced_analytics(df)
        self.render_ai_insights(df)
        self.render_multi_system_view()
        
        # Footer
        st.markdown("---")
        st.caption("Built with ❤️ by Smart System Health Monitor v2.0")

def main():
    """Main function"""
    dashboard = Dashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
