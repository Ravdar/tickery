import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State, MATCH, ALLSMALLER
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
                        dbc.Input(id="ma_input", type="number", disabled=False),
                    ]
                ),
                dbc.ModalFooter(
                    [
                        dbc.Button("OK", color="primary", id="ma_ok"),
                        dbc.Button("Cancel", id="ma_cancel"),
                    ]
                ),
            ],
            id="moving_average_modal",
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
                    yaxis={"autorange": True},
                    xaxis_rangeslider_visible=False,
                ),
            ),
        ),
    ],
)


@app.callback(
    [Output("ticker_cndl_chart", "figure"), Output("error_alert", "is_open")],
    [
        Input("input_ticker", "value"),
        Input("interval_dropdown", "value"),
        Input("date_picker", "start_date"),
        Input("date_picker", "end_date"),
        Input("indicator_dropdown", "value"),
    ],
)
def update_chart(ticker_value, interval_value, start_date, end_date, indicator_value):

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
    if indicator_value == "Moving average":
        ticker2 = yf.download(
            tickers=ticker_value,
            interval=interval_value,
            start=(
                datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
                - timedelta(days=15)
            ),
            end=end_date,
            prepost=False,
            threads=True,
        )
        if ticker2.empty:
            ticker["Moving Average"] = ticker["Close"].rolling(window=10).mean()
        else:
            ticker2["Moving Average"] = ticker2["Close"].rolling(window=10).mean()
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

    fig = go.Figure(
        data=fig_data,
        layout=go.Layout(
            title=ticker_value,
            yaxis={"autorange": True},
            xaxis_rangeslider_visible=False,
            xaxis={"tickmode": "array", "tickvals": tick_values, "ticktext": ticktext,},
        ),
    )
    print(ticker)

    return fig, False


if __name__ == "__main__":
    app.run_server(debug=True)
