import plotly.express as px
import matplotlib.pyplot as plt
import yfinance as yf
import numpy as np


def count_zeros_after_decimal(number):
    """Counts number of "0" after decimal in selected number"""
    number_after_decimal = str(number).split(".")[1]
    count = 1
    for symbol in number_after_decimal:
        if symbol == "0":
            count += 1
        else:
            break
    return count


def get_linear_regression_params(ticker, interval, start_date, end_date):
    """Calculates and creates linear regression chart with trendline of provided stock"""

    data = yf.download(
        tickers=f"{ticker} SPY", interval=interval, start=start_date, end=end_date
    )

    data = data["Close"]

    returns = np.log(data).diff()
    returns = returns.dropna()
    correlation = returns.corr()
    reg = np.polyfit(returns["SPY"], returns[ticker], deg=1)
    trend = np.polyval(reg, returns[ticker])
    # plt.scatter(x=returns["SPY"], y=returns[ticker])
    # plt.plot(returns[ticker], trend, 'r')
    output = {"Returns": returns, "Correlation": correlation, "Trend": trend}

    return output


def calculate_streak(data, up=True):
    """Calculates longest streak of up or down values in provided DataFrame"""

    max_streak = 0
    current_streak = 0
    if up == True:
        for row in range(len(data.index)):
            if data.iloc[row, 0] > 0:
                current_streak += 1
                if current_streak > max_streak:
                    max_streak = current_streak
            else:
                current_streak = 0
    else:
        for row in range(len(data.index)):
            if data.iloc[row, 0] < 0:
                current_streak += 1
                if current_streak > max_streak:
                    max_streak = current_streak
            else:
                current_streak = 0

    return max_streak


def get_percentage_returns_statistics(data):
    """Returns a dictionary containing statistics on the percentage returns of the provided OHLC data."""
    data = data[["Close"]]
    data["Percentage returns"] = data["Close"].pct_change() * 100
    data.dropna(inplace=True)
    data = data[["Percentage returns"]]

    number_of_candles = len(data)
    avg_candle = data["Percentage returns"].mean()
    max_candle = data["Percentage returns"].max()
    min_candle = data["Percentage returns"].min()

    number_of_up_candles = len(data[data["Percentage returns"] > 0])
    avg_up_candle = (data["Percentage returns"][data["Percentage returns"] > 0]).mean()
    max_up_candle = (data["Percentage returns"][data["Percentage returns"] > 0]).max()
    min_up_candle = (data["Percentage returns"][data["Percentage returns"] > 0]).min()
    longest_up_streak = calculate_streak(data, True)

    number_of_down_candles = len(data[data["Percentage returns"] < 0])
    avg_down_candle = (
        data["Percentage returns"][data["Percentage returns"] < 0]
    ).mean()
    max_down_candle = (data["Percentage returns"][data["Percentage returns"] > 0]).max()
    min_down_candle = (data["Percentage returns"][data["Percentage returns"] > 0]).min()
    longest_down_streak = calculate_streak(data, False)

    output = {
        "Number of candles": number_of_candles,
        "Average candle": avg_candle,
        "Biggest candle": max_candle,
        "Smallest candle": min_candle,
        "Number of up candles": number_of_up_candles,
        "Average up candle": avg_up_candle,
        "Biggest up candle": max_up_candle,
        "Smallest up candle": min_up_candle,
        "Longest up streak": longest_up_streak,
        "Number of down candles": number_of_down_candles,
        "Average down candle": avg_down_candle,
        "Biggest down candle": max_down_candle,
        "Smallest down candle": min_down_candle,
        "Longest down streak": longest_down_streak,
    }

    return output

