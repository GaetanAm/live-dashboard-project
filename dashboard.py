import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px

app = dash.Dash(__name__)
app.title = "US-30 Dashboard"

def load_data():
    df = pd.read_csv("data.csv", names=["timestamp", "value"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["value"] = pd.to_numeric(df["value"].str.replace(",", ""))
    return df

app.layout = html.Div([
    html.H1("US-30 Index (Dow Jones) - Live"),
    dcc.Graph(id="line-chart", figure={})
])

@app.callback(
    dash.dependencies.Output("line-chart", "figure"),
    dash.dependencies.Input("line-chart", "id")
)
def update_chart(_):
    df = load_data()
    fig = px.line(df, x="timestamp", y="value", title="US-30 Price Over Time")
    return fig

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)


