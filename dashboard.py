import pandas as pd
import dash
from dash import dcc, html
import plotly.graph_objects as go
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

    dcc.Graph(id="line-chart", figure={}, style={"width": "80%", "margin": "auto"}),

    html.Div([
        html.Label("Afficher :", style={"fontWeight": "bold", "marginRight": "10px"}),
        dcc.Checklist(
            id="options",
            options=[
                {"label": "Moyenne", "value": "mean"},
                {"label": "Volatilité", "value": "volatility"}
            ],
            value=[],
            labelStyle={"display": "inline-block", "marginRight": "20px"}
        )
    ], style={"textAlign": "center", "marginTop": "20px", "marginBottom": "30px", "fontFamily": "Arial"})
], style={"backgroundColor": "#ffffff", "fontFamily": "Arial"})

@app.callback(
    dash.dependencies.Output("line-chart", "figure"),
    dash.dependencies.Input("options", "value")
)
def update_chart(options):
    df = load_data()
    report = load_report()

    if df.empty:
        return {}

    fig = go.Figure()

    # Courbe principale
    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["value"],
        mode="lines", name="US-30 Value",
        line=dict(color="royalblue")
    ))

    # Moyenne
    if report and "mean" in options:
        fig.add_hline(y=report["mean"], line_dash="dash", line_color="green", name="Moyenne")

    # Zone de volatilité
    if report and "volatility" in options:
        mean = report["mean"]
        vol = report["volatility"]
        fig.add_trace(go.Scatter(
            x=list(df["timestamp"]) + list(df["timestamp"][::-1]),
            y=[mean + vol] * len(df) + [mean - vol] * len(df),
            fill='toself',
            fillcolor='rgba(255, 0, 0, 0.1)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            name="Zone de volatilité"
        ))

    fig.update_layout(
        title="US-30 Price Over Time",
        xaxis_title="Timestamp",
        yaxis_title="Price",
        template="plotly_white",
        hovermode="x unified",
        xaxis=dict(
            rangeselector=dict(
                buttons=[
                    dict(count=1, label="1h", step="hour", stepmode="backward"),
                    dict(count=6, label="6h", step="hour", stepmode="backward"),
                    dict(count=12, label="12h", step="hour", stepmode="backward"),
                    dict(count=1, label="1j", step="day", stepmode="backward"),
                    dict(step="all", label="All")
                ]
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )

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
