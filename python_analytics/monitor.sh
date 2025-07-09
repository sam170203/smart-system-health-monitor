#!/bin/bash

timestamp=$(date +"%Y-%m-%d %H:%M:%S")

cpu=$(top -bn1 | grep "Cpu(s)" | awk '{print 100 - $8}')
cpu=$(printf "%.2f" "$cpu")

ram=$(free | grep Mem | awk '{print $3/$2 * 100.0}')
ram=$(printf "%.2f" "$ram")

disk=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//g')

iface=$(ip route show default | awk '/default/ {print $5}')
net_rx=$(cat /sys/class/net/${iface}/statistics/rx_bytes)
net_tx=$(cat /sys/class/net/${iface}/statistics/tx_bytes)
net_total_kb=$(( (net_rx + net_tx) / 1024 ))

logfile="logs/system_metrics.csv"
mkdir -p logs
if [ ! -f "$logfile" ]; then
    echo "timestamp,cpu,ram,disk,network_kb" > "$logfile"
fi

echo "$timestamp,$cpu,$ram,$disk,$net_total_kb" >> "$logfile"

# Alerts
if (( $(echo "$cpu > 80" | bc -l) )); then
    python3 python_analytics/telegram_alert.py "🚨 High CPU Usage: ${cpu}%"
fi

if (( $(echo "$ram > 80" | bc -l) )); then
    python3 python_analytics/telegram_alert.py "🚨 High RAM Usage: ${ram}%"
fi

if (( $(echo "$disk > 90" | bc -l) )); then
    python3 python_analytics/telegram_alert.py "🚨 Disk almost full: ${disk}%"
fi
