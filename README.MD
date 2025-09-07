# 🧠 Smart System Health Monitor v2.0

A comprehensive, real-time system health monitoring solution that tracks CPU, RAM, Disk, and Network usage with advanced machine learning predictions, multi-channel alerts, and a beautiful interactive dashboard. Now with enhanced features, better deployment options, and cross-platform support!

## ✨ What's New in v2.0

* 🎨 **Enhanced Dashboard**: Interactive charts with Plotly, real-time updates, and better UX
* 🤖 **Advanced ML**: Multiple algorithms, better predictions, and confidence intervals
* 📧 **Multi-Channel Alerts**: Telegram, Email, and Webhook support
* 🐳 **Easy Deployment**: Docker, Docker Compose, and local deployment options
* 🔧 **Cross-Platform**: Works on Windows, Linux, and macOS
* ⚙️ **Configuration Management**: Centralized config with environment variables
* 📊 **More Metrics**: Temperature, load average, process count, and more
* 🏥 **Health Analysis**: Intelligent system health scoring and recommendations

## 📦 Features

### 🔍 **Core Monitoring**
* **Real-time Resource Tracking**: CPU, RAM, Disk, Network usage
* **Advanced Metrics**: Temperature, load average, process count
* **Cross-Platform Support**: Windows, Linux, macOS
* **Intelligent Logging**: Automatic cleanup and retention management

### 📊 **Visualization & Analytics**
* **Interactive Dashboard**: Beautiful Streamlit interface with Plotly charts
* **Real-time Updates**: Live monitoring with auto-refresh
* **Historical Analysis**: Trend analysis and pattern recognition
* **Health Scoring**: Intelligent system health assessment

### 🤖 **Machine Learning**
* **Multiple Algorithms**: Random Forest, Gradient Boosting, Linear Regression
* **Predictive Analytics**: Future resource usage predictions
* **Confidence Intervals**: Uncertainty quantification for predictions
* **Auto-Retraining**: Models improve over time with new data

### 🚨 **Smart Alerting**
* **Multi-Channel Notifications**: Telegram, Email, Webhooks
* **Intelligent Thresholds**: Configurable alert levels
* **Rich Messages**: Detailed alerts with recommendations
* **Alert History**: Track and analyze past alerts

### 🚀 **Deployment Options**
* **Docker**: Containerized deployment with Docker Compose
* **Local**: Direct Python installation
* **Cloud Ready**: Easy deployment to cloud platforms
* **Auto-Setup**: Automated installation and configuration

## 🛠️ Tech Stack

* **Backend**: Python 3.8+, psutil, pandas, numpy
* **ML**: scikit-learn, joblib
* **Frontend**: Streamlit, Plotly
* **Notifications**: requests, smtplib
* **Deployment**: Docker, Docker Compose
* **Monitoring**: Cross-platform system monitoring

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/sam170203/smart-system-health-monitor.git
cd smart-system-health-monitor

# Copy and edit configuration
cp env.example .env
# Edit .env with your settings

# Deploy with Docker Compose
docker-compose up -d

# Access dashboard at http://localhost:8501
```

### Option 2: Local Installation

```bash
# Clone the repository
git clone https://github.com/sam170203/smart-system-health-monitor.git
cd smart-system-health-monitor

# Run automated setup
python setup.py

# Start the dashboard
streamlit run src/dashboard.py
```

### Option 3: Windows Deployment

```cmd
# Clone the repository
git clone https://github.com/sam170203/smart-system-health-monitor.git
cd smart-system-health-monitor

# Run Windows deployment script
deploy.bat
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with your configuration:

```env
# Monitoring Settings
MONITORING_INTERVAL=300
LOG_RETENTION_DAYS=30

# Alert Thresholds
CPU_THRESHOLD=80.0
RAM_THRESHOLD=80.0
DISK_THRESHOLD=90.0
NETWORK_THRESHOLD=500000

# Telegram Notifications
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

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
```

### Setting Up Telegram Bot

