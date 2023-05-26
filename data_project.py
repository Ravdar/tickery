import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State, MATCH, ALLSMALLER
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.graph_objects as go
import datetime
from datetime import date, timedelta

ticker_list = [
    "^DJI",
    "^GDAXI",
    "AAPL",
    "AMD",
    "AMZN",
    "BTC-USD",
    "BYND",
    "CL=F",
    "ETH-USD",
    "EURCHF=X",
    "EURUSD=X",
    "GC=F",
    "JPY=X",
    "TSLA",
]
intervals = ["1d", "1m", "1mo", "1wk", "3mo", "5m", "15m", "30m", "60m", "90m"]

file_path = f"C:\\Users\Tomasz\\Desktop\\Test_folder\\BYND\\3mo\\CSV RAW\\BYND"

ticker = pd.DataFrame(columns=["Datetime", "Open", "High", "Low", "Close", "Adj Close"])

min = ticker["Low"].min()
avg = 8
max = ticker["High"].max()
price_range = round((max - min), 2)
perc_range = round((price_range / max * 100), 2)


today_date = pd.Timestamp.now()
week_ago = pd.to_datetime(datetime.datetime.now() - timedelta(weeks=1))

n_clicks = 0

app = dash.Dash()


def generate_new_layout(n_clicks):

    return html.Div(
        children=[
            html.Div(
                children=[
                    html.H4("Min:", style={"display": "inline"}),
                    html.P(
                        id={"type": "min_label", "index": n_clicks},
                        style={"display": "inline", "margin-left": "5px"},
                    ),
                ],
                style={
                    "display": "inline-block",
                    "margin-left": "80px",  # level with graph
                    "margin-right": "20px",
                },
            ),
            html.Div(
                children=[
                    html.H4("Avg:", style={"display": "inline"}),
                    html.P(
                        id={"type": "avg_label", "index": n_clicks},
                        style={"display": "inline", "margin-left": "5px"},
                    ),
                ],
                style={"display": "inline-block", "margin-right": "20px"},
            ),
            html.Div(
                children=[
                    html.H4("Max:", style={"display": "inline"}),
                    html.P(
                        id={"type": "max_label", "index": n_clicks},
                        style={"display": "inline", "margin-left": "5px"},
                    ),
                ],
                style={"display": "inline-block", "margin-right": "20px"},
            ),
            html.Div(
                children=[
                    html.H4("Percentage change:", style={"display": "inline"}),
                    html.P(
                        id={"type": "perc_change_label", "index": n_clicks},
                        style={"display": "inline", "margin-left": "5px"},
                    ),
                ],
                style={
                    "display": "inline-block",
                    "margin-right": "20px",
                    "margin-bottom": "0px",
                },
            ),
            html.Div(
                children=[
                    html.H4("Price range:", style={"display": "inline"}),
                    html.P(
                        id={"type": "price_range_label", "index": n_clicks},
                        style={"display": "inline", "margin-left": "5px"},
                    ),
                ],
                style={"display": "inline-block", "margin-right": "20px"},
            ),
            html.Div(
                children=[
                    html.H4("Percentage range:", style={"display": "inline"}),
                    html.P(
                        id={"type": "perc_range_label", "index": n_clicks},
                        style={"display": "inline", "margin-left": "5px"},
                    ),
                ],
                style={
                    "display": "inline-block",
                    "margin-right": "20px",
                    "margin-bottom": "0px",
                },
            ),
            html.Div(
                children=[
                    html.Div(
                        children=[
                            dcc.DatePickerRange(
                                id={"type": "date_picker", "index": n_clicks},
                                min_date_allowed=date(1900, 1, 1,),
                                max_date_allowed=date(
                                    today_date.year, today_date.month, today_date.day
                                ),
                                initial_visible_month=date(
                                    week_ago.year, week_ago.month, week_ago.day
                                ),
                                end_date=date(
                                    week_ago.year, week_ago.month, week_ago.day
                                ),
                                style={
                                    "width": "300px",
                                    "margin-left": "80px",
                                    "margin-top": "20px",
                                },
                            ),
                        ],
                    ),
                    html.Div(
                        children=[
                            dcc.Dropdown(
                                options=[{"label": i, "value": i} for i in ticker_list],
                                id={"type": "ticker_dropdown", "index": n_clicks},
                                placeholder="Select a ticker",
                                style={
                                    "width": "200px",
                                    "margin-right": "20px",
                                    "margin-top": "20px",
                                },
                            ),
                        ],
                    ),
                    html.Div(
                        children=[
                            dcc.Dropdown(
                                options=[{"label": i, "value": i} for i in intervals],
                                id={"type": "interval_dropdown", "index": n_clicks},
                                placeholder="Select interval",
                                style={
                                    "width": "200px",
                                    "margin-right": "20px",
                                    "margin-top": "20px",
                                },
                            ),
                        ],
                    ),
                    html.Button("Add chart", "add-chart", n_clicks=n_clicks,),
                    dcc.Checklist(
                        ["Remove blanks from x axis"],
                        id={"type": "check_blank", "index": n_clicks},
                        inline=True,
                    ),
                ],
                style={
                    "display": "flex",
                    "align-items": "center",
                    "justify-content": "center",
                },
            ),
            dcc.Graph(
                id={"type": "chart", "index": n_clicks},
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
                        title="BTCUSD",
                        yaxis={"autorange": True},
                        xaxis_rangeslider_visible=False,
                    ),
                ),
            ),
            html.Div(
                children=[
                    html.H4("Avg change candle:", style={"display": "inline"}),
                    html.P(
                        id={"type": "avg_change_candle", "index": n_clicks},
                        style={"display": "inline", "margin-left": "5px"},
                    ),
                ],
                style={
                    "display": "inline-block",
                    "margin-left": "80px",  # level with graph
                    "margin-right": "20px",
                },
            ),
            html.Div(
                children=[
                    html.H4("Min change candle:", style={"display": "inline"}),
                    html.P(
                        id={"type": "min_change_candle", "index": n_clicks},
                        style={"display": "inline", "margin-left": "5px"},
                    ),
                ],
                style={"display": "inline-block", "margin-right": "20px"},
            ),
            html.Div(
                children=[
                    html.H4("Max change candle", style={"display": "inline"}),
                    html.P(
                        id={"type": "max_change_candle", "index": n_clicks},
                        style={"display": "inline", "margin-left": "5px"},
                    ),
                ],
                style={"display": "inline-block", "margin-right": "20px"},
            ),
            html.Div(
                children=[
                    html.H4("Avg range candle:", style={"display": "inline"}),
                    html.P(
                        id={"type": "avg_range_candle", "index": n_clicks},
                        style={"display": "inline", "margin-left": "5px"},
                    ),
                ],
                style={
                    "display": "inline-block",
                    "margin-right": "20px",
                    "margin-bottom": "0px",
                },
            ),
            html.Div(
                children=[
                    html.H4("Min range candle:", style={"display": "inline"}),
                    html.P(
                        id={"type": "min_range_candle", "index": n_clicks},
                        style={"display": "inline", "margin-left": "5px"},
                    ),
                ],
                style={"display": "inline-block", "margin-right": "20px"},
            ),
            html.Div(
                children=[
                    html.H4("Max range candle:", style={"display": "inline"}),
                    html.P(
                        id={"type": "max_range_candle", "index": n_clicks},
                        style={"display": "inline", "margin-left": "5px"},
                    ),
                ],
                style={
                    "display": "inline-block",
                    "margin-right": "20px",
                    "margin-bottom": "0px",
                },
            ),
            html.Div(
                children=[
                    html.H4("Avg gap:", style={"display": "inline"}),
                    html.P(
                        id={"type": "avg_gap", "index": n_clicks},
                        style={"display": "inline", "margin-left": "5px"},
                    ),
                ],
                style={
                    "display": "inline-block",
                    "margin-left": "80px",  # level with graph
                    "margin-right": "20px",
                },
            ),
            html.Div(
                children=[
                    html.H4("Min gap:", style={"display": "inline"}),
                    html.P(
                        id={"type": "min_gap", "index": n_clicks},
                        style={"display": "inline", "margin-left": "5px"},
                    ),
                ],
                style={"display": "inline-block", "margin-right": "20px"},
            ),
            html.Div(
                children=[
                    html.H4("Max gap:", style={"display": "inline"}),
                    html.P(
                        id={"type": "max_gap", "index": n_clicks},
                        style={"display": "inline", "margin-left": "5px"},
                    ),
                ],
                style={"display": "inline-block", "margin-right": "20px"},
            ),
        ],
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
        generate_new_layout(n_clicks),
    ],
)

