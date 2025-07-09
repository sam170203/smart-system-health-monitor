import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np
import os

def get_health_suggestions(cpu, ram, disk, net_rx, net_tx):
    suggestions = []

    if cpu > 70:
        suggestions.append("🔴 **High CPU Usage:** Heavy applications or too many background tasks.")
        suggestions.append("💡 Use `top` or `htop` to see which processes are using the CPU.")

    if ram > 80:
        suggestions.append("🔴 **High RAM Usage:** Possible memory leak or big apps running.")
        suggestions.append("💡 Use `free -m` and `ps aux --sort=-%mem | head` to inspect RAM usage.")

    if disk > 80:
        suggestions.append("🔴 **Disk Almost Full:** Could lead to slowdowns or crashes.")
        suggestions.append("💡 Use `df -h` and `du -sh *` to check which folders are taking space.")

    if net_rx > 500000 or net_tx > 500000:
        suggestions.append("🔴 **High Network Activity:** Possible downloads, updates, or remote syncs.")
        suggestions.append("💡 Use `iftop` or `nethogs` to check network-heavy processes.")

    if not suggestions:
        suggestions.append("✅ System health looks good! No critical issues found.")

    return suggestions



# Load data
log_path = "../logs/system_stats.csv"
if not os.path.exists(log_path):
    st.error("Log file not found. Make sure cron has generated some data.")
    st.stop()

data = pd.read_csv(log_path, parse_dates=["timestamp"])

st.title("📊 Smart System Health Monitor Dashboard")

# Show latest entry
st.subheader("🧠 Latest System Stats")
st.write(data.tail(1))

# Time-based trend plots
st.subheader("📈 Resource Usage Over Time")
metrics = ["cpu_usage", "ram_usage", "disk_usage", "net_rx_kb", "net_tx_kb"]
for metric in metrics:
    st.write(f"**{metric.replace('_', ' ').title()}**")
    plt.figure(figsize=(10, 3))
    plt.plot(data["timestamp"], data[metric], label=metric)
    plt.xlabel("Time")
    plt.ylabel(metric)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt)

# Predict future CPU and RAM usage
st.subheader("🔮 Prediction: Resource Usage in 10 Minutes")
latest = data.iloc[-1]
cpu = latest["cpu_usage"]
ram = latest["ram_usage"]
disk = latest["disk_usage"]
net_rx = latest["net_rx_kb"]
net_tx = latest["net_tx_kb"]

st.subheader("🛠️ System Health Suggestions")
tips = get_health_suggestions(cpu, ram, disk, net_rx, net_tx)
for tip in tips:
    st.markdown(tip)


def predict_usage(metric_name):
    st.write(f"**Predicting {metric_name.replace('_', ' ').title()}**")
    if len(data) < 2:
        st.warning("Not enough data to predict.")
        return
    data["minutes"] = (data["timestamp"] - data["timestamp"].min()).dt.total_seconds() / 60
    X = data[["minutes"]]
    y = data[metric_name]
    model = LinearRegression()
    model.fit(X, y)
    future_minute = np.array([[X["minutes"].max() + 10]])
    prediction = model.predict(future_minute)[0]
    st.info(f"Estimated {metric_name.replace('_', ' ')} after 10 min: **{prediction:.2f}**")

predict_usage("cpu_usage")
predict_usage("ram_usage")
