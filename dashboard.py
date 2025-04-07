import pandas as pd
import dash
from dash import dcc, html
import plotly.graph_objects as go
import requests
from datetime import datetime

app = dash.Dash(__name__)
app.title = "US-30 Dashboard"

# ========== DATA LOADERS ==========
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

# ========== APP LAYOUT ==========
app.layout = html.Div([
    html.H1("US-30 Index (Dow Jones) - Live", style={"textAlign": "center"}),

    html.Div(id="summary-card", style={
        "textAlign": "center",
        "padding": "15px",
        "margin": "10px auto",
        "width": "400px",
        "borderRadius": "10px",
        "backgroundColor": "#e6f2ff",
        "boxShadow": "0 2px 5px rgba(0,0,0,0.1)",
        "fontSize": "16px",
        "fontFamily": "Arial"
    }),

    html.Div(id="last-update", style={
        "textAlign": "center",
        "color": "#555",
        "marginBottom": "20px",
        "fontSize": "14px"
    }),

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
        html.Label("Afficher les données sur :", style={"marginRight": "10px"}),
        dcc.Dropdown(
            id="time-filter",
            options=[
                {"label": "1 heure", "value": "1H"},
                {"label": "6 heures", "value": "6H"},
                {"label": "12 heures", "value": "12H"},
                {"label": "1 jour", "value": "1D"},
                {"label": "Tout", "value": "ALL"}
            ],
            value="ALL",
            style={"width": "300px", "margin": "auto"}
        )
    ], style={"textAlign": "center", "marginBottom": "20px"}),

    html.Div([
        html.Label("Afficher sous forme de bougies :", style={"marginRight": "10px"}),
        dcc.RadioItems(
            id="chart-type",
            options=[
                {"label": "Ligne", "value": "line"},
                {"label": "Bougies", "value": "candlestick"}
            ],
            value="line",
            labelStyle={"display": "inline-block", "marginRight": "20px"}
        )
    ], style={"textAlign": "center", "marginBottom": "20px"}),

    dcc.Graph(id="line-chart", figure={}, style={"width": "80%", "margin": "auto"}),

    html.Div([
        html.Label("Afficher :", style={"fontWeight": "bold", "marginRight": "10px"}),
        dcc.Checklist(
            id="options",
            options=[
                {"label": "Moyenne", "value": "mean"},
                {"label": "Volatilité", "value": "volatility"},
                {"label": "Prédiction naïve", "value": "prediction"}
            ],
            value=[],
            labelStyle={"display": "inline-block", "marginRight": "20px"}
        )
    ], style={"textAlign": "center", "marginTop": "20px", "marginBottom": "30px", "fontFamily": "Arial"})
], style={"backgroundColor": "#ffffff", "fontFamily": "Arial"})

# ========== CALLBACKS ==========
@app.callback(
    dash.dependencies.Output("line-chart", "figure"),
    [dash.dependencies.Input("options", "value"),
     dash.dependencies.Input("chart-type", "value"),
     dash.dependencies.Input("time-filter", "value")]
)
def update_chart(options, chart_type, time_filter):
    df = load_data()
    report = load_report()
    if df.empty:
        return {}

    # Filtrage
    if time_filter != "ALL":
        delta = pd.Timedelta(time_filter)
        df = df[df["timestamp"] > df["timestamp"].max() - delta]

    fig = go.Figure()

    if chart_type == "line":
        fig.add_trace(go.Scatter(
            x=df["timestamp"], y=df["value"],
            mode="lines", name="US-30 Value",
            line=dict(color="royalblue")
        ))

        if report and "mean" in options:
            fig.add_hline(y=report["mean"], line_dash="dash", line_color="green", name="Moyenne")

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

        if "prediction" in options:
            df_sorted = df.sort_values("timestamp")
            X = (df_sorted["timestamp"] - df_sorted["timestamp"].min()).dt.total_seconds().values.reshape(-1, 1)
            y = df_sorted["value"].values
            try:
                from sklearn.linear_model import LinearRegression
                model = LinearRegression().fit(X, y)
                future_X = [[X[-1][0] + 300]]  # 5 min plus tard
                future_y = model.predict(future_X)[0]
                fig.add_trace(go.Scatter(
                    x=[df_sorted["timestamp"].max(), df_sorted["timestamp"].max() + pd.Timedelta(minutes=5)],
                    y=[y[-1], future_y],
                    mode="lines", name="Tendance (naïve)",
                    line=dict(color="orange", dash="dot")
                ))
            except:
                pass

    else:
        df_resampled = df.set_index("timestamp").resample("1H").agg({
            "value": ["first", "max", "min", "last"]
        }).dropna()
        df_resampled.columns = ["open", "high", "low", "close"]
        df_resampled = df_resampled.reset_index()

        fig.add_trace(go.Candlestick(
            x=df_resampled["timestamp"],
            open=df_resampled["open"],
            high=df_resampled["high"],
            low=df_resampled["low"],
            close=df_resampled["close"],
            name="US-30 (OHLC)"
        ))

    fig.update_layout(
        title="US-30 Price Over Time",
        xaxis_title="Timestamp",
        yaxis_title="Price",
        template="plotly_white",
        hovermode="x unified"
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

@app.callback(
    dash.dependencies.Output("summary-card", "children"),
    dash.dependencies.Input("line-chart", "id")
)
def update_summary(_):
    report = load_report()
    if not report:
        return "Résumé non disponible."
    try:
        open_val = float(report["open"])
        close_val = float(report["close"])
        variation = (close_val - open_val) / open_val * 100
        trend = "📈 Haussière" if variation >= 0 else "📉 Baissière"
        alert = "⚠️ Volatilité inhabituelle détectée." if abs(variation) > 5 else ""
        return [
            html.Div(f"📅 {report['date']}"),
            html.Div(f"Dernier prix : {close_val:,.2f}"),
            html.Div(f"Variation : {variation:+.2f}%"),
            html.Div(f"Tendance : {trend}"),
            html.Div(alert, style={"color": "red", "marginTop": "10px"}) if alert else ""
        ]
    except:
        return "Erreur dans les données."

@app.callback(
    dash.dependencies.Output("last-update", "children"),
    dash.dependencies.Input("line-chart", "figure")
)
def update_timestamp(fig):
    df = load_data()
    if df.empty:
        return ""
    last_time = df["timestamp"].max()
    return f"Dernière mise à jour : {last_time.strftime('%d/%m/%Y %H:%M')}"

# ========== RUN APP ==========
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
