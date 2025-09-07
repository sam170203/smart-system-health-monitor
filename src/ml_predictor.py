"""
Enhanced ML prediction module with multiple algorithms and better accuracy
"""
import pandas as pd
import numpy as np
import joblib
import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import logging
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings

import sys
from pathlib import Path

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent))

from config import Config

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

class MLPredictor:
    """Enhanced ML predictor with multiple algorithms and features"""
    
    def __init__(self):
        self.config = Config()
        self.models = {}
        self.scalers = {}
        self.feature_columns = [
            'ram_usage', 'disk_usage', 'network_rx_kb', 'network_tx_kb',
            'load_average', 'process_count', 'temperature_c'
        ]
        self.target_columns = ['cpu_usage', 'ram_usage']
        self.model_types = {
            'cpu_usage': RandomForestRegressor(n_estimators=100, random_state=42),
            'ram_usage': GradientBoostingRegressor(n_estimators=100, random_state=42)
        }
    
    def load_data(self) -> Optional[pd.DataFrame]:
        """Load and preprocess monitoring data"""
        try:
            if not self.config.LOG_FILE.exists():
                logger.warning("No log file found for training")
                return None
            
            df = pd.read_csv(self.config.LOG_FILE)
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Sort by timestamp
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            # Add time-based features
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
            
            # Add rolling averages for better predictions
            for col in ['cpu_usage', 'ram_usage']:
                df[f'{col}_ma_5'] = df[col].rolling(window=5, min_periods=1).mean()
                df[f'{col}_ma_10'] = df[col].rolling(window=10, min_periods=1).mean()
            
            # Add lag features
            for col in ['cpu_usage', 'ram_usage']:
                df[f'{col}_lag_1'] = df[col].shift(1)
                df[f'{col}_lag_2'] = df[col].shift(2)
            
            # Fill NaN values
            df = df.fillna(method='bfill').fillna(method='ffill')
            
            logger.info(f"Loaded {len(df)} data points for training")
            return df
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return None
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """Prepare features for training"""
        # Base features
        base_features = self.feature_columns + ['hour', 'day_of_week', 'is_weekend']
        
        # Add rolling averages and lag features
        feature_cols = base_features.copy()
        for col in ['cpu_usage', 'ram_usage']:
            feature_cols.extend([f'{col}_ma_5', f'{col}_ma_10', f'{col}_lag_1', f'{col}_lag_2'])
        
        # Ensure all feature columns exist
        available_features = [col for col in feature_cols if col in df.columns]
        
        X = df[available_features]
        
        # Prepare targets
        targets = {}
        for target in self.target_columns:
            if target in df.columns:
                targets[target] = df[target]
        
        return X, targets
    
    def train_models(self) -> Dict[str, Any]:
        """Train ML models for different metrics"""
        df = self.load_data()
        if df is None or len(df) < 10:
            logger.warning("Insufficient data for training")
            return {'success': False, 'message': 'Insufficient data'}
        
        X, targets = self.prepare_features(df)
        
        results = {}
        
        for target_name, y in targets.items():
            try:
                # Remove rows with NaN values
                valid_indices = ~(X.isna().any(axis=1) | y.isna())
                X_clean = X[valid_indices]
                y_clean = y[valid_indices]
                
                if len(X_clean) < 5:
                    logger.warning(f"Insufficient clean data for {target_name}")
                    continue
                
                # Split data
                X_train, X_test, y_train, y_test = train_test_split(
                    X_clean, y_clean, test_size=0.2, random_state=42
                )
                
                # Scale features
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)
                
                # Train model
                model = self.model_types[target_name]
                model.fit(X_train_scaled, y_train)
                
                # Evaluate model
                y_pred = model.predict(X_test_scaled)
                mae = mean_absolute_error(y_test, y_pred)
                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                # Cross-validation score
                cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=3)
                
                # Save model and scaler
                self.models[target_name] = model
                self.scalers[target_name] = scaler
                
                results[target_name] = {
                    'mae': mae,
                    'mse': mse,
                    'r2': r2,
                    'cv_mean': cv_scores.mean(),
                    'cv_std': cv_scores.std(),
                    'feature_importance': dict(zip(X.columns, model.feature_importances_)) if hasattr(model, 'feature_importances_') else None
                }
                
                logger.info(f"Trained {target_name} model - MAE: {mae:.2f}, R²: {r2:.3f}")
                
            except Exception as e:
                logger.error(f"Error training {target_name} model: {e}")
                results[target_name] = {'error': str(e)}
        
        # Save models
        self.save_models()
        
        return {'success': True, 'results': results}
    
    def save_models(self):
        """Save trained models and scalers"""
        try:
            self.config.MODELS_DIR.mkdir(exist_ok=True)
            
            for target_name, model in self.models.items():
                model_path = self.config.MODELS_DIR / f"{target_name}_model.pkl"
                joblib.dump(model, model_path)
                
                scaler_path = self.config.MODELS_DIR / f"{target_name}_scaler.pkl"
                joblib.dump(self.scalers[target_name], scaler_path)
            
            logger.info("Models saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    def load_models(self) -> bool:
        """Load pre-trained models"""
        try:
            loaded = False
            
            for target_name in self.target_columns:
                model_path = self.config.MODELS_DIR / f"{target_name}_model.pkl"
                scaler_path = self.config.MODELS_DIR / f"{target_name}_scaler.pkl"
                
                if model_path.exists() and scaler_path.exists():
                    self.models[target_name] = joblib.load(model_path)
                    self.scalers[target_name] = joblib.load(scaler_path)
                    loaded = True
                    logger.info(f"Loaded {target_name} model")
            
            return loaded
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            return False
    
    def predict(self, metrics: Dict[str, Any], horizon_minutes: int = 10) -> Dict[str, Any]:
        """Make predictions for future values"""
        if not self.models:
            if not self.load_models():
                return {'error': 'No trained models available'}
        
        try:
            # Get recent data for context
            df = self.load_data()
            if df is None or len(df) < 2:
                return {'error': 'Insufficient historical data'}
            
            # Prepare features for prediction
            X, _ = self.prepare_features(df)
            
            # Use the most recent row as base
            latest_features = X.iloc[-1:].copy()
            
            # Update with current metrics
            for key, value in metrics.items():
                if key in latest_features.columns:
                    latest_features[key] = value
            
            predictions = {}
            
            for target_name, model in self.models.items():
                if target_name not in self.scalers:
                    continue
                
                # Scale features
                features_scaled = self.scalers[target_name].transform(latest_features)
                
                # Make prediction
                prediction = model.predict(features_scaled)[0]
                
                # Add some uncertainty based on model performance
                uncertainty = 0.1 * abs(prediction)  # 10% uncertainty
                
                predictions[target_name] = {
                    'value': float(prediction),
                    'uncertainty': float(uncertainty),
                    'confidence': 'high' if uncertainty < 5 else 'medium' if uncertainty < 15 else 'low'
                }
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error making predictions: {e}")
            return {'error': str(e)}
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about trained models"""
        info = {}
        
        for target_name in self.target_columns:
            model_path = self.config.MODELS_DIR / f"{target_name}_model.pkl"
            scaler_path = self.config.MODELS_DIR / f"{target_name}_scaler.pkl"
            
            if model_path.exists() and scaler_path.exists():
                try:
                    model = joblib.load(model_path)
                    info[target_name] = {
                        'type': type(model).__name__,
                        'trained': True,
                        'last_modified': datetime.fromtimestamp(model_path.stat().st_mtime)
                    }
                except:
                    info[target_name] = {'trained': False, 'error': 'Corrupted model file'}
            else:
                info[target_name] = {'trained': False}
        
        return info

def main():
    """Train models from command line"""
    predictor = MLPredictor()
    
    print("Training ML models...")
    results = predictor.train_models()
    
    if results['success']:
        print("✅ Models trained successfully!")
        for target, metrics in results['results'].items():
            if 'error' not in metrics:
                print(f"{target}: MAE={metrics['mae']:.2f}, R²={metrics['r2']:.3f}")
    else:
        print(f"❌ Training failed: {results['message']}")

if __name__ == "__main__":
    main()
