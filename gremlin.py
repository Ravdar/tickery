import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State, MATCH, ALLSMALLER, ALL
from dash.exceptions import PreventUpdate
from dash import dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import datetime
from datetime import date, timedelta
import yfinance as yf
import yahooquery
from yahooquery import Ticker
from find_image import find_logo
import radar_ratings
from radar_ratings import (
    value_rating,
    debt_rating,
    stability_rating,
    dividend_rating,
    future_rating,
)


intervals = ["1d", "1m", "1mo", "1wk", "3mo", "5m", "15m", "30m", "60m", "90m"]
indicators = ["Moving average", "Bollinger Bands", "MACD", "Stochastic"]
ticker = pd.DataFrame(columns=["Datetime", "Open", "High", "Low", "Close", "Adj Close"])
today_date = pd.Timestamp.now()
week_ago = pd.to_datetime(datetime.datetime.now() - timedelta(weeks=1))
colors = {"background": "#111111", "text": "#7FDBFF"}

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, "assets/styles.css"])


def add_indicator_button(
    indicator_short,
    indicator_name,
    param_2_name,
    param_1_name,
    param_1_value,
    param_2_value,
    s2_display,
    button_visible,
):

    return html.Div(
        children=[
            dbc.Button(
                f"{indicator_name}({param_1_value, param_2_value}",
                id=f"{indicator_short}_button",
                color="primary",
                className="me-1",
                style={"display": button_visible,},
            ),
            dbc.Button(
                "X",
                id=f"{indicator_short}_x_button",
                color="primary",
                className="me-1",
                style={"display": button_visible,},
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle(indicator_name)),
                    dbc.ModalBody(
                        [
                            dbc.Label(f"{param_1_name}:"),
                            dbc.Input(
                                id=f"{indicator_short}_param1",
                                type="number",
                                disabled=False,
                            ),
                            dbc.Label(
                                f"{param_2_name}:", style={"display": s2_display}
                            ),
                            dbc.Input(
                                id=f"{indicator_short}_param2",
                                type="number",
                                disabled=False,
                                style={"display": s2_display},
                            ),
                        ]
                    ),
                    dbc.ModalFooter(
                        [dbc.Button("OK", color="primary", id=f"{indicator_short}_ok"),]
                    ),
                ],
                id=f"{indicator_short}_modal",
            ),
        ],
        style={
            "display": "flex",
            "justify-content": "flex-start",
            "margin-top": "10px",
            "background-color": "#211F32",
            "align-items": "center",
            "gap": "0px",
            "margin-bottom": "0px",
        },
    )


# Layout part
app.layout = html.Div(
    id="dynamic-container",
    children=[
        html.Div(
            style={
                "display": "flex",
                "justify-content": "space-between",
                "align-items": "center",
            },
            children=[
                html.H1(
                    "GremlinGains",
                    style={
                        "text-align": "center",
                        "color": "white",
                        "margin": "30px auto 0",
                    },
                ),
            ],
        ),
        html.P("Hunt your profits", style={"text-align": "center", "color": "white"},),
        html.Div(
            dcc.Input(
                id="input_ticker".format("search"),
                type="search",
                placeholder="Search ticker".format("search"),
                style={
                    "width": "350px",
                    "height": "45px",
                    "background-color": "white",
                    "color": "#211F32",
                    "margin-bottom": "15px",
                    "text-align": "center",
                    "borderRadius": "30px",
                },
            ),
            style={"display": "flex", "justify-content": "center",},
        ),
        html.Div(id="short_info_container", children=[],),
        html.Div(
            id="tabs_container",
            style={"display": "flex", "justify-content": "center",},
            children=[
                dcc.Tabs(
                    id="main_tabs",
                    value="summary_tab",
                    children=[
                        dcc.Tab(
                            label="Summary",
                            value="summary_tab",
                            selected_className="main-selected-tab",
                        ),
                        dcc.Tab(
                            label="Chart",
                            value="main_chart_tab",
                            selected_className="main-selected-tab",
                        ),
                        dcc.Tab(
                            label="Financials",
                            value="financials_tab",
                            selected_className="main-selected-tab",
                        ),
                        dcc.Tab(
                            label="Statistics",
                            value="statistics_tab",
                            selected_className="main-selected-tab",
                        ),
                    ],
                    style={"display": "none", "width": "700px",},
                )
            ],
        ),
        html.H5(
            "Nothing is here yet, type stock ticker to start",
            style={
                "color": "white",
                "margin-top": "150px",
                "display": "flex",
                "justify-content": "center",
                "font-size": "60px",
                "text-align": "center",
            },
            id="welcome_message",
        ),
        html.Div(id="tabs_content"),
    ],
    style={"backgroundColor": "#211F32", "height": "100vh", "margin": "0"},
)


def add_moving_average(
    ma_length, ticker, fig_data, ticker_value, interval_value, start_date, end_date
):
    ticker2 = yf.download(
        tickers=ticker_value,
        interval=interval_value,
        start=(
            datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            - timedelta(days=(ma_length + 10))
        ),
        end=end_date,
        prepost=False,
        threads=True,
    )
    if ticker2.empty:
        ticker["Moving Average"] = ticker["Close"].rolling(window=ma_length).mean()
    else:
        ticker2["Moving Average"] = ticker2["Close"].rolling(window=ma_length).mean()
        row_diff = len(ticker2) - len(ticker)
        ticker2 = ticker2[row_diff:]
        ticker = ticker2
        ticker = ticker.reset_index()
    fig_data.append(
        go.Scatter(
            x=ticker.index,
            y=ticker["Moving Average"],
            mode="lines",
            name="Moving Average",
        )
    )