1. Create a bot with [@BotFather](https://t.me/botfather)
2. Get your bot token
3. Get your chat ID by messaging [@userinfobot](https://t.me/userinfobot)
4. Add both to your `.env` file

### Setting Up Email Notifications

1. Enable 2-factor authentication on your Gmail account
2. Generate an app password
3. Use your email and app password in the `.env` file

## 📁 Project Structure

```
smart-system-health-monitor/
├── src/                         # Source code
│   ├── __init__.py
│   ├── monitor.py              # Enhanced monitoring
│   ├── alerts.py               # Multi-channel alerting
│   ├── ml_predictor.py         # ML predictions
│   └── dashboard.py            # Enhanced dashboard
├── logs/                       # Monitoring data
├── models/                     # ML models
├── config/                     # Configuration files
├── config.py                   # Configuration management
├── monitor_enhanced.py         # Enhanced monitoring script
├── setup.py                    # Automated setup
├── deploy.sh                   # Linux/macOS deployment
├── deploy.bat                  # Windows deployment
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile.enhanced         # Enhanced Dockerfile
├── requirements.txt            # Python dependencies
├── env.example                 # Environment template
└── README.md                   # This file
```

## 🎯 Usage

### Dashboard Features

1. **Real-time Monitoring**: Live system metrics with auto-refresh
2. **Historical Analysis**: Interactive charts showing trends over time
3. **ML Predictions**: Future resource usage predictions with confidence intervals
4. **Health Analysis**: System health scoring and recommendations
5. **Alert Management**: View and manage alert history
6. **Configuration**: Easy access to system settings

### Monitoring Script

The enhanced monitoring script (`monitor_enhanced.py`) provides:

- Cross-platform system monitoring
- Intelligent alerting
- ML predictions
- Automatic log cleanup
- Comprehensive error handling

### API Integration

The system can be integrated with external services via webhooks:

```python
# Example webhook payload
{
    "timestamp": "2025-01-09T10:30:00",
    "alerts": ["High CPU Usage: 85.2%"],
    "metrics": {
        "cpu_usage": 85.2,
        "ram_usage": 67.8,
        "disk_usage": 45.3
    }
}
```

## 🔧 Advanced Configuration

### Custom Alert Thresholds

```env
# Customize alert thresholds
CPU_THRESHOLD=75.0
RAM_THRESHOLD=85.0
DISK_THRESHOLD=95.0
NETWORK_THRESHOLD=1000000
```

### ML Model Configuration

```env
# ML settings
ML_ENABLED=true
PREDICTION_HORIZON=15  # Predict 15 minutes ahead
```

### Monitoring Intervals

```env
# Adjust monitoring frequency
MONITORING_INTERVAL=180  # Monitor every 3 minutes
```

## 🐳 Docker Deployment

### Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Docker Only

```bash
# Build image
docker build -f Dockerfile.enhanced -t smart-system-monitor .

# Run container
docker run -d \
  --name smart-system-monitor \
  -p 8501:8501 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/models:/app/models \
  --env-file .env \
  smart-system-monitor
```

## 📊 Example Output

### Dashboard Screenshots

The dashboard provides:
- Real-time metrics with color-coded status
- Interactive time-series charts
- ML predictions with confidence intervals
- System health analysis
- Alert history and management

### Log Data Format

```csv
timestamp,cpu_usage,ram_usage,disk_usage,network_rx_kb,network_tx_kb,load_average,process_count,temperature_c
2025-01-09 10:30:00,25.4,67.8,45.3,125000,89000,1.2,156,45.2
2025-01-09 10:35:00,28.1,68.2,45.4,127500,91200,1.3,158,46.1
```

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📜 License

MIT License – feel free to use, improve, and contribute.

## 🆘 Support

- 📧 **Email**: Create an issue on GitHub
- 💬 **Discussions**: Use GitHub Discussions
- 📚 **Documentation**: Check the wiki
- 🐛 **Bug Reports**: Use GitHub Issues

## 🎉 Acknowledgments

Special thanks to:

* [Streamlit](https://streamlit.io) - Amazing dashboard framework
* [Plotly](https://plotly.com) - Interactive visualizations
* [scikit-learn](https://scikit-learn.org) - Machine learning library
* [psutil](https://psutil.readthedocs.io) - System monitoring
* [Docker](https://docker.com) - Containerization platform

---

**Made with ❤️ by the Smart System Health Monitor Team**