# Callback part


@app.callback(
    Output("dynamic-container", "children"),
    Input("add-chart", "n_clicks"),
    State("dynamic-container", "children"),
)
def add_new_chart(n_clicks, children):
    print(n_clicks)
    if n_clicks < 1:
        raise PreventUpdate
    new_layout = generate_new_layout(n_clicks)
    children.append(new_layout)
    return children


@app.callback(
    [
        Output({"type": "chart", "index": MATCH}, "figure"),
        Output({"type": "min_label", "index": MATCH}, "children"),
        Output({"type": "avg_label", "index": MATCH}, "children"),
        Output({"type": "max_label", "index": MATCH}, "children"),
        Output({"type": "perc_change_label", "index": MATCH}, "children"),
        Output({"type": "price_range_label", "index": MATCH}, "children"),
        Output({"type": "perc_range_label", "index": MATCH}, "children"),
        Output({"type": "avg_change_candle", "index": MATCH}, "children"),
        Output({"type": "min_change_candle", "index": MATCH}, "children"),
        Output({"type": "max_change_candle", "index": MATCH}, "children"),
        Output({"type": "avg_range_candle", "index": MATCH}, "children"),
        Output({"type": "min_range_candle", "index": MATCH}, "children"),
        Output({"type": "max_range_candle", "index": MATCH}, "children"),
        Output({"type": "avg_gap", "index": MATCH}, "children"),
        Output({"type": "min_gap", "index": MATCH}, "children"),
        Output({"type": "max_gap", "index": MATCH}, "children"),
    ],
    [
        Input({"type": "ticker_dropdown", "index": MATCH}, "value"),
        Input({"type": "interval_dropdown", "index": MATCH}, "value"),
        Input({"type": "date_picker", "index": MATCH}, "start_date"),
        Input({"type": "date_picker", "index": MATCH}, "end_date"),
        Input({"type": "check_blank", "index": MATCH}, "value"),
    ],
)
def update_chart(ticker_value, interval_value, start_date, end_date, check_value):

    if start_date is None:
        start_date = end_date

    if ticker_value is None or interval_value is None:
        return (
            go.Figure(),
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )

    file_path = f"C:\\Users\\Tomasz\\Desktop\\Test_folder\\{ticker_value}\\{interval_value}\\CSV RAW\\{ticker_value}"
    ticker = pd.read_csv(file_path)
    if ticker.columns[0] != "Date":
        start_date = f"{start_date} 00:00:00"
        end_date = f"{end_date} 23:59:59"

    ticker = ticker[(ticker.iloc[:, 0] >= start_date) & (ticker.iloc[:, 0] <= end_date)]
    ticker["Perc change"] = (ticker["Open"] - ticker["Close"]) / ticker["Open"] * 100
    ticker["Perc range"] = (ticker["High"] - ticker["Low"]) / ticker["High"] * 100
    ticker["Gap"] = (ticker["Open"] - ticker["Close"].shift(1)) / ticker["Open"] * 100
    ticker["Gap"] = ticker["Gap"].fillna(0)

    # STATISTICS
    # Whole period
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

    if check_value != ["Remove blanks from x axis"]:
        fig = go.Figure(
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
                title=ticker_value,
                yaxis={"autorange": True},
                xaxis_rangeslider_visible=False,
            ),
        )
    else:
        length_df = len(ticker.index)
        if length_df < 25:
            tick_indices = [i for i in range(0, length_df, 1)]
        else:
            tick_indices = [i for i in range(0, length_df, length_df // 25)]
        tick_values = ticker.index[tick_indices]
        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=ticker.index,
                    open=ticker["Open"],
                    high=ticker["High"],
                    low=ticker["Low"],
                    close=ticker["Close"],
                )
            ],
            layout=go.Layout(
                title=ticker_value,
                yaxis={"autorange": True},
                xaxis_rangeslider_visible=False,
            ),
        )

    return (
        fig,
        min,
        avg,
        max,
        f"{perc_change} %",
        price_range,
        f"{perc_range} %",
        f"{avg_perc_change} %",
        f"{min_perc_change} %",
        f"{max_perc_change} %",
        f"{avg_perc_range} %",
        f"{min_perc_range} %",
        f"{max_perc_range} %",
        f"{avg_gap} %",
        f"{min_gap} %",
        f"{max_gap} %",
    )


if __name__ == "__main__":
    app.run_server(debug=True)