def add_bollinger_bands(
    bb_length,
    std_dev,
    ticker,
    fig_data,
    ticker_value,
    interval_value,
    start_date,
    end_date,
):
    ticker2 = yf.download(
        tickers=ticker_value,
        interval=interval_value,
        start=(
            datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            - timedelta(days=(bb_length + 10))
        ),
        end=end_date,
        prepost=False,
        threads=True,
    )
    if ticker2.empty:
        ticker["TP"] = (ticker["Close"] + ticker["Low"] + ticker["High"]) / 3
        ticker["STD"] = ticker["TP"].rolling(window=bb_length).std(ddof=0)
        ticker["MA-TP"] = ticker["TP"].rolling(window=bb_length).mean()
        ticker["BB Up"] = ticker["MA-TP"] + std_dev * ticker["STD"]
        ticker["BB Down"] = ticker["MA-TP"] - std_dev * ticker["STD"]
    else:
        ticker2["TP"] = (ticker2["Close"] + ticker2["Low"] + ticker2["High"]) / 3
        ticker2["STD"] = ticker2["TP"].rolling(window=bb_length).std(ddof=0)
        ticker2["MA-TP"] = ticker2["TP"].rolling(window=bb_length).mean()
        ticker2["BB Up"] = ticker2["MA-TP"] + std_dev * ticker2["STD"]
        ticker2["BB Down"] = ticker2["MA-TP"] - std_dev * ticker2["STD"]
        row_diff = len(ticker2) - len(ticker)
        ticker2 = ticker2[row_diff:]
        ticker = ticker2
        ticker = ticker.reset_index()
    fig_data.append(
        go.Scatter(x=ticker.index, y=ticker["BB Up"], mode="lines", name="BB Up")
    )

    fig_data.append(
        go.Scatter(x=ticker.index, y=ticker["MA-TP"], mode="lines", name="MA-TP",)
    )

    fig_data.append(
        go.Scatter(x=ticker.index, y=ticker["BB Down"], mode="lines", name="BB Down",)
    )


def add_stochastic(
    st_length,
    slowing,
    ticker,
    ticker_value,
    interval_value,
    start_date,
    end_date,
    xaxis,
):

    ticker2 = yf.download(
        tickers=ticker_value,
        interval=interval_value,
        start=(
            datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            - timedelta(days=(st_length + 10))
        ),
        end=end_date,
        prepost=False,
        threads=True,
    )

    if ticker2.empty:
        length_high = ticker["High"].rolling(st_length).max()
        length_low = ticker["Low"].rolling(st_length).min()
        ticker["%K"] = (ticker["Close"] - length_low) * 100 / (length_high - length_low)
        ticker["%D"] = ticker["%K"].rolling(slowing).mean()
    else:
        length_high = ticker2["High"].rolling(st_length).max()
        length_low = ticker2["Low"].rolling(st_length).min()
        ticker2["%K"] = (
            (ticker2["Close"] - length_low) * 100 / (length_high - length_low)
        )
        ticker2["%D"] = ticker2["%K"].rolling(slowing).mean()
        row_diff = len(ticker2) - len(ticker)
        ticker2 = ticker2[row_diff:]
        ticker = ticker2
    ticker = ticker.reset_index()

    fig2 = (
        dcc.Graph(
            id="stochastic_chart",
            figure=go.Figure(
                data=[
                    go.Scatter(x=ticker.iloc[:, 0], y=ticker["%K"], name="%K"),
                    go.Scatter(x=ticker.iloc[:, 0], y=ticker["%D"], name="%D"),
                ],
                layout=go.Layout(
                    showlegend=False,
                    yaxis=dict(
                        autorange=True,
                        titlefont=dict(color="grey"),
                        tickfont=dict(color="grey"),
                    ),
                    xaxis_rangeslider_visible=False,
                    xaxis=dict(
                        showticklabels=xaxis,
                        autorange=True,
                        titlefont=dict(color="grey"),
                        tickfont=dict(color="grey"),
                    ),
                    margin=go.layout.Margin(
                        l=40,  # left margin
                        r=40,  # right margin
                        b=5,  # bottom margin
                        t=0,  # top margin
                    ),
                    paper_bgcolor="#211F32",
                    plot_bgcolor="#211F32",
                ),
            ),
            style={
                "margin-top": "0px",
                "height": "175px",
                "padding-top": "0px",
                "width": "100%",
            },
        ),
    )

    return fig2


def add_macd(
    fast_ema,
    slow_ema,
    ticker,
    ticker_value,
    interval_value,
    start_date,
    end_date,
    xaxis,
):

    ticker2 = yf.download(
        tickers=ticker_value,
        interval=interval_value,
        start=(
            datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            - timedelta(days=(slow_ema + 10))
        ),
        end=end_date,
        prepost=False,
        threads=True,
    )

    if ticker2.empty:
        ticker["Fast EMA"] = ticker["Close"].ewm(span=fast_ema, adjust=False).mean()
        ticker["Slow EMA"] = ticker["Close"].ewm(span=slow_ema, adjust=False).mean()
        ticker["MACD"] = ticker["Fast EMA"] - ticker["Slow EMA"]
    else:
        ticker2["Fast EMA"] = ticker2["Close"].ewm(span=fast_ema, adjust=False).mean()
        ticker2["Slow EMA"] = ticker2["Close"].ewm(span=slow_ema, adjust=False).mean()
        ticker2["MACD"] = ticker2["Fast EMA"] - ticker2["Slow EMA"]
        row_diff = len(ticker2) - len(ticker)
        ticker2 = ticker2[row_diff:]
        ticker = ticker2
    ticker = ticker.reset_index()
    macd_positive = ticker.loc[ticker["MACD"] >= 0]
    macd_negative = ticker.loc[ticker["MACD"] < 0]

    fig3 = dcc.Graph(
        id="macd_chart",
        figure=go.Figure(
            data=[
                # Use different colors for positive and negative values
                go.Bar(
                    x=macd_positive.iloc[:, 0],
                    y=macd_positive["MACD"],
                    name="MACD",
                    yaxis="y1",
                    marker=dict(color="blue"),
                ),
                go.Bar(
                    x=macd_negative.iloc[:, 0],
                    y=macd_negative["MACD"],
                    name="MACD",
                    yaxis="y1",
                    marker=dict(color="Aqua"),
                ),
                go.Scatter(
                    x=ticker.iloc[:, 0],
                    y=ticker["Fast EMA"],
                    name="Fast EMA",
                    yaxis="y2",
                ),
                go.Scatter(
                    x=ticker.iloc[:, 0],
                    y=ticker["Slow EMA"],
                    name="Slow EMA",
                    yaxis="y2",
                ),
            ],
            layout=go.Layout(
                yaxis1=dict(
                    autorange=True,
                    titlefont=dict(color="gray"),
                    tickfont=dict(color="gray"),
                ),
                yaxis2=dict(
                    titlefont=dict(color="gray"),
                    tickfont=dict(color="gray"),
                    anchor="free",
                    overlaying="y",
                    side="right",
                    position=1,
                ),
                showlegend=False,
                xaxis_rangeslider_visible=False,
                xaxis={"showticklabels": xaxis},
                margin=go.layout.Margin(
                    l=40,  # left margin
                    r=40,  # right margin
                    b=5,  # bottom margin
                    t=0,  # top margin
                ),
                paper_bgcolor="#211F32",
                plot_bgcolor="#211F32",
            ),
        ),
        style={
            "margin-top": "0px",
            "height": "175px",
            "padding-top": "0px",
            "width": "100%",
        },
    )

    return fig3


