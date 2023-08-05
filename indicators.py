import yfinance as yf
import datetime
from datetime import date, timedelta
import plotly.graph_objects as go
from dash import dcc

BG_COLOR = "#211F32"


def add_moving_average(
    ma_length, ticker, fig_data, ticker_value, interval_value, start_date, end_date
):
    """Based on provided settings calculates and adds moving average indicator to the graph"""

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
            line=dict(color="blue"),
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
    """Based on provided settings calculates and adds bollinger bands indicator to the graph"""

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
        go.Scatter(
            x=ticker.index,
            y=ticker["BB Up"],
            mode="lines",
            name="BB Up",
            line=dict(color="green"),
        )
    )

    fig_data.append(
        go.Scatter(
            x=ticker.index,
            y=ticker["MA-TP"],
            mode="lines",
            name="MA-TP",
            line=dict(color="blue"),
        )
    )

    fig_data.append(
        go.Scatter(
            x=ticker.index,
            y=ticker["BB Down"],
            mode="lines",
            name="BB Down",
            line=dict(color="red"),
        )
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
    """Based on provided settings calculates and adds stochastic indicator to the graph"""

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
                    go.Scatter(
                        x=ticker.iloc[:, 0],
                        y=ticker["%K"],
                        name="%K",
                        line=dict(color="#3ad1b8"),
                    ),
                    go.Scatter(
                        x=ticker.iloc[:, 0],
                        y=ticker["%D"],
                        name="%D",
                        line=dict(color="magenta"),
                    ),
                ],
                layout=go.Layout(
                    showlegend=False,
                    yaxis=dict(
                        autorange=True, tickfont=dict(color="white"), gridcolor="grey",
                    ),
                    xaxis_rangeslider_visible=False,
                    xaxis=dict(
                        showticklabels=xaxis,
                        autorange=True,
                        tickfont=dict(color="white"),
                        gridcolor="grey",
                    ),
                    margin=go.layout.Margin(l=40, r=40, b=5, t=0,),
                    paper_bgcolor=BG_COLOR,
                    plot_bgcolor=BG_COLOR,
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
    """Based on provided settings calculates and adds MACD indicator to the graph"""

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
                    marker=dict(color="yellow"),
                ),
                go.Bar(
                    x=macd_negative.iloc[:, 0],
                    y=macd_negative["MACD"],
                    name="MACD",
                    yaxis="y1",
                    marker=dict(color="orange"),
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
                    autorange=True, tickfont=dict(color="white"), gridcolor="gray",
                ),
                yaxis2=dict(
                    tickfont=dict(color="white"),
                    gridcolor="gray",
                    anchor="free",
                    overlaying="y",
                    side="right",
                    position=1,
                ),
                showlegend=False,
                xaxis_rangeslider_visible=False,
                xaxis={"showticklabels": xaxis, "tickfont": {"color": "white"}},
                margin=go.layout.Margin(l=40, r=40, b=5, t=0,),
                paper_bgcolor=BG_COLOR,
                plot_bgcolor=BG_COLOR,
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
