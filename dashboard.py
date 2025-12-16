import base64
import io
from pathlib import Path

import numpy as np
import pandas as pd
from dash import Dash, html, dcc, Input, Output, State, no_update
from dash import dash_table
from plotly.subplots import make_subplots
import plotly.express as px

# ======================================================
# CONFIG
# ======================================================
APP_TITLE = "ECOv2 Stability Data Analysis"
DATA_CSV = "data.csv"

METRICS = ["HGO", "LGO", "LTC", "RAW", "VMain"]

COLOR_POOL = px.colors.qualitative.Plotly

# ======================================================
# App
# ======================================================
app = Dash(__name__)
app.title = APP_TITLE

# ======================================================
# Helpers
# ======================================================
def parse_uploaded_csv(contents):
    decoded = base64.b64decode(contents.split(",", 1)[1])
    return pd.read_csv(io.BytesIO(decoded))


def ensure_columns(df):
    if "SerialNumber" not in df.columns:
        raise ValueError("Missing SerialNumber column")

    df = df.copy()
    df["SerialID"] = df["SerialNumber"].astype(str).str.strip()
    df["Channel"] = pd.to_numeric(df["Channel"], errors="coerce").astype("Int64")
    df["SampleCount"] = pd.to_numeric(df["SampleCount"], errors="coerce")
    df["X"] = df["SampleCount"]

    if {"Date", "Time"}.issubset(df.columns):
        df["Timestamp"] = pd.to_datetime(
            df["Date"].astype(str) + " " + df["Time"].astype(str),
            errors="coerce",
        )
    elif "FileMTime" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["FileMTime"], unit="s", errors="coerce")
    else:
        df["Timestamp"] = pd.NaT

    return df


def add_run_index(df):
    df = df.sort_values(["SerialID", "Channel", "X"], kind="mergesort")
    df["RunIndex"] = (
        df.groupby(["SerialID", "Channel"])["X"]
        .diff()
        .fillna(1)
        .lt(0)
        .groupby([df["SerialID"], df["Channel"]])
        .cumsum()
    )
    return df


def keep_latest_run_only(df):
    latest = df.groupby(["SerialID", "Channel"])["RunIndex"].transform("max")
    return df[df["RunIndex"] == latest]


# ======================================================
# Layout
# ======================================================
app.layout = html.Div(
    style={"maxWidth": "1600px", "margin": "0 auto", "padding": "16px"},
    children=[
        dcc.Store(id="data-store"),

        html.H2(APP_TITLE, style={"textAlign": "center"}),

        dcc.Upload(
            id="upload-csv",
            children=html.Div("📂 Drag & Drop master data.csv"),
        ),

        html.Hr(),

        html.Div(
            style={"display": "flex", "gap": "12px", "flexWrap": "wrap"},
            children=[
                html.Label("Metric"),
                dcc.Dropdown(
                    id="metric-dropdown",
                    options=[{"label": m, "value": m} for m in METRICS],
                    value="RAW",
                    clearable=False,
                    style={"width": "140px"},
                ),

                html.Label("Compare Serials"),
                dcc.Dropdown(
                    id="compare-serials",
                    multi=True,
                    placeholder="Compare serials",
                    style={"minWidth": "420px"},
                ),

                html.Label("Top Plot Samples"),
                dcc.Input(id="top-n", type="number", value=100),
            ],
        ),

        html.Div(id="run-label", style={"fontStyle": "italic", "marginTop": "6px"}),
        html.Div(
            id="compare-warning",
            style={"color": "#b94a48", "fontStyle": "italic", "marginTop": "4px"},
        ),

        dcc.Graph(id="plot", style={"height": "850px"}),

        html.Hr(),

        dash_table.DataTable(
            id="stats-table",
            columns=[
                {"name": "SerialNumber", "id": "SerialNumber"},
                {"name": "Channel", "id": "Channel"},
                {"name": "Metric", "id": "Metric"},
                {"name": "Mean", "id": "Mean"},
                {"name": "StdDev", "id": "StdDev"},
                {"name": "N", "id": "N"},
            ],
            style_cell={"fontSize": "11px", "padding": "6px"},
        ),
    ],
)