@app.callback(
    [
        Output("ma_modal", "is_open", allow_duplicate=True),
        Output("bb_modal", "is_open", allow_duplicate=True),
        Output("st_modal", "is_open", allow_duplicate=True),
        Output("macd_modal", "is_open", allow_duplicate=True),
    ],
    Input("indicator_dropdown", "value"),
    prevent_initial_call=True,
)
def show_indicator_modal(indicator_value):

    if indicator_value == "Moving average":
        return True, False, False, False
    elif indicator_value == "Bollinger Bands":
        return False, True, False, False
    elif indicator_value == "Stochastic":
        return False, False, True, False
    elif indicator_value == "MACD":
        return False, False, False, True
    else:
        return False, False, False, False


@app.callback(
    [
        Output("indicator_dropdown", "value", allow_duplicate=True),
        Output("ma_button", "style", allow_duplicate=True),
        Output("ma_x_button", "style", allow_duplicate=True),
    ],
    Input("ma_ok", "n_clicks"),
    prevent_initial_call=True,
)
def draw_ma(n_clicks):
    if n_clicks != None:
        n_clicks = None
        return (
            None,
            {
                "display": "flex",
                "margin-right": "0px",
                "padding": "5px",
                "background-color": "#211F32",
                "font-size": "12px",
            },
            {
                "display": "flex",
                "margin-left": "0px",
                "padding": "5px",
                "background-color": "#211F32",
                "font-size": "12px",
            },
        )


@app.callback(
    [
        Output("indicator_dropdown", "value", allow_duplicate=True),
        Output("bb_button", "style", allow_duplicate=True),
        Output("bb_x_button", "style", allow_duplicate=True),
    ],
    Input("bb_ok", "n_clicks"),
    prevent_initial_call=True,
)
def draw_bb(n_clicks):
    if n_clicks != None:
        n_clicks = None
        return (
            None,
            {
                "display": "flex",
                "margin-right": "0px",
                "padding": "5px",
                "background-color": "#211F32",
                "font-size": "12px",
            },
            {
                "display": "flex",
                "margin-left": "0px",
                "padding": "5px",
                "background-color": "#211F32",
                "font-size": "12px",
            },
        )


@app.callback(
    [
        Output("indicator_dropdown", "value", allow_duplicate=True),
        Output("st_button", "style", allow_duplicate=True),
        Output("st_x_button", "style", allow_duplicate=True),
    ],
    Input("st_ok", "n_clicks"),
    prevent_initial_call=True,
)
def draw_st(n_clicks):
    if n_clicks != None:
        return (
            None,
            {
                "display": "flex",
                "margin-right": "0px",
                "padding": "5px",
                "background-color": "#211F32",
                "font-size": "12px",
            },
            {
                "display": "flex",
                "margin-left": "0px",
                "padding": "5px",
                "background-color": "#211F32",
                "font-size": "12px",
            },
        )


@app.callback(
    [
        Output("indicator_dropdown", "value", allow_duplicate=True),
        Output("macd_button", "style", allow_duplicate=True),
        Output("macd_x_button", "style", allow_duplicate=True),
    ],
    Input("macd_ok", "n_clicks"),
    prevent_initial_call=True,
)
def draw_macd(n_clicks):
    if n_clicks != None:
        return (
            None,
            {
                "display": "flex",
                "margin-right": "0px",
                "padding": "5px",
                "background-color": "#211F32",
                "font-size": "12px",
            },
            {
                "display": "flex",
                "margin-left": "0px",
                "padding": "5px",
                "background-color": "#211F32",
                "font-size": "12px",
            },
        )


# BUTTON PART
# Moving Average
# Clicking button
@app.callback(Output("ma_modal", "is_open"), Input("ma_button", "n_clicks"))
def show_ma_modal(n_clicks):
    if n_clicks != None:
        n_clicks = None
        return True
    else:
        return False


# Confirming settings
@app.callback(
    [Output("ma_button", "n_clicks"), Output("ma_button", "children")],
    Input("ma_ok", "n_clicks"),
    [State("ma_param1", "value"), State("ma_button", "children")],
)
def update_indicator(n_clicks, indicator_param1, indicator_name):
    if n_clicks != None:
        button_value = f"{indicator_name[:14]}({indicator_param1})"
        n_clicks = None
        return None, button_value


# Deleting button
@app.callback(
    [
        Output("ma_button", "style"),
        Output("ma_x_button", "style"),
        Output("ma_ok", "n_clicks", allow_duplicate=True),
    ],
    Input("ma_x_button", "n_clicks"),
    prevent_initial_call=True,
)
def delete_ma_buttons(n_clicks):
    if n_clicks != None:
        return {"display": "none"}, {"display": "none"}, None


# Bollinger Bands
# Clicking button
@app.callback(Output("bb_modal", "is_open"), Input("bb_button", "n_clicks"))
def show_bb_modal(n_clicks):
    if n_clicks != None:
        n_clicks = None
        return True
    else:
        return False


# Confirming settings
@app.callback(
    [Output("bb_button", "n_clicks"), Output("bb_button", "children")],
    Input("bb_ok", "n_clicks"),
    [
        State("bb_param1", "value"),
        State("bb_param2", "value"),
        State("bb_button", "children"),
    ],
)
def update_indicator(n_clicks, indicator_param1, indicator_param2, indicator_name):
    if n_clicks != None:
        button_value = f"{indicator_name[:15]}({indicator_param1}, {indicator_param2})"
        n_clicks = None
        return None, button_value


# Deleting button
@app.callback(
    [
        Output("bb_button", "style"),
        Output("bb_x_button", "style"),
        Output("bb_ok", "n_clicks", allow_duplicate=True),
    ],
    Input("bb_x_button", "n_clicks"),
    prevent_initial_call=True,
)
def delete_bb_buttons(n_clicks):
    if n_clicks != None:
        return {"display": "none"}, {"display": "none"}, None


# Stochistic
# Clicking button
@app.callback(Output("st_modal", "is_open"), Input("st_button", "n_clicks"))
def show_st_modal(n_clicks):
    if n_clicks != None:
        n_clicks = None
        return True
    else:
        return False


# Confirming settings
@app.callback(
    [Output("st_button", "n_clicks"), Output("st_button", "children"),],
    Input("st_ok", "n_clicks"),
    [
        State("st_param1", "value"),
        State("st_param2", "value"),
        State("st_button", "children"),
    ],
)
def update_indicator(n_clicks, indicator_param1, indicator_param2, indicator_name):
    if n_clicks != None:
        button_value = f"{indicator_name[:10]}({indicator_param1}, {indicator_param2})"
        n_clicks = None
        return None, button_value


