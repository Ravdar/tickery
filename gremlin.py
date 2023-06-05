import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State, MATCH, ALLSMALLER, ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import datetime
from datetime import date, timedelta
import yfinance as yf


intervals = ["1d", "1m", "1mo", "1wk", "3mo", "5m", "15m", "30m", "60m", "90m"]
indicators = ["Moving average", "Bollinger Bands", "MACD", "Stochastic"]
ticker = pd.DataFrame(columns=["Datetime", "Open", "High", "Low", "Close", "Adj Close"])
today_date = pd.Timestamp.now()
week_ago = pd.to_datetime(datetime.datetime.now() - timedelta(weeks=1))
colors = {"background": "#111111", "text": "#7FDBFF"}

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])


def add_indicator_button(
    indicator_short, indicator_name, length, std, s2_display, button_visible
):

    return html.Div(
        [
            dbc.Button(
                f"{indicator_name}({length, std}",
                id=f"{indicator_short}_button",
                color="primary",
                className="me-1",
                style={"display": button_visible},
            ),
            dbc.Button(
                "X",
                id=f"{indicator_short}_x_button",
                color="primary",
                className="me-1",
                style={"display": button_visible},
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle(indicator_name)),
                    dbc.ModalBody(
                        [
                            dbc.Label("Length:"),
                            dbc.Input(
                                id=f"{indicator_short}_length",
                                type="number",
                                disabled=False,
                            ),
                            dbc.Label(
                                "Standard deviation:", style={"display": s2_display}
                            ),
                            dbc.Input(
                                id=f"{indicator_short}_std",
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
        ]
    )


# Layout part
app.layout = html.Div(
    id="dynamic-container",
    children=[
        html.H1("OHLC Analyzer Tool", style={"text-align": "center"}),
        html.P(
            "This is a tool that helps to analyze OHLC data.",
            style={"text-align": "center"},
        ),
        html.Div(
            dcc.Input(
                id="input_ticker".format("search"),
                type="search",
                placeholder="Search ticker".format("search"),
                style={"width": "230px"},
            ),
            style={"display": "flex", "justify-content": "center"},
        ),
        html.Div(
            dcc.Dropdown(
                options=[{"label": i, "value": i} for i in intervals],
                id="interval_dropdown",
                placeholder="Select interval",
                style={"width": "230px", "margin-top": "10px"},
            ),
            style={"display": "flex", "justify-content": "center"},
        ),
        html.Div(
            dcc.DatePickerRange(
                id="date_picker",
                min_date_allowed=date(1900, 1, 1,),
                max_date_allowed=date(
                    today_date.year, today_date.month, today_date.day
                ),
                initial_visible_month=date(week_ago.year, week_ago.month, week_ago.day),
                end_date=date(today_date.year, today_date.month, today_date.day),
                style={"margin-top": "10px"},
            ),
            style={"display": "flex", "justify-content": "center"},
        ),
        html.Div(
            dbc.Alert(
                "Invalid ticker or data range. Please be aware that for shorter intervals, only the data from the past 7 days is available.",
                id="error_alert",
                color="danger",
                dismissable=True,
                is_open=False,
                duration=4500,
            ),
            style={"display": "flex", "justify-content": "center"},
        ),
        dcc.Dropdown(
            options=[{"label": i, "value": i} for i in indicators],
            id="indicator_dropdown",
            placeholder="Select indicator",
            style={"width": "230px", "margin-top": "10px"},
        ),
        html.Div(
            id="modals",
            children=[
                add_indicator_button("ma", "Moving average", 0, 0, "none", "none"),
                add_indicator_button("bb", "Bollinger Bands", 0, 0, "display", "none"),
                add_indicator_button("st", "Stochastic", 0, 0, "display", "none"),
                add_indicator_button("macd", "MACD", 0, 0, "display", "none"),
            ],
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
                    title="Chart",
                    showlegend=False,
                    yaxis={"autorange": True},
                    xaxis_rangeslider_visible=False,
                    margin=go.layout.Margin(
                        l=40,  # left margin
                        r=40,  # right margin
                        b=5,  # bottom margin
                        t=40,  # top margin
                    ),
                ),
            ),
            style={
                "margin_bottom": "0px",
                "padding-bottom": "0px",
                "height": "550px",
                "width": "100%",
            },
            className="h-5",
        ),
        html.Div(id="stoch_container", children=[],),
        html.Div(id="macd_container", children=[],),
    ],
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
                    yaxis={"autorange": True},
                    xaxis_rangeslider_visible=False,
                    xaxis={"showticklabels": xaxis},
                    margin=go.layout.Margin(
                        l=40,  # left margin
                        r=40,  # right margin
                        b=5,  # bottom margin
                        t=0,  # top margin
                    ),
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
                    titlefont=dict(color="#1f77b4"),
                    tickfont=dict(color="#1f77b4"),
                ),
                yaxis2=dict(
                    titlefont=dict(color="#ff7f0e"),
                    tickfont=dict(color="#ff7f0e"),
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
                    b=0,  # bottom margin
                    t=0,  # top margin
                ),
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
        return None, {"display": "flex"}, {"display": "flex"}


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
        return None, {"display": "flex"}, {"display": "flex"}


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
        return None, {"display": "flex"}, {"display": "flex"}


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
        return None, {"display": "flex"}, {"display": "flex"}


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
    [State("ma_length", "value"), State("ma_button", "children")],
)
def update_indicator(n_clicks, indicator_length, indicator_name):
    if n_clicks != None:
        button_value = f"{indicator_name[:14]}({indicator_length})"
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
        State("bb_length", "value"),
        State("bb_std", "value"),
        State("bb_button", "children"),
    ],
)
def update_indicator(n_clicks, indicator_length, indicator_std, indicator_name):
    if n_clicks != None:
        button_value = f"{indicator_name[:15]}({indicator_length}, {indicator_std})"
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
        State("st_length", "value"),
        State("st_std", "value"),
        State("st_button", "children"),
    ],
)
def update_indicator(n_clicks, indicator_length, indicator_std, indicator_name):
    if n_clicks != None:
        button_value = f"{indicator_name[:10]}({indicator_length}, {indicator_std})"
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
        State("macd_length", "value"),
        State("macd_std", "value"),
        State("macd_button", "children"),
    ],
)
def update_indicator(n_clicks, indicator_length, indicator_std, indicator_name):
    if n_clicks != None:
        button_value = f"{indicator_name[:4]}({indicator_length}, {indicator_std})"
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