# ======================================================
# Load CSV
# ======================================================
@app.callback(
    Output("data-store", "data"),
    Output("compare-serials", "options"),
    Input("upload-csv", "contents"),
    prevent_initial_call=True,
)
def load_csv(contents):
    df = parse_uploaded_csv(contents)
    df = ensure_columns(df)
    df = add_run_index(df)
    df.to_csv(DATA_CSV, index=False)

    serials = sorted(df["SerialID"].unique())
    return df.to_json(orient="split"), [{"label": s, "value": s} for s in serials]


# ======================================================
# Plot (mean / std overlays, NO ghosting)
# ======================================================
@app.callback(
    Output("plot", "figure"),
    Output("run-label", "children"),
    Output("compare-warning", "children"),
    Input("data-store", "data"),
    Input("metric-dropdown", "value"),
    Input("compare-serials", "value"),
    Input("top-n", "value"),
)
def update_plot(data, metric, compare_serials, top_n):
    if not data:
        return px.line(), "", ""

    df = pd.read_json(data, orient="split")
    df = keep_latest_run_only(df)

    all_serials = sorted(df["SerialID"].unique())
    warning = ""

    if compare_serials:
        valid = [s for s in compare_serials if s in all_serials]
        missing = [s for s in compare_serials if s not in all_serials]

        if not valid:
            return px.line(), "No valid serials selected", f"⚠️ No data for: {', '.join(missing)}"

        serials = valid
        label = f"Comparing {len(serials)} serial(s)"
        if missing:
            warning = f"⚠️ No data for: {', '.join(missing)}"
    else:
        serials = all_serials
        label = "All serials (latest run)"

    df = df[df["SerialID"].isin(serials)]

    df_top = df[df["X"] <= top_n]
    df_bot = df[df["X"] > top_n]

    fig = make_subplots(
        rows=2,
        cols=1,
        vertical_spacing=0.12,
        subplot_titles=[f"{metric} 1–{top_n}", f"{metric} {top_n + 1}+"],
    )

    color_map = {s: COLOR_POOL[i % len(COLOR_POOL)] for i, s in enumerate(serials)}

    for row_df, row_idx in [(df_top, 1), (df_bot, 2)]:
        for s in serials:
            g = row_df[row_df["SerialID"] == s]
            if g.empty:
                continue

            col = color_map[s]

            # Main data
            fig.add_scatter(
                x=g["X"],
                y=g[metric],
                name=s,
                line=dict(color=col),
                showlegend=(row_idx == 1),
                row=row_idx,
                col=1,
            )

            # Mean / ±σ
            mean = g[metric].mean()
            std = g[metric].std(ddof=1)
            x0, x1 = g["X"].min(), g["X"].max()

            fig.add_scatter(
                x=[x0, x1],
                y=[mean, mean],
                mode="lines",
                name=f"{s} (mean)",
                line=dict(color=col, dash="dash", width=2),
                showlegend=(row_idx == 1),
                row=row_idx,
                col=1,
            )

            if pd.notna(std):
                fig.add_scatter(
                    x=[x0, x1],
                    y=[mean + std, mean + std],
                    mode="lines",
                    line=dict(color=col, dash="dot"),
                    showlegend=False,
                    row=row_idx,
                    col=1,
                )
                fig.add_scatter(
                    x=[x0, x1],
                    y=[mean - std, mean - std],
                    mode="lines",
                    line=dict(color=col, dash="dot"),
                    showlegend=False,
                    row=row_idx,
                    col=1,
                )

    fig.update_layout(
        height=850,
        legend=dict(orientation="h", y=-0.25),
    )

    return fig, label, warning


# ======================================================
# Main
# ======================================================
if __name__ == "__main__":
    print(f"Running {APP_TITLE} → http://127.0.0.1:8050")
    app.run(debug=False)
