#!/bin/bash

# Timestamp
timestamp=$(date +"%Y-%m-%d %H:%M:%S")

# CPU Usage
cpu=$(top -bn1 | grep "Cpu(s)" | awk '{print 100 - $8}')
cpu=$(printf "%.2f" "$cpu")

# RAM Usage
ram=$(free | grep Mem | awk '{print $3/$2 * 100.0}')
ram=$(printf "%.2f" "$ram")

# Disk Usage
disk=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//g')

# Network usage (rx+tx in KB)
net_rx=$(cat /sys/class/net/$(ip route show default | awk '/default/ {print $5}')/statistics/rx_bytes)
net_tx=$(cat /sys/class/net/$(ip route show default | awk '/default/ {print $5}')/statistics/tx_bytes)
net_total_kb=$(( (net_rx + net_tx) / 1024 ))

# Log to CSV
echo "$timestamp,$cpu,$ram,$disk,$net_total_kb" >> ~/smart-system-health-monitor/logs/system_metrics.csv

# CPU Alert
if (( $(echo "$cpu > 80" | bc -l) )); then
    python3 ~/smart-system-health-monitor/python_analytics/telegram_alert.py "🚨 High CPU Usage: ${cpu}%"
fi

# RAM Alert
if (( $(echo "$ram > 80" | bc -l) )); then
    python3 ~/smart-system-health-monitor/python_analytics/telegram_alert.py "🚨 High RAM Usage: ${ram}%"
fi

# Disk Alert
if (( $(echo "$disk > 90" | bc -l) )); then
    python3 ~/smart-system-health-monitor/python_analytics/telegram_alert.py "🚨 High Disk Usage: ${disk}%"
fi
