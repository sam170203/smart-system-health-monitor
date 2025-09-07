#!/usr/bin/env python3
"""
Enhanced monitoring script with integrated alerting and ML predictions
"""
import sys
import time
import logging
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from config import Config
from src.monitor import SystemMonitor
from src.alerts import AlertManager
from src.ml_predictor import MLPredictor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main monitoring function"""
    logger.info("Starting Smart System Health Monitor...")
    
    # Initialize components
    config = Config()
    monitor = SystemMonitor()
    alert_manager = AlertManager()
    predictor = MLPredictor()
    
    # Validate configuration
    if not config.validate_config():
        logger.error("Configuration validation failed")
        sys.exit(1)
    
    # Load ML models
    predictor.load_models()
    
    logger.info("Monitor initialized successfully")
    
    try:
        while True:
            # Run monitoring cycle
            result = monitor.run_monitoring_cycle()
            
            if result['logged']:
                logger.info("Metrics logged successfully")
            else:
                logger.error("Failed to log metrics")
            
            # Send alerts if any
            if result['alerts']:
                logger.warning(f"Sending {len(result['alerts'])} alerts")
                alert_results = alert_manager.send_alerts(result['alerts'], result['metrics'])
                
                for channel, success in alert_results.items():
                    if success:
                        logger.info(f"Alert sent via {channel}")
                    else:
                        logger.error(f"Failed to send alert via {channel}")
            
            # Make predictions if ML is enabled
            if config.ML_ENABLED and predictor.models:
                predictions = predictor.predict(result['metrics'], config.PREDICTION_HORIZON)
                if 'error' not in predictions:
                    logger.info(f"Predictions: CPU={predictions.get('cpu_usage', {}).get('value', 0):.1f}%, RAM={predictions.get('ram_usage', {}).get('value', 0):.1f}%")
            
            # Wait for next cycle
            logger.info(f"Waiting {config.MONITORING_INTERVAL} seconds for next cycle...")
            time.sleep(config.MONITORING_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("Monitor stopped by user")
    except Exception as e:
        logger.error(f"Monitor error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