# Deleting button
@app.callback(
    [
        Output("st_button", "style"),
        Output("st_x_button", "style"),
        Output("stoch_container", "children", allow_duplicate=True),
        Output("st_ok", "n_clicks", allow_duplicate=True),
    ],
    Input("st_x_button", "n_clicks"),
    prevent_initial_call=True,
)
def delete_st(n_clicks):
    if n_clicks != None:
        n_clicks = None
        return {"display": "none"}, {"display": "none"}, [], None


# MACD
# Clicking button
@app.callback(Output("macd_modal", "is_open"), Input("macd_button", "n_clicks"))
def show_macd_modal(n_clicks):
    if n_clicks != None:
        n_clicks = None
        return True
    else:
        return False


# Confirming settings
@app.callback(
    [Output("macd_button", "n_clicks"), Output("macd_button", "children"),],
    Input("macd_ok", "n_clicks"),
    [
        State("macd_param1", "value"),
        State("macd_param2", "value"),
        State("macd_button", "children"),
    ],
)
def update_indicator(n_clicks, indicator_param1, indicator_param2, indicator_name):
    if n_clicks != None:
        button_value = f"{indicator_name[:4]}({indicator_param1}, {indicator_param2})"
        n_clicks = None
        return None, button_value


# Deleting button
@app.callback(
    [
        Output("macd_button", "style"),
        Output("macd_x_button", "style"),
        Output("macd_container", "children", allow_duplicate=True),
        Output("macd_ok", "n_clicks", allow_duplicate=True),
    ],
    Input("macd_x_button", "n_clicks"),
    prevent_initial_call=True,
)
def delete_macd(n_clicks):
    if n_clicks != None:
        n_clicks = None
        return {"display": "none"}, {"display": "none"}, [], None


