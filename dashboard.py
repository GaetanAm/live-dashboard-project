import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px
import requests

app = dash.Dash(__name__)
app.title = "US-30 Dashboard"

def load_data():
    df = pd.read_csv(
        "https://raw.githubusercontent.com/GaetanAm/live-dashboard-project/main/data.csv",
        names=["timestamp", "value"]
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["value"] = df["value"].astype(str).str.replace(",", "")
    df["value"] = pd.to_numeric(df["value"])
    return df

def load_report():
    try:
        url = "https://raw.githubusercontent.com/GaetanAm/live-dashboard-project/main/report.json"
        r = requests.get(url)
        return r.json()
    except:
        return None

app.layout = html.Div([
    html.H1("US-30 Index (Dow Jones) - Live", style={"textAlign": "center"}),

    html.Div(id="daily-report", style={
        "backgroundColor": "#f9f9f9",
        "padding": "20px",
        "borderRadius": "10px",
        "boxShadow": "0 2px 5px rgba(0,0,0,0.1)",
        "width": "400px",
        "margin": "auto",
        "marginBottom": "30px",
        "fontFamily": "Arial"
    }),

    html.Div([
        html.H3("Dernière valeur :", style={"display": "inline"}),
        html.Span(id="last-value", style={"fontWeight": "bold"})
    ], style={"textAlign": "center", "marginBottom": "20px"}),

    dcc.Graph(id="line-chart", figure={}, style={"width": "80%", "margin": "auto"})
], style={"backgroundColor": "#ffffff", "fontFamily": "Arial"})


@app.callback(
    dash.dependencies.Output("line-chart", "figure"),
    dash.dependencies.Input("line-chart", "id")
)
def update_chart(_):
    df = load_data()
    if df.empty:
        return {}

    color = "green" if df["value"].iloc[-1] >= df["value"].iloc[0] else "red"
    fig = px.line(df, x="timestamp", y="value", title="US-30 Price Over Time")
    fig.update_traces(line=dict(color=color, width=2.5))
    fig.update_layout(plot_bgcolor="#f5f5f5")
    return fig


@app.callback(
    dash.dependencies.Output("last-value", "children"),
    dash.dependencies.Input("line-chart", "figure")
)
def update_last_value(_):
    df = load_data()
    if df.empty:
        return "N/A"
    return f"{df['value'].iloc[-1]:,.2f}"


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
