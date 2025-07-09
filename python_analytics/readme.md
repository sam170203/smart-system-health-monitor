# 🧠 Smart System Health Monitor

A real-time system health monitoring tool that tracks CPU, RAM, Disk, and Network usage, logs data into CSV, predicts future usage using machine learning, sends Telegram alerts for threshold breaches, and presents visualizations on a beautiful **Streamlit dashboard**.

## 📦 Features

* 🔤️ **Resource Monitoring**: Bash script tracks CPU, memory, disk, and network usage.
* 📊 **Streamlit Dashboard**: Live visual analytics of system metrics.
* 🧠 **ML Predictions**: Predicts future CPU usage using a trained ML model.
* 📈 **Graphical Plots**: Plots trends of CPU and RAM usage with suggestions.
* 📩 **Telegram Alerts**: Sends alerts when thresholds are exceeded.
* 🔄 **Auto Logging**: Logs every 5 mins via cron.
* 🧹 **Auto Cleanup**: Supports auto-deletion of old logs (optional).
* 🛣️ **Docker Support**: Runs inside a lightweight container (optional).
* 📁 **GitHub Repo**: [https://github.com/sam170203/smart-system-health-monitor](https://github.com/sam170203/smart-system-health-monitor)

---

## 🛠️ Tech Stack

* **Linux (WSL2) + Bash**
* **Python 3.10**
* **Streamlit**
* **Scikit-learn, Pandas, Matplotlib, Seaborn**
* **Docker (optional)**
* **Telegram Bot API**

---

## 🚀 Setup Instructions

### ⚖️ Prerequisites

* Python 3.10+
* pip
* `virtualenv`
* Telegram Bot Token & Chat ID

---

### ⚙️ Installation (without Docker)

```bash
# Clone the repo
git clone https://github.com/sam170203/smart-system-health-monitor.git
cd smart-system-health-monitor

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r python_analytics/requirements.txt

# Train ML model (first time only)
python3 python_analytics/train_model.py
```

---

### 🔤️ Run Dashboard

```bash
streamlit run python_analytics/dashboard.py
```

Visit [http://localhost:8501](http://localhost:8501)

---

### 📋 Monitor System Resources (every 5 mins)

Add to crontab:

```bash
crontab -e
```

Add:

```bash
*/5 * * * * /bin/bash ~/smart-system-health-monitor/monitor.sh
```

---

### 📧 Telegram Alerts

Add your `BOT_TOKEN` and `CHAT_ID` in `python_analytics/.env`:

```env
BOT_TOKEN=your_bot_token
CHAT_ID=your_chat_id
```

---

### 🛣️ Run with Docker (optional)

```bash
docker build -t system-health-monitor .
docker run -d -p 8501:8501 --env-file python_analytics/.env --name monitor system-health-monitor
```

---

## 📁 Project Structure

```
smart-system-health-monitor/
├── monitor.sh                   # System stats logger
├── logs/                        # Logs CSV
├── python_analytics/           # Python scripts
│   ├── dashboard.py            # Streamlit dashboard
│   ├── analyze.py              # Data analyzer
│   ├── alert.py                # Alert logic
│   ├── telegram_alert.py       # Telegram notification
│   ├── train_model.py          # Train ML model
│   ├── cpu_predictor.pkl       # Trained model
├── Dockerfile
├── requirements.txt
```

---

## 📊 Example Output

* `logs/system_metrics.csv`:

  ```
  timestamp,cpu,ram,disk,network_kb
  2025-07-09 14:05:01,2.4,8.37,1,372558
  2025-07-09 14:10:01,7.0,8.47,1,372568
  ```

---

## 📜 License

MIT License – feel free to use, improve, and contribute.

---

## 🤝 Acknowledgements

Special thanks to:

* [Streamlit](https://streamlit.io)
* [scikit-learn](https://scikit-learn.org)
* [Telegram Bot API](https://core.telegram.org/bots/api)
