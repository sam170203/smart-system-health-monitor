import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

# Load the CSV data
df = pd.read_csv("logs/system_metrics.csv")

# Prepare features and target
X = df[['ram', 'disk', 'network_kb']]  # You can add more features if needed
y = df['cpu']

# Train model
model = LinearRegression()
model.fit(X, y)

# Save model
joblib.dump(model, 'python_analytics/cpu_predictor.pkl')

print("✅ Model trained and saved to 'python_analytics/cpu_predictor.pkl'")