# TABS
@app.callback(Output("tabs_content", "children"), Input("main_tabs", "value"))
def render_tab(tab):
    if tab == "summary_tab":
        return html.Div(
            id="summary_container",
            children=[],
            style={"margin-left": "300px", "margin-right": "300px",},
        )
    elif tab == "main_chart_tab":
        return html.Div(
            id="tab_1_container",
            children=[
                html.Div(
                    children=[
                        dcc.Dropdown(
                            options=[{"label": i, "value": i} for i in intervals],
                            id="interval_dropdown",
                            placeholder="Interval",
                            style={
                                "width": "230px",
                                "background-color": "#211F32",
                                "width": "140px",
                            },
                            className="dropdown-custom",
                        ),
                        dcc.Dropdown(
                            options=[{"label": i, "value": i} for i in indicators],
                            id="indicator_dropdown",
                            placeholder="Indicators",
                            style={
                                "width": "230px",
                                "background-color": "#211F32",
                                "width": "140px",
                            },
                            className="dropdown-custom",
                        ),
                        dcc.DatePickerRange(
                            id="date_picker",
                            min_date_allowed=date(1900, 1, 1,),
                            max_date_allowed=date(
                                today_date.year, today_date.month, today_date.day
                            ),
                            initial_visible_month=date(
                                week_ago.year, week_ago.month, week_ago.day
                            ),
                            end_date=date(
                                today_date.year, today_date.month, today_date.day
                            ),
                            style={"background-color": "#211F32", "padding": "0px"},
                        ),
                        dcc.Dropdown(
                            options=[
                                {"label": "Linear", "value": "linear"},
                                {"label": "Logarithmic", "value": "log"},
                            ],
                            id="scale_dropdown",
                            placeholder="Scale",
                            value="linear",
                            style={
                                "width": "230px",
                                "background-color": "#211F32",
                                "width": "140px",
                            },
                            className="dropdown-custom",
                        ),
                        dcc.Dropdown(
                            options=[
                                {"label": "Candlesticks", "value": "candlesticks"},
                                {"label": "Bars", "value": "bars"},
                                {"label": "Linear", "value": "linear"},
                            ],
                            id="type_dropdown",
                            placeholder="Type",
                            value="candlesticks",
                            style={
                                "width": "230px",
                                "background-color": "#211F32",
                                "width": "140px",
                            },
                            className="dropdown-custom",
                        ),
                    ],
                    style={
                        "display": "flex",
                        "justify-content": "center",
                        "margin-top": "10px",
                        "background-color": "#211F32",
                    },
                ),
                html.Div(
                    dbc.Alert(
                        "Invalid data range. Please be aware that for shorter intervals, only the data from the past 7 days is available.",
                        id="error_alert",
                        color="danger",
                        dismissable=True,
                        is_open=False,
                        duration=5500,
                    ),
                    style={"display": "flex", "justify-content": "center"},
                ),
                html.Div(
                    id="modals",
                    children=[
                        add_indicator_button(
                            "ma", "Moving average", "Length", "", 0, 0, "none", "none"
                        ),
                        add_indicator_button(
                            "bb",
                            "Bollinger Bands",
                            "Period",
                            "Standard deviation",
                            0,
                            0,
                            "display",
                            "none",
                        ),
                        add_indicator_button(
                            "st",
                            "Stochastic",
                            "%K period",
                            "Slowing",
                            0,
                            0,
                            "display",
                            "none",
                        ),
                        add_indicator_button(
                            "macd",
                            "MACD",
                            "Fast EMA",
                            "Slow EMA",
                            0,
                            0,
                            "display",
                            "none",
                        ),
                    ],
                    style={
                        "display": "flex",
                        "justify-content": "center",
                        "margin-top": "10px",
                        "background-color": "#211F32",
                    },
                ),
                html.Div(
                    id="stats_container",
                    children=[],
                    style={
                        "display": "flex",
                        "justify-content": "center",
                        "margin-top": "10px",
                    },
                ),
                dcc.Graph(
                    id="ticker_cndl_chart",
                    figure=go.Figure(
                        data=[
                            go.Candlestick(
                                x=ticker.iloc[:, 0],
                                open=ticker["Open"],
                                high=ticker["High"],
                                low=ticker["Low"],
                                close=ticker["Close"],
                            )
                        ],
                        layout=go.Layout(
                            titlefont=dict(color="grey"),
                            showlegend=False,
                            yaxis=dict(
                                type="linear",
                                autorange=True,
                                titlefont=dict(color="grey"),
                                tickfont=dict(color="grey"),
                                gridcolor="grey",
                            ),
                            xaxis_rangeslider_visible=False,
                            xaxis=dict(
                                autorange=True,
                                titlefont=dict(color="grey"),
                                tickfont=dict(color="grey"),
                                gridcolor="grey",
                            ),
                            margin=go.layout.Margin(
                                l=40,  # left margin
                                r=40,  # right margin
                                b=5,  # bottom margin
                                t=5,  # top margin
                            ),
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="#211F32",
                        ),
                    ),
                    style={
                        "margin_bottom": "0px",
                        "padding-bottom": "0px",
                        "margin_top": "0px",
                        "padding-top": "0px",
                        "height": "550px",
                        "width": "100%",
                        "overflow": "hidden",
                        "background-color": "#211F32",
                    },
                    className="h-5",
                ),
                html.Div(id="stoch_container", children=[],),
                html.Div(id="macd_container", children=[],),
            ],
        )
    elif tab == "financials_tab":
        return html.Div(
            children=[
                html.Div(
                    children=[
                        dcc.Tabs(
                            id="financials_tab",
                            value="income_stmt_tab",
                            children=[
                                dcc.Tab(
                                    label="Income statement",
                                    value="income_stmt_tab",
                                    className="custom-tabs",
                                    selected_className="selected-tab",
                                    style={"padding-top": "4px",},
                                    selected_style={"padding-top": "4px"},
                                ),
                                dcc.Tab(
                                    label="Balance sheet",
                                    value="balance_sheet_tab",
                                    className="custom-tabs",
                                    selected_className="selected-tab",
                                ),
                                dcc.Tab(
                                    label="Cash flow",
                                    value="cash_flow_tab",
                                    className="custom-tabs",
                                    selected_className="selected-tab",
                                ),
                            ],
                            style={
                                "width": "400px",
                                "display": "flex",
                                "font-size": "12px",
                                "margin-right": "60px",
                                "borders": "none",
                            },
                        ),
                        dcc.Tabs(
                            id="qora_tabs",
                            value="annual_tab",
                            children=[
                                dcc.Tab(
                                    label="Annual",
                                    value="annual_tab",
                                    className="custom-tabs",
                                    selected_className="selected-tab",
                                    style={"padding-left": "20px",},
                                    selected_style={"padding-left": "20px"},
                                ),
                                dcc.Tab(
                                    label="Quarterly",
                                    value="quarterly_tab",
                                    className="custom-tabs",
                                    selected_className="selected-tab",
                                    style={"padding-left": "15px",},
                                    selected_style={"padding-left": "15px"},
                                ),
                            ],
                            style={
                                "width": "150px",
                                "display": "flex",
                                "font-size": "10px",
                                "borders": "none",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "justify-content": "center",
                        "margin-top": "10px",
                        "margin-bottom": "5px",
                    },
                ),
                html.Div(
                    id="financials_container",
                    children=[],
                    style={"backgroundColor": "#211F32"},
                ),
            ]
        )
    elif tab == "statistics_tab":
        return html.Div(
            id="statistics_container",
            children=[],
            style={"backgroundColor": "#211F32"},
        )


# UPDATING CHART
@app.callback(
    [
        Output("ticker_cndl_chart", "figure"),
        Output("error_alert", "is_open"),
        Output("stoch_container", "children", allow_duplicate=True),
        Output("macd_container", "children", allow_duplicate=True),
        Output("stats_container", "children"),
    ],
    [
        Input("input_ticker", "value"),
        Input("interval_dropdown", "value"),
        Input("date_picker", "start_date"),
        Input("date_picker", "end_date"),
        Input("ma_ok", "n_clicks"),
        Input("bb_ok", "n_clicks"),
        Input("st_ok", "n_clicks"),
        Input("macd_ok", "n_clicks"),
        Input("scale_dropdown", "value"),
        Input("type_dropdown", "value"),
    ],
    State("ma_param1", "value"),
    State("bb_param2", "value"),
    State("bb_param1", "value"),
    State("st_param1", "value"),
    State("st_param2", "value"),
    State("macd_param1", "value"),
    State("macd_param2", "value"),
    State("ticker_cndl_chart", "figure"),
    prevent_initial_call=True,
)
def update_chart(
    ticker_value,
    interval_value,
    start_date,
    end_date,
    ma_ok,
    bb_ok,
    st_ok,
    macd_ok,
    scale,
    type,
    ma_length,
    bb_length,
    bb_std,
    st_length,
    st_slowing,
    fast_ema,
    slow_ema,
    init_figure,
):
    stoch = []
    macd = []

    if ticker_value is None or interval_value is None or start_date is None:
        return init_figure, False, stoch, macd, None

    ticker = yf.download(
        tickers=ticker_value,
        interval=interval_value,
        start=start_date,
        end=end_date,
        prepost=False,
        threads=True,
    )
    print(f"Ticker = {ticker}")
    if ticker.empty:
        print("Fullfilled")
        return init_figure, True, stoch, macd, None

    ticker = ticker.reset_index()

    # STATS

    ticker["Perc change"] = (ticker["Open"] - ticker["Close"]) / ticker["Open"] * 100
    ticker["Perc range"] = (ticker["High"] - ticker["Low"]) / ticker["High"] * 100
    ticker["Gap"] = (ticker["Open"] - ticker["Close"].shift(1)) / ticker["Open"] * 100
    ticker["Gap"] = ticker["Gap"].fillna(0)

    min = round(ticker["Low"].min(), 2)
    avg = f"{start_date} & {end_date}"
    max = round(ticker["High"].max(), 2)
    perc_change = round(
        (
            100
            * (
                (int(ticker.iloc[-1, 4]) - int(ticker.iloc[0, 1]))
                / int(ticker.iloc[0, 1])
            )
        ),
        2,
    )

    price_range = round((max - min), 2)
    perc_range = round((price_range / max * 100), 2)
    # Gap
    avg_gap = round(ticker["Gap"].mean(), 2)
    min_gap = round(ticker["Gap"].min(), 2)
    max_gap = round(ticker["Gap"].max(), 2)
    # Single candles
    avg_perc_change = round(ticker["Perc change"].mean(), 2)
    min_perc_change = round(ticker["Perc change"].min(), 2)
    max_perc_change = round(ticker["Perc change"].max(), 2)
    avg_perc_range = round(ticker["Perc range"].mean(), 2)
    min_perc_range = round(ticker["Perc range"].min(), 2)
    max_perc_range = round(ticker["Perc range"].max(), 2)

    stats = [
        html.H5(f"Percentage change: {perc_change}%", className="stats_styling"),
        html.H5(f"Price range: {price_range}", className="stats_styling"),
        html.H5(f"Percentage range: {perc_range}%", className="stats_styling"),
        html.H5(f"Min: {min}", className="stats_styling"),
        html.H5(f"Avg: {avg}", className="stats_styling"),
        html.H5(f"Max: {max}", className="stats_styling"),
    ]

    length_df = len(ticker.index)
    if length_df < 25:
        tick_indices = [i for i in range(0, length_df, 1)]
    else:
        tick_indices = [i for i in range(0, length_df, length_df // 10)]
    tick_values = ticker.index[tick_indices]

    # Convert x-axis labels based on interval (date type)
    if ticker.columns[0] == "Datetime":
        ticktext = [str(val)[:19] for val in ticker.iloc[tick_indices, 0]]
        # Drop last row beacuse it is called incorrectly for some reason
        if str(ticker.iloc[-1, 0])[:19] != str(ticker.iloc[-2, 0])[:19]:
            ticker = ticker[:-1]

    else:
        ticktext = [str(val)[:10] for val in ticker.iloc[tick_indices, 0]]

    if type == "candlesticks":
        fig_data = [
            go.Candlestick(
                x=ticker.index,
                open=ticker["Open"],
                high=ticker["High"],
                low=ticker["Low"],
                close=ticker["Close"],
            )
        ]
    elif type == "bars":
        fig_data = [
            go.Ohlc(
                x=ticker.index,
                open=ticker["Open"],
                high=ticker["High"],
                low=ticker["Low"],
                close=ticker["Close"],
            )
        ]
    else:
        fig_data = [go.Scatter(x=ticker.index, y=ticker["Close"],)]

    # Add moving average to the plot if selected
    if ma_ok != None:
        add_moving_average(
            ma_length,
            ticker,
            fig_data,
            ticker_value,
            interval_value,
            start_date,
            end_date,
        )
    # Add bollinger bands to the plot if selected
    if bb_ok != None:
        add_bollinger_bands(
            bb_length,
            bb_std,
            ticker,
            fig_data,
            ticker_value,
            interval_value,
            start_date,
            end_date,
        )
    # Add stochastic to the plot if selected
    if st_ok is not None:
        stoch = add_stochastic(
            st_length,
            st_slowing,
            ticker,
            ticker_value,
            interval_value,
            start_date,
            end_date,
            macd_ok is None,
        )
    else:
        stoch = []

    # Handle MACD if needed
    if macd_ok is not None:
        macd = add_macd(
            fast_ema,
            slow_ema,
            ticker,
            ticker_value,
            interval_value,
            start_date,
            end_date,
            True,
        )
    else:
        macd = []

    if st_ok != None or macd_ok != None:
        xaxis = {
            "showticklabels": False,
            "gridcolor": "grey",
            "tickfont": {"color": "white"},
        }
    else:
        xaxis = {
            "tickmode": "array",
            "tickvals": tick_values,
            "ticktext": ticktext,
            "gridcolor": "grey",
            "tickfont": {"color": "white"},
        }

    fig = go.Figure(
        data=fig_data,
        layout=go.Layout(
            showlegend=False,
            titlefont=dict(color="white"),
            yaxis=dict(
                type=scale,
                autorange=True,
                titlefont=dict(color="white"),
                tickfont=dict(color="white"),
                gridcolor="grey",
            ),
            xaxis_rangeslider_visible=False,
            xaxis=xaxis,
            margin=go.layout.Margin(
                l=40,  # left margin
                r=40,  # right margin
                b=5,  # bottom margin
                t=5,  # top margin
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        ),
    )

    return fig, False, stoch, macd, stats


@app.callback(
    Output("welcome_message", "children"),
    Output("welcome_message", "style"),
    Output("main_tabs", "style"),
    Output("short_info_container", "children"),
    Input("input_ticker", "value"),
)
def show_info(ticker_text):

    empty = "Nothing is here yet, type stock ticker to start"
    loading = "Loading..."
    not_found = "We couldn't find your ticker :( Correct it and try again"
    style = {
        "color": "white",
        "margin-top": "150px",
        "justify-content": "center",
        "display": "flex",
        "font-size": "60px",
        "text-align": "center",
    }

    if ticker_text:
        ticker = yf.Ticker(ticker_text)
        ticker_yq = Ticker(ticker_text, validate=True)
        validation = ticker_yq.symbols
    else:
        return empty, style, {"display": "none"}, None
    if validation == []:
        return not_found, style, {"display": "none"}, None

    name = ticker.info["shortName"]
    currency = ticker.info["currency"]
    logo_url = find_logo(ticker_text)
    industry = ticker.info["industry"]
    # country = ticker.info["country"]
    # flag = find_flag(country)
    exchange = ticker_yq.price[ticker_text]["exchangeName"]
    history = ticker.history(period="1m")
    last_price = round(history["Close"].iloc[-1], 2)
    prev_close = round(ticker.info["previousClose"], 2)
    change = round(last_price - prev_close, 2)
    if change >= 0:
        change = f"+{change}"
        perc_change = f"+{round(((last_price - prev_close) / prev_close * 100),2)}%"
        font_color = "#00b51a"
    else:
        change = f"{change}"
        perc_change = f"{round(((last_price - prev_close) / prev_close * 100),2)}%"
        font_color = "#ff2d21"

    return (
        "",
        {"display": "none"},
        {"display": "block", "width": "700px"},
        html.Div(
            children=[
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Img(
                                    src=f"{logo_url}",
                                    alt="image",
                                    style={
                                        "width": "160px",
                                        "height": "160px",
                                        "border-radius": "10px",
                                        "border": "2px solid white",
                                        "object-fit": "fill",
                                        "object-position": "center",
                                    },
                                )
                            ],
                            style={
                                "margin-left": "700px",
                                "margin-right": "0px",
                                "margin-top": "9px",
                            },
                        ),
                        dbc.Col(
                            [
                                html.Div(
                                    children=[
                                        html.H1(
                                            name,
                                            style={
                                                "text-align": "left",
                                                "color": "white",
                                                "margin-left": "0",
                                                "white-space": "nowrap",  # Prevent text wrapping
                                                "overflow": "hidden",  # Hide any overflowing text
                                                "text-overflow": "ellipsis",
                                            },
                                        ),
                                        # html.Img(
                                        #     src=f"{flag}",
                                        #     alt="image",
                                        #     style={
                                        #         "width": "60px",
                                        #         "height": "40px",
                                        #         "margin-left": "0",
                                        #     },
                                        # ),
                                    ],
                                ),
                                html.Div(
                                    children=[
                                        html.H1(
                                            [
                                                f"{last_price} {currency} ",
                                                html.Span(
                                                    f"{change} {perc_change}",
                                                    style={
                                                        "font-size": "20px",
                                                        "color": font_color,
                                                    },
                                                ),
                                            ],
                                            style={
                                                "text-align": "left",
                                                "color": "white",
                                                "margin-left": "0",
                                                "white-space": "nowrap",  # Prevent text wrapping
                                                "overflow": "hidden",  # Hide any overflowing text
                                                "text-overflow": "ellipsis",
                                            },
                                        ),
                                    ]
                                ),
                                html.H5(
                                    industry,
                                    style={
                                        "text-align": "left",
                                        "color": "white",
                                        "margin-left": "0",
                                    },
                                ),
                                html.H5(
                                    exchange,
                                    style={
                                        "text-align": "left",
                                        "color": "white",
                                        "margin-left": "0",
                                    },
                                ),
                            ],
                            style={},
                        ),
                    ],
                    align="start",  # Align columns to the top
                )
            ],
            style={"display": "flex", "margin-bottom": "15px"},
        ),
    )


@app.callback(
    Output("financials_container", "children"),
    [
        Input("input_ticker", "value"),
        Input("main_tabs", "value"),
        Input("financials_tab", "value"),
        Input("qora_tabs", "value"),
    ],
)
def update_financials(ticker_text, tab1, tab2, tab3):
    if tab1 == "financials_tab":
        ticker = Ticker(ticker_text)
        if tab3 == "annual_tab":
            frequency = "a"
        elif tab3 == "quarterly_tab":
            frequency = "q"
        if tab2 == "balance_sheet_tab":
            table_data = ticker.balance_sheet(frequency)
        elif tab2 == "income_stmt_tab":
            table_data = ticker.income_statement(frequency)
        elif tab2 == "cash_flow_tab":
            table_data = ticker.cash_flow(frequency)

        table_data = table_data.transpose()
        table_data.reset_index(inplace=True)
        table_data.columns = range(table_data.shape[1])

        print(table_data)
        table_data.drop(1, 0, inplace=True)
        table_data.drop(2, 0, inplace=True)

        for period in table_data.iloc[0]:
            print(period)
            if str(period)[0] == "2":
                if frequency == "a":
                    period = str(period)[:4]
                elif frequency == "q":
                    period == str(period)[:7]
                print(period)

        # columns = []  # Start with index column
        # for column in table_data.columns:
        #     columns.append({"name": column, "id": column})

        initial_active_cell = {"row": 11, "column": 0, "column_id": "0", "row_id": 11}

        table = dash_table.DataTable(
            id="financials_table",
            data=table_data.to_dict("records"),
            active_cell=initial_active_cell,
            style_table={
                "maxWidth": "700px",
                "marginLeft": "auto",
                "marginRight": "auto",
            },  # Center the table horizontally
            style_cell={
                "whiteSpace": "normal",
                "textAlign": "center",
                "color": "white",
                "backgroundColor": "#211F32",
                "fontFamily": "Lato",
            },
            style_header={"fontWeight": "bold"},
        )

        return html.Div(
            children=[html.Div(id="graph_container", children=[]), table],
            style={"text-align": "center", "backgroundColor": "#211F32"},
        )


@app.callback(
    Output("graph_container", "children"),
    Input("financials_table", "active_cell"),
    State("financials_table", "data"),
)
def cell_clicked(active_cell, table):

    if active_cell is None:
        return None

    row = active_cell["row"]
    value = table[row]["0"]
    x_data = [table[0]["1"], table[0]["2"], table[0]["3"], table[0]["4"]]
    y_data = [table[row]["1"], table[row]["2"], table[row]["3"], table[row]["4"]]

    figson = dcc.Graph(
        id="bar-chart",
        className="financial-charts",
        figure={
            "data": [
                {
                    "x": x_data,
                    "y": y_data,
                    "type": "bar",
                    "marker": {"color": "#3ad1b8"},
                }
            ],
            "layout": {
                "title": value,
                "titlefont": {"color": "white"},
                "xaxis": {"color": "white"},
                "yaxis": {"color": "white"},
                "plot_bgcolor": "#211F32",
                "paper_bgcolor": "#211F32",
            },
        },
    )

    return figson


@app.callback(
    Output("statistics_container", "children"),
    [Input("input_ticker", "value"), Input("main_tabs", "value"),],
)
def update_statistics(ticker_text, tab):
    if tab == "statistics_tab":
        ticker = Ticker(ticker_text)

        table_data = ticker.calendar_events
        table_data.reset_index(inplace=True)
        # table_data = table_data.drop(table_data.columns[2], axis=1)

        table = dash_table.DataTable(
            id="statistics_table",
            data=table_data.to_dict("records"),
            style_table={
                "maxWidth": "700px",
                "marginLeft": "auto",
                "marginRight": "auto",
            },  # Center the table horizontally
            style_cell={
                "whiteSpace": "normal",
                "textAlign": "center",
                "color": "white",
                "backgroundColor": "#211F32",
            },
            style_header={"fontWeight": "bold"},
        )

        return table


@app.callback(
    Output("summary_container", "children", allow_duplicate=True),
    [Input("input_ticker", "value"), Input("main_tabs", "value"),],
    prevent_initial_call=True,
)
def update_summary(ticker_text, tab):

    if ticker_text == "":
        return None

    validation = Ticker(ticker_text, validate=True).symbols
    if validation == []:
        return None

    current_year = int(today_date.strftime("%Y"))
    date_slider = dbc.Col(
        [
            dcc.RangeSlider(
                marks={
                    0: str(current_year - 4),
                    1: str(current_year - 3),
                    2: str(current_year - 2),
                    3: str(current_year - 1),
                    4: str(current_year),
                },
                step=1,
                value=[3, 4],
                id="my_range_slider",
                disabled=False,
            )
        ],
        width=8,
    )

    if tab == "summary_tab" and ticker_text is not None:
        price_data = yf.download(
            tickers=ticker_text,
            interval="1d",
            period="1y",
            prepost=False,
            threads=True,
        )
        price_data = price_data.reset_index()

        period = 52
        period_change = round(
            (
                (price_data.iloc[-1, 4] - price_data.iloc[0, 4])
                / price_data.iloc[0, 4]
                * 100
            ),
            2,
        )
        period_max = round(price_data["Close"].max(), 2)
        period_min = round(price_data["Close"].min(), 2)
        price_data["Change"] = (
            (price_data["Close"] - price_data["Close"].shift(1))
            / price_data["Close"].shift(1)
            * 100
        )
        max_gain = round(price_data["Change"].max(), 2)
        max_surge = round(price_data["Change"].min(), 2)

        if period_change >= 0:
            line_color = "#00b51a"
        else:
            line_color = "#ff2d21"

        price_graph = dcc.Graph(
            id="simple_price_chart",
            figure=go.Figure(
                data=[
                    go.Scatter(
                        x=price_data["Date"],
                        y=price_data["Close"],
                        line={"color": line_color},
                    )
                ],
                layout=go.Layout(
                    titlefont=dict(color="grey"),
                    showlegend=False,
                    yaxis=dict(
                        autorange=True,
                        titlefont=dict(color="grey"),
                        tickfont=dict(color="grey"),
                        gridcolor="grey",
                    ),
                    xaxis_rangeslider_visible=False,
                    xaxis=dict(
                        autorange=True,
                        titlefont=dict(color="grey"),
                        tickfont=dict(color="grey"),
                        gridcolor="grey",
                    ),
                    margin=go.layout.Margin(
                        l=40,  # left margin
                        r=0,  # right margin
                        b=5,  # bottom margin
                        t=40,  # top margin
                    ),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                ),
            ),
            style={
                "margin_bottom": "0px",
                "padding-bottom": "0px",
                "margin_right": "0px",
                "padding-right": "0px",
                "height": "400px",
                "overflow": "hidden",
                "background-color": "#211F32",
            },
        )

        value = value_rating(ticker_text)
        debt = debt_rating(ticker_text)
        stability = stability_rating(price_data)
        dividend = dividend_rating(ticker_text)
        future = future_rating(ticker_text)

        ratings = [value, debt, stability, dividend, future]
        ratings_sum = sum(ratings)
        if ratings_sum >= 15:
            inside_color = "rgb(0,181,26)"
        elif ratings_sum >= 7:
            inside_color = "rgb(255,255,0)"
        else:
            inside_color = "rgb(255,45,33)"

        radar_graph = dcc.Graph(
            id="radar_chart",
            figure=go.Figure(
                data=go.Scatterpolar(
                    r=ratings,
                    theta=["Value", "Debt", "Stability", "Dividends", "Future"],
                    fill="toself",
                    line=dict(color=inside_color, shape="spline"),
                    showlegend=False,
                ),
                layout=go.Layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True, range=[0, 5], showticklabels=False,
                        ),
                        angularaxis=dict(tickfont=dict(size=16, color="white"),),
                    ),
                    paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=60, r=60, t=40, b=20),
                ),
            ),
            style={"width": "400px", "height": "400px", "margin-left": "50px"},
        )

    infos = html.Div(
        id="infos_container",
        children=[
            html.H5(
                f"{period} Week change: {period_change}%",
                style={"color": "white", "margin-right": "20px"},
            ),
            html.H5(
                f"{period} Week max: {period_max}",
                style={"color": "white", "margin-right": "20px",},
            ),
            html.H5(
                f"{period} Week min: {period_min}",
                style={"color": "white", "margin-right": "20px"},
            ),
            html.H5(
                f"{period} Week max gain: {max_gain}%",
                style={"color": "white", "margin-right": "20px"},
            ),
            html.H5(
                f"{period} max surge: {max_surge}%",
                style={"color": "white", "margin-right": "20px"},
            ),
        ],
        style={"display": "flex", "margin": "auto", "justify-content": "center",},
    )

    charts = dbc.Row(
        [
            dbc.Col([price_graph], id="price_graph_col", width=8),
            dbc.Col([radar_graph], width=4),
        ],
        style={"margin-bottom": "40px"},
    )

    div = html.Div(children=[infos, charts, date_slider], style={"margin-top": "20px"},)

    return div


