import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
import datetime

# CSV path
csv_path = "../logs/system_stats.csv"

# Load CSV into DataFrame
df = pd.read_csv(csv_path, parse_dates=['timestamp'])

# Display head for sanity check
print("🧠 Showing recent system stats:")
print(df.tail())

# 📊 Plot CPU usage over time
def plot_metric(metric):
    plt.figure(figsize=(10, 4))
    sns.lineplot(data=df, x='timestamp', y=metric)
    plt.xticks(rotation=45)
    plt.title(f"{metric.upper()} Over Time")
    plt.tight_layout()
    plt.savefig(f"{metric}_plot.png")
    plt.show()

# 🔮 Predict next hour's usage using Linear Regression
def predict_next_hour(metric):
    print(f"\n🔮 Predicting {metric} for the next hour:")
    
    # Convert timestamp to numeric for ML
    df['time_num'] = df['timestamp'].astype('int64') // 10**9  # seconds

    # Select last N rows (e.g., last 6 entries = 1 hour if 10-min intervals)
    recent = df.tail(6)

    X = recent[['time_num']]
    y = recent[metric]

    model = LinearRegression()
    model.fit(X, y)

    # Predict for next timestamp (10 mins later)
    next_time = recent['time_num'].max() + 600
    prediction = model.predict([[next_time]])
    print(f"🔧 Estimated {metric} in next 10 min: {round(prediction[0], 2)}%")

# Run all
for metric in ['cpu_usage', 'ram_usage']:
    plot_metric(metric)
    predict_next_hour(metric)

# Recommendation
if df['ram_usage'].tail(6).mean() > 80:
    print("⚠️ RAM usage has been high recently. Consider upgrading memory or restarting heavy apps.")

from alert import send_alert

if latest['ram_usage'].values[0] > 80:
    send_alert(
        "🚨 High RAM Usage Alert",
        f"RAM usage is at {latest['ram_usage'].values[0]:.2f}% on your system!"
    )

