#!/bin/bash

LOG_DIR="/home/icro_igsakshamudgalll17/smart-system-health-monitor/logs"
THRESHOLD_MINUTES=720
BOT_TOKEN="7530245982:AAFSe04FELYzTWQVyFb3nnWVH_3vHX66r94"
CHAT_ID="1297377435"

DELETED_FILES=$(find "$LOG_DIR" -type f -name "*.csv" -mmin +$THRESHOLD_MINUTES)

if [ -n "$DELETED_FILES" ]; then
    find "$LOG_DIR" -type f -name "*.csv" -mmin +$THRESHOLD_MINUTES -delete

    MESSAGE="🗑️ Deleted old CSV logs older than 12 hours:\n$DELETED_FILES"
    
    curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
         -d chat_id="$CHAT_ID" \
         -d text="$MESSAGE" > /dev/null
fi
