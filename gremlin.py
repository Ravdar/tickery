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

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout part
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
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Moving average")),
                dbc.ModalBody(
                    [
                        dbc.Label("Length:"),
                        dbc.Input(id="ma_length", type="number", disabled=False),
                    ]
                ),
                dbc.ModalFooter([dbc.Button("OK", color="primary", id="ma_ok"),]),
            ],
            id="moving_average_modal",
        ),
        html.Div(id="indicators_container", children=[]),
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
                    yaxis={"autorange": True},
                    xaxis_rangeslider_visible=False,
                ),
            ),
        ),
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
        go.Scatter(x=ticker.index, y=ticker["BB Up"], mode="lines", name="BB Up",)
    )

    fig_data.append(
        go.Scatter(x=ticker.index, y=ticker["MA-TP"], mode="lines", name="MA-TP",)
    )

    fig_data.append(
        go.Scatter(x=ticker.index, y=ticker["BB Down"], mode="lines", name="BB Down",)
    )


def add_indicator(indicator_name, indicator_settings):

    return html.Div(
        [
            dbc.Button(
                f"{indicator_name}({indicator_settings})",
                id="ma_button",
                color="primary",
                className="me-1",
            ),
            dbc.Button("X", id="ma_x_button", color="primary", className="me-1"),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle(indicator_name)),
                    dbc.ModalBody(
                        [
                            dbc.Label("Length:"),
                            dbc.Input(
                                id="ma_length_button",
                                value=indicator_settings,
                                type="number",
                                disabled=False,
                            ),
                        ]
                    ),
                    dbc.ModalFooter(
                        [dbc.Button("OK", color="primary", id="ma_ok_button"),]
                    ),
                ],
                id="moving_average_modal_button",
            ),
        ]
    )


@app.callback(
    Output("moving_average_modal", "is_open"), Input("indicator_dropdown", "value"),
)
def show_ma_modal(indicator_value):

    if indicator_value == "Moving average":
        return True
    else:
        return False


@app.callback(
    [
        Output("indicator_dropdown", "value"),
        Output("indicators_container", "children"),
    ],
    Input("ma_ok", "n_clicks"),
    State("ma_length", "value"),
)
def draw_ma(n_clicks, ma_length):
    if n_clicks != None:
        ma_button = add_indicator("Moving average", ma_length)
        n_clicks = None
        return None, ma_button


# BUTTON PART
# Clicking button
@app.callback(
    Output("moving_average_modal_button", "is_open"), Input("ma_button", "n_clicks")
)
def show_ma_modal_button(n_clicks):
    if n_clicks != None:
        n_clicks = None
        return True
    else:
        return False


# Confirming settings
@app.callback(
    [Output("ma_button", "n_clicks"), Output("ma_button", "children")],
    Input("ma_ok_button", "n_clicks"),
    [State("ma_length_button", "value"), State("indicator_dropdown", "value")],
)
def update_indicator(n_clicks, indicator_length, indicator_name):
    if n_clicks != None:
        button_value = f"{indicator_name}({indicator_length})"
        n_clicks = None
        return None, button_value


# Deleting button
@app.callback(
    [Output("ma_button", "style"), Output("ma_x_button", "style")],
    Input("ma_x_button", "n_clicks"),
)
def delete_ma_buttons(n_clicks):
    if n_clicks != None:
        return {"display": "none"}, {"display": "none"}


# UPDATING CHART
@app.callback(
    [Output("ticker_cndl_chart", "figure"), Output("error_alert", "is_open")],
    [
        Input("input_ticker", "value"),
        Input("interval_dropdown", "value"),
        Input("date_picker", "start_date"),
        Input("date_picker", "end_date"),
        Input("ma_ok", "n_clicks"),
        Input("indicator_dropdown", "value"),
    ],
    State("ma_length", "value"),
)
def update_chart(
    ticker_value,
    interval_value,
    start_date,
    end_date,
    ok_button,
    indicator_value,
    ma_length,
):

    if ticker_value is None or interval_value is None or start_date is None:
        return go.Figure(), False

    ticker = yf.download(
        tickers=ticker_value,
        interval=interval_value,
        start=start_date,
        end=end_date,
        prepost=False,
        threads=True,
    )

    if ticker.empty:
        return go.Figure(), True

    ticker = ticker.reset_index()

    length_df = len(ticker.index)
    if length_df < 25:
        tick_indices = [i for i in range(0, length_df, 1)]
    else:
        tick_indices = [i for i in range(0, length_df, length_df // 25)]
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
    if ok_button == 1:
        add_moving_average(
            ma_length,
            ticker,
            fig_data,
            ticker_value,
            interval_value,
            start_date,
            end_date,
        )
    if indicator_value == "Bollinger Bands":
        add_bollinger_bands(
            20, 2, ticker, fig_data, ticker_value, interval_value, start_date, end_date,
        )
        print("Done")

    fig = go.Figure(
        data=fig_data,
        layout=go.Layout(
            title=ticker_value,
            yaxis={"autorange": True},
            xaxis_rangeslider_visible=False,
            xaxis={"tickmode": "array", "tickvals": tick_values, "ticktext": ticktext,},
        ),
    )
    print(ok_button)

    return fig, False


if __name__ == "__main__":
    app.run_server(debug=True)