@app.callback(
    [
        Output("price_graph_col", "children"),
        Output("my_range_slider", "value"),
        Output("infos_container", "children"),
    ],
    Input("my_range_slider", "value"),
    [State("price_graph_col", "children"), State("input_ticker", "value")],
    State("infos_container", "children"),
)
def update_simple_chart(year, graph, ticker_text, infos):

    if year[1] != 4:
        return graph, [year[0], 4], infos

    if year[0] == 4:
        return graph, [3, 4], infos

    year_list = [4, 3, 2, 1, 0]
    year_rv = year[0]
    year_rv = year_list[year_rv]

    print(year_rv)

    price_data = yf.download(
        tickers=ticker_text,
        interval="1d",
        period=f"{year_rv}y",
        prepost=False,
        threads=True,
    )
    price_data = price_data.reset_index()

    period = 52 * (year_rv)
    period_change = round(
        (
            (price_data.iloc[-1, 4] - price_data.iloc[0, 4])
            / price_data.iloc[0, 4]
            * 100
        ),
        2,
    )
    period_max = round(price_data["Close"].max(), 2)
    period_min = round(price_data["Close"].min(), 2)
    price_data["Change"] = (
        (price_data["Close"] - price_data["Close"].shift(1))
        / price_data["Close"].shift(1)
        * 100
    )
    max_gain = round(price_data["Change"].max(), 2)
    max_surge = round(price_data["Change"].min(), 2)

    if period_change >= 0:
        line_color = "#00b51a"
    else:
        line_color = "#ff2d21"

    price_graph = dcc.Graph(
        id="simple_price_chart",
        figure=go.Figure(
            data=[
                go.Scatter(
                    x=price_data["Date"],
                    y=price_data["Close"],
                    line={"color": line_color},
                )
            ],
            layout=go.Layout(
                titlefont=dict(color="grey"),
                showlegend=False,
                yaxis=dict(
                    autorange=True,
                    titlefont=dict(color="grey"),
                    tickfont=dict(color="grey"),
                    gridcolor="grey",
                ),
                xaxis_rangeslider_visible=False,
                xaxis=dict(
                    autorange=True,
                    titlefont=dict(color="grey"),
                    tickfont=dict(color="grey"),
                    gridcolor="grey",
                ),
                margin=go.layout.Margin(
                    l=40,  # left margin
                    r=40,  # right margin
                    b=5,  # bottom margin
                    t=40,  # top margin
                ),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
            ),
        ),
        style={
            "margin_bottom": "0px",
            "padding-bottom": "0px",
            "height": "400px",
            "overflow": "hidden",
            "background-color": "#211F32",
        },
    )

    infos = [
        html.H5(
            f"{period} Week change: {period_change}%",
            style={"color": "white", "margin-right": "20px"},
        ),
        html.H5(
            f"{period} Week max: {period_max}",
            style={"color": "white", "margin-right": "20px",},
        ),
        html.H5(
            f"{period} Week min: {period_min}",
            style={"color": "white", "margin-right": "20px"},
        ),
        html.H5(
            f"{period} Week max gain: {max_gain}%",
            style={"color": "white", "margin-right": "20px"},
        ),
        html.H5(
            f"{period} max surge: {max_surge}%",
            style={"color": "white", "margin-right": "20px"},
        ),
    ]

    return price_graph, year, infos


if __name__ == "__main__":
    app.run_server(debug=True)
