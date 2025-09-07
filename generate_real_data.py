#!/usr/bin/env python3
"""
Generate real system monitoring data and test alerts
"""
import sys
import time
import psutil
from datetime import datetime
import csv
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from config import Config
from src.monitor import SystemMonitor
from src.alerts import AlertManager

def generate_real_data():
    """Generate real system monitoring data"""
    print("🔄 Generating real system monitoring data...")
    print("This will collect actual system metrics and test the monitoring system.")
    print("Press Ctrl+C to stop after a few samples.\n")
    
    # Initialize components
    config = Config()
    monitor = SystemMonitor()
    alert_manager = AlertManager()
    
    try:
        for i in range(10):  # Generate 10 samples
            print(f"📊 Sample {i+1}/10 - Collecting system metrics...")
            
            # Run monitoring cycle
            result = monitor.run_monitoring_cycle()
            
            # Display current metrics
            metrics = result['metrics']
            print(f"   CPU: {metrics['cpu_usage']:.1f}% | RAM: {metrics['ram_usage']:.1f}% | Disk: {metrics['disk_usage']:.1f}%")
            
            # Show alerts if any
            if result['alerts']:
                print(f"   🚨 Alerts: {len(result['alerts'])}")
                for alert in result['alerts']:
                    print(f"      {alert}")
                
                # Send alerts
                alert_results = alert_manager.send_alerts(result['alerts'], result['metrics'])
                for channel, success in alert_results.items():
                    if success:
                        print(f"      ✅ Alert sent via {channel}")
                    else:
                        print(f"      ❌ Failed to send via {channel}")
            
            print()
            
            # Wait 10 seconds between samples
            if i < 9:  # Don't wait after the last sample
                time.sleep(10)
    
    except KeyboardInterrupt:
        print("\n⏹️  Data generation stopped by user")
    
    print("\n✅ Real system data generated!")
    print("📁 Check the logs/system_metrics.csv file for the collected data")
    print("🌐 Refresh your dashboard to see the real data")

def test_ml_predictions():
    """Test ML predictions with real data"""
    print("\n🤖 Testing ML predictions...")
    
    try:
        from src.ml_predictor import MLPredictor
        
        predictor = MLPredictor()
        
        # Load models
        if predictor.load_models():
            print("✅ ML models loaded successfully")
            
            # Get current system metrics
            monitor = SystemMonitor()
            metrics = monitor.collect_metrics()
            
            # Make predictions
            predictions = predictor.predict(metrics, 10)
            
            if 'error' not in predictions:
                print("🔮 Predictions for next 10 minutes:")
                for target, pred in predictions.items():
                    print(f"   {target.replace('_', ' ').title()}: {pred['value']:.1f}% (confidence: {pred['confidence']})")
            else:
                print(f"❌ Prediction error: {predictions['error']}")
        else:
            print("⚠️  No trained models found. Run the dashboard and click 'Retrain Models' first.")
    
    except Exception as e:
        print(f"❌ Error testing ML predictions: {e}")

def main():
    """Main function"""
    print("🧠 Smart System Health Monitor - Real Data Generator")
    print("=" * 60)
    
    # Check if .env exists
    if not Path('.env').exists():
        print("⚠️  No .env file found. Run setup_telegram.py first to configure notifications.")
        print("   Or create a .env file manually with your Telegram bot settings.\n")
    
    # Generate real data
    generate_real_data()
    
    # Test ML predictions
    test_ml_predictions()
    
    print("\n🎉 Testing complete!")
    print("📊 Your dashboard should now show real system data")
    print("🔔 If you configured Telegram, you should have received test alerts")

if __name__ == "__main__":
    main()
