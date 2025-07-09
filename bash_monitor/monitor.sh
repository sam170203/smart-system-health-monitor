#!/bin/bash

#!/bin/bash

source ~/.profile
source ~/.bashrc
source /home/icro_igsakshamudgalll17/smart-system-health-monitor/python_analytics/venv/bin/activate
cd /home/icro_igsakshamudgalll17/smart-system-health-monitor/python_analytics


# File to log system stats
LOG_FILE="../logs/system_stats.csv"

# If the log file doesn't exist, create it with headers
if [ ! -f "$LOG_FILE" ]; then
    echo "timestamp,cpu_usage,ram_usage,disk_usage,net_rx_kb,net_tx_kb" > "$LOG_FILE"
fi

# Collect system metrics
timestamp=$(date '+%Y-%m-%d %H:%M:%S')
cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print 100 - $8}')
ram_usage=$(free | grep Mem | awk '{print ($3/$2) * 100.0}')
disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
net_rx_kb=$(cat /proc/net/dev | grep eth0 | awk '{print $2 / 1024}')
net_tx_kb=$(cat /proc/net/dev | grep eth0 | awk '{print $10 / 1024}')

# Append data to CSV
echo "$timestamp,$cpu_usage,$ram_usage,$disk_usage,$net_rx_kb,$net_tx_kb" >> "$LOG_FILE"

# Thresholds
CPU_THRESHOLD=80
RAM_THRESHOLD=80

# Get current values
CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}')
RAM=$(free | awk '/Mem:/ {printf("%.2f"), $3/$2 * 100.0}')

# Send Telegram alert if above threshold
if (( $(echo "$CPU > $CPU_THRESHOLD" | bc -l) )); then
    python3 -c "from telegram_alert import send_telegram_alert; send_telegram_alert('🚨 *High CPU Usage Alert* 🔥\nCPU usage is at ${CPU}%')"
fi

if (( $(echo "$RAM > $RAM_THRESHOLD" | bc -l) )); then
    python3 -c "from telegram_alert import send_telegram_alert; send_telegram_alert('🚨 *High RAM Usage Alert* 🧠\nRAM usage is at ${RAM}%')"
fi
