import pandas as pd
import dash
from dash import dcc, html
import plotly.graph_objects as go
import requests
from datetime import datetime
from dash.dependencies import Input, Output, State, ClientsideFunction
import io
import base64

external_scripts = []
external_stylesheets = []

app = dash.Dash(__name__, external_scripts=external_scripts, external_stylesheets=external_stylesheets)
app.title = "US-30 Dashboard"

def get_container_style(theme, base_color="#f9f9f9"):
    if theme == "plotly_dark":
        return {
            "backgroundColor": "#1e1e1e",
            "color": "white",
            "padding": "20px",
            "borderRadius": "10px",
            "boxShadow": "0 2px 5px rgba(0,0,0,0.3)",
            "width": "500px",
            "margin": "20px auto",
            "fontFamily": "Arial"
        }
    else:
        return {
            "backgroundColor": base_color,
            "color": "black",
            "padding": "20px",
            "borderRadius": "10px",
            "boxShadow": "0 2px 5px rgba(0,0,0,0.1)",
            "width": "500px",
            "margin": "20px auto",
            "fontFamily": "Arial"
        }

# ========== DATA LOADERS ==========
def load_data():
    df = pd.read_csv(
        "https://raw.githubusercontent.com/GaetanAm/live-dashboard-project/main/data.csv",
        names=["timestamp", "value"]
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"])
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
    dcc.Store(id="theme-store", storage_type="local"),

    html.H1("US-30 Index (Dow Jones) - Live", style={"textAlign": "center"}),

    html.Div([
        html.Label("Mode d'affichage :"),
        dcc.RadioItems(
            id="theme-toggle",
            options=[
                {"label": "Clair", "value": "plotly_white"},
                {"label": "Sombre", "value": "plotly_dark"}
            ],
            value="plotly_white",
            labelStyle={"display": "inline-block", "marginRight": "20px"}
        )
    ], style={"textAlign": "center", "marginBottom": "10px"}),

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

    html.Div(id="history-list", style={
        "backgroundColor": "#f2f2f2",
        "padding": "20px",
        "borderRadius": "10px",
        "width": "500px",
        "margin": "20px auto",
        "fontFamily": "Arial",
        "boxShadow": "0 2px 5px rgba(0,0,0,0.1)"
    }),

    html.Div([
        html.Label("Afficher les données sur :", title="Filtrer les dernières données"),
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
        html.Label("Afficher sous forme de bougies :", title="Choisissez le type de graphique"),
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

    html.Div([
        html.Label("Afficher :", style={"fontWeight": "bold", "marginRight": "10px"}),
        dcc.Checklist(
            id="options",
            options=[
                {"label": "Moyenne (mean)", "value": "mean"},
                {"label": "Volatilité", "value": "volatility"},
                {"label": "Prédiction naïve", "value": "prediction"},
                {"label": "SMA (1h)", "value": "sma"},
                {"label": "Anomalies (spikes)", "value": "anomaly"}
            ],
            value=[],
            labelStyle={"display": "inline-block", "marginRight": "20px"}
        )
    ], style={"textAlign": "center", "marginTop": "20px", "marginBottom": "30px", "fontFamily": "Arial"}),

    dcc.Graph(id="line-chart", figure={}, style={"width": "90%", "margin": "auto"}),

    html.Div([
        html.Button("📅 Télécharger les données", id="download-btn"),
        dcc.Download(id="download-data"),

    ], style={"textAlign": "center", "marginTop": "20px"}),

    html.Footer([
        html.Hr(),
        html.Div("Projet réalisé par GaetanAm", style={"textAlign": "center"}),
        html.Div([
            html.A("🔗 GitHub", href="https://github.com/GaetanAm/live-dashboard-project", target="_blank", style={"marginRight": "15px"}),
            html.A("📊 Source: Investing.com", href="https://www.investing.com/indices/us-30", target="_blank")
        ], style={"textAlign": "center", "padding": "10px"})
    ], style={"marginTop": "40px", "backgroundColor": "#f1f1f1", "padding": "10px 0"})
], id="main-container", style={"backgroundColor": "#ffffff", "fontFamily": "Arial"})

@app.callback(
    Output("main-container", "style"),
    Input("theme-toggle", "value")
)
def toggle_theme(theme):
    bg = "#ffffff" if theme == "plotly_white" else "#121212"
    text = "#000000" if theme == "plotly_white" else "#ffffff"
    return {
        "backgroundColor": bg,
        "color": text,
        "fontFamily": "Arial"
    }


# ========== CALLBACKS ==========
@app.callback(
    Output("line-chart", "figure"),
    [Input("options", "value"), Input("chart-type", "value"), Input("time-filter", "value"), Input("theme-toggle", "value")]
)
def update_chart(options, chart_type, time_filter, theme):
    df = load_data()
    report = load_report()
    if df.empty:
        return {}

    if time_filter != "ALL":
        delta = pd.Timedelta(time_filter)
        df = df[df["timestamp"] > df["timestamp"].max() - delta]

    fig = go.Figure()

    if chart_type == "line":
        fig.add_trace(go.Scatter(x=df["timestamp"], y=df["value"], mode="lines", name="US-30 Value", line=dict(color="royalblue")))

        if "sma" in options:
            sma = df.set_index("timestamp")["value"].rolling("1H").mean()
            fig.add_trace(go.Scatter(x=sma.index, y=sma.values, mode="lines", name="SMA (1h)", line=dict(color="orange", dash="dot")))

        if report and "mean" in options:
            fig.add_hline(y=report["mean"], line_dash="dash", line_color="green", name="Moyenne")

        if report and "volatility" in options:
            mean, vol = report["mean"], report["volatility"]
            fig.add_trace(go.Scatter(
                x=list(df["timestamp"]) + list(df["timestamp"][::-1]),
                y=[mean + vol] * len(df) + [mean - vol] * len(df),
                fill='toself', fillcolor='rgba(255, 0, 0, 0.1)',
                line=dict(color='rgba(255,255,255,0)'), hoverinfo="skip", name="Zone de volatilité"
            ))

        if "prediction" in options:
            from sklearn.linear_model import LinearRegression
            df_sorted = df.sort_values("timestamp")
            X = (df_sorted["timestamp"] - df_sorted["timestamp"].min()).dt.total_seconds().values.reshape(-1, 1)
            y = df_sorted["value"].values
            model = LinearRegression().fit(X, y)
            future_X = [[X[-1][0] + 300]]
            future_y = model.predict(future_X)[0]
            fig.add_trace(go.Scatter(
                x=[df_sorted["timestamp"].max(), df_sorted["timestamp"].max() + pd.Timedelta(minutes=5)],
                y=[y[-1], future_y], mode="lines", name="Tendance (naïve)",
                line=dict(color="purple", dash="dash")
            ))

        if "anomaly" in options:
            std_dev = df["value"].std()
            mean_val = df["value"].mean()
            anomalies = df[(df["value"] > mean_val + 2 * std_dev) | (df["value"] < mean_val - 2 * std_dev)]
            fig.add_trace(go.Scatter(
                x=anomalies["timestamp"], y=anomalies["value"], mode="markers", name="Anomalies",
                marker=dict(color="red", size=8, symbol="x")
            ))

    else:
        df_resampled = df.set_index("timestamp").resample("1H").agg({"value": ["first", "max", "min", "last"]}).dropna()
        df_resampled.columns = ["open", "high", "low", "close"]
        df_resampled = df_resampled.reset_index()
        fig.add_trace(go.Candlestick(
            x=df_resampled["timestamp"],
            open=df_resampled["open"], high=df_resampled["high"],
            low=df_resampled["low"], close=df_resampled["close"],
            name="US-30 (OHLC)"
        ))

    fig.update_layout(
        title="US-30 Price Over Time",
        xaxis_title="Timestamp",
        yaxis_title="Price",
        template=theme,
        hovermode="x unified"
    )
    return fig

@app.callback(
    Output("daily-report", "children"),
    Output("daily-report", "style"),
    Input("line-chart", "id"),
    Input("theme-toggle", "value")
)
def update_report(_, theme):
    report = load_report()
    if not report:
        return "No report available yet.", get_container_style(theme)
    return html.Ul([
        html.Li(f"Date: {report['date']}"),
        html.Li(f"Open: {report['open']}"),
        html.Li(f"Close: {report['close']}"),
        html.Li(f"Min: {report['min']}"),
        html.Li(f"Max: {report['max']}"),
        html.Li(f"Mean: {report['mean']}"),
        html.Li(f"Volatility: {report['volatility']}")
    ]), get_container_style(theme)


@app.callback(
    Output("summary-card", "children"),
    Output("summary-card", "style"),
    Input("line-chart", "id"),
    Input("theme-toggle", "value")
)
def update_summary(_, theme):
    report = load_report()
    if not report:
        return "Résumé non disponible.", get_container_style(theme, "#e6f2ff")
    try:
        open_val, close_val = float(report["open"]), float(report["close"])
        variation = (close_val - open_val) / open_val * 100
        trend = "📈 Haussière" if variation >= 0 else "📉 Baissière"
        alert = "⚠️ Volatilité inhabituelle détectée." if abs(variation) > 5 else ""
        return [
            html.Div(f"📅 {report['date']}"),
            html.Div(f"Dernier prix : {close_val:,.2f}"),
            html.Div(f"Variation : {variation:+.2f}%"),
            html.Div(f"Tendance : {trend}"),
            html.Div(alert, style={"color": "red", "marginTop": "10px"}) if alert else ""
        ], get_container_style(theme, "#e6f2ff")
    except:
        return "Erreur dans les données.", get_container_style(theme, "#e6f2ff")


@app.callback(
    Output("last-update", "children"),
    Input("line-chart", "figure")
)
def update_timestamp(fig):
    df = load_data()
    if df.empty:
        return ""
    last_time = df["timestamp"].max()
    return f"Dernière mise à jour : {last_time.strftime('%d/%m/%Y %H:%M')}"

@app.callback(
    Output("history-list", "children"),
    Output("history-list", "style"),
    Input("line-chart", "figure"),
    Input("theme-toggle", "value")
)
def display_history(_, theme):
    df = load_data()
    if df.empty:
        return "", get_container_style(theme, "#f2f2f2")
    df_day = df.copy()
    df_day["date"] = df_day["timestamp"].dt.date
    grouped = df_day.groupby("date")["value"]
    html_list = [
        html.Div(f"📅 {date} — Clôture : {values.iloc[-1]:,.2f} — Vol : {values.std():.2f}")
        for date, values in grouped
    ][-5:]
    return html.Div([
        html.H4("Historique journalier :"),
        html.Ul([html.Li(item) for item in html_list])
    ]), get_container_style(theme, "#f2f2f2")


@app.callback(
    Output("download-data", "data"),
    Input("download-btn", "n_clicks"),
    prevent_initial_call=True
)
def download_csv(n):
    df = load_data()
    csv = df.to_csv(index=False)
    return dict(content=csv, filename="us30_data.csv")


    
# ========== RUN APP ==========
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