# UPDATING CHART
@app.callback(
    [
        Output("ticker_cndl_chart", "figure"),
        Output("error_alert", "is_open"),
        Output("stoch_container", "children", allow_duplicate=True),
        Output("macd_container", "children", allow_duplicate=True),
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
    ],
    State("ma_length", "value"),
    State("bb_length", "value"),
    State("bb_std", "value"),
    State("st_length", "value"),
    State("st_std", "value"),
    State("macd_length", "value"),
    State("macd_std", "value"),
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
    ma_length,
    bb_length,
    bb_std,
    st_length,
    st_slowing,
    fast_ema,
    slow_ema,
):
    stoch = []
    macd = []

    if ticker_value is None or interval_value is None or start_date is None:
        return go.Figure(), False, stoch

    ticker = yf.download(
        tickers=ticker_value,
        interval=interval_value,
        start=start_date,
        end=end_date,
        prepost=False,
        threads=True,
    )

    if ticker.empty:
        return go.Figure(), True, stoch

    ticker = ticker.reset_index()

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

    fig_data = [
        go.Candlestick(
            x=ticker.index,
            open=ticker["Open"],
            high=ticker["High"],
            low=ticker["Low"],
            close=ticker["Close"],
            name="OHLC",
        )
    ]

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

    print(f"equals to:{macd_ok}")
    # Handle MACD if needed
    if macd_ok is not None:
        print("It is not None")
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
        xaxis = {"showticklabels": False}
    else:
        xaxis = {
            "tickmode": "array",
            "tickvals": tick_values,
            "ticktext": ticktext,
        }

    fig = go.Figure(
        data=fig_data,
        layout=go.Layout(
            title=ticker_value,
            showlegend=False,
            yaxis={"autorange": True},
            xaxis_rangeslider_visible=False,
            xaxis=xaxis,
            margin=go.layout.Margin(
                l=40,  # left margin
                r=40,  # right margin
                b=5,  # bottom margin
                t=40,  # top margin
            ),
        ),
    )
    print(f"equals to:{macd_ok}")

    return fig, False, stoch, macd


if __name__ == "__main__":
    app.run_server(debug=True)
