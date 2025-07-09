import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os

st.set_page_config(page_title="Smart System Health Monitor", layout="wide")
st.title("💻 Smart System Health Monitor Dashboard")

CSV_PATH = "logs/system_metrics.csv"
MODEL_PATH = "python_analytics/cpu_predictor.pkl"

if not os.path.exists(CSV_PATH):
    st.error("Log file not found. Make sure system_metrics.csv exists.")
    st.stop()

# Load CSV
st.info(f"Reading from: {CSV_PATH}")
df = pd.read_csv(CSV_PATH)

# Ensure timestamp is datetime
if 'timestamp' in df.columns:
    df['timestamp'] = pd.to_datetime(df['timestamp'])

# Show raw data
with st.expander("🔍 View Raw System Data"):
    st.dataframe(df.tail(10), use_container_width=True)

# Line chart
st.subheader("📊 CPU, RAM & Network Usage Over Time")
st.line_chart(df.set_index("timestamp")[['cpu', 'ram', 'network_kb']])

# CPU Usage Heatmap
st.subheader("🔥 CPU Usage Distribution")
fig, ax = plt.subplots()
sns.histplot(df['cpu'], kde=True, color="skyblue", ax=ax)
ax.set_xlabel("CPU Usage (%)")
st.pyplot(fig)

# Suggestion Based on Last Row
latest = df.iloc[-1]
suggestions = []

if latest['cpu'] > 80:
    suggestions.append("⚠️ High CPU usage detected. Consider closing unnecessary applications.")
if latest['ram'] > 80:
    suggestions.append("⚠️ RAM usage is high. You may want to upgrade RAM or stop memory-heavy apps.")
if latest['disk'] > 90:
    suggestions.append("⚠️ Low disk space. Consider cleaning temporary files or extending your storage.")

st.subheader("💡 System Health Suggestions")
if suggestions:
    for s in suggestions:
        st.warning(s)
else:
    st.success("✅ System health is within normal range.")

# ML Prediction
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    input_features = latest[['ram', 'disk', 'network_kb']].values.reshape(1, -1)
    predicted_cpu = model.predict(input_features)[0]

    st.subheader("🤖 Predicted CPU Usage (Next 5 min)")
    st.metric(label="Predicted CPU (%)", value=f"{predicted_cpu:.2f}")
else:
    st.error(f"ML model not found at {MODEL_PATH}. Please train the model first.")

# Footer
st.markdown("---")
st.caption("Built with ❤️ by Smart System Health Monitor")

