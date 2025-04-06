import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px

app = dash.Dash(__name__)
app.title = "US-30 Dashboard"

def load_data():
    df = pd.read_csv("https://raw.githubusercontent.com/GaetanAm/live-dashboard-project/main/data.csv", names=["timestamp", "value"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["value"] = pd.to_numeric(df["value"].str.replace(",", ""))
    return df

import requests

def load_report():
    try:
        url = "https://raw.githubusercontent.com/GaetanAm/live-dashboard-project/main/report.json"
        r = requests.get(url)
        return r.json()
    except:
        return None


app.layout = html.Div([
    html.H1("US-30 Index (Dow Jones) - Live"),html.Div(id="daily-report"),
    dcc.Graph(id="line-chart", figure={})
])

@app.callback(
    dash.dependencies.Output("line-chart", "figure"),
    dash.dependencies.Input("line-chart", "id")
)
def update_chart(_):
    df = load_data()
    print("📊 DF utilisé pour le graph :")
    print(df.head())

    if df.empty:
        print("🚨 DF est vide !")
        return {}

    fig = px.line(df, x="timestamp", y="value", title="US-30 Price Over Time")
    return fig



@app.callback(
    dash.dependencies.Output("daily-report", "children"),
    dash.dependencies.Input("line-chart", "id")
)
def update_report(_):
    report = load_report()
    if not report:
        return "No report available yet."
    return html.Ul([
        html.Li(f"Date: {report['date']}"),
        html.Li(f"Open: {report['open']}"),
        html.Li(f"Close: {report['close']}"),
        html.Li(f"Min: {report['min']}"),
        html.Li(f"Max: {report['max']}"),
        html.Li(f"Mean: {report['mean']}"),
        html.Li(f"Volatility: {report['volatility']}")
    ])



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)


