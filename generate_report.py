import pandas as pd
import json
from datetime import datetime

df = pd.read_csv("data.csv", names=["timestamp", "value"])
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["value"] = pd.to_numeric(df["value"], errors="coerce")


today = pd.Timestamp.now().date()
df_today = df[df["timestamp"].dt.date == today]

open_price = df_today["value"].iloc[0]
close_price = df_today["value"].iloc[-1]
min_price = df_today["value"].min()
max_price = df_today["value"].max()
mean_price = df_today["value"].mean()
volatility = df_today["value"].std()

report = {
    "date": today.isoformat(),
    "open": round(open_price, 2),
    "close": round(close_price, 2),
    "min": round(min_price, 2),
    "max": round(max_price, 2),
    "mean": round(mean_price, 2),
    "volatility": round(volatility, 2)
}

with open("report.json", "w") as f:
    json.dump(report, f, indent=4)

print("Report generated:", report)
