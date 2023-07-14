import plotly.express as px
import matplotlib.pyplot as plt
import yfinance as yf
import numpy as np
from scipy.stats import norm


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


def monte_carlo_simulation(data, number_of_simulations=150, forecast_period=100):
    """Returns numpy array of simulated prices for provided forecast period and number of simulations"""

    returns = data["Close"].pct_change()
    last_price = data["Close"].iloc[-1]
    average_return = returns.mean()
    return_std = returns.std()

    simulated_prices = np.zeros((forecast_period, number_of_simulations))

    for simulation in range(number_of_simulations):
        prices = [last_price]
        for x in range(forecast_period):
            daily_return = np.random.normal(average_return, return_std)
            price = prices[-1] * (1 + daily_return)
            prices.append(price)
        simulated_prices[:, simulation] = prices[1:]

    return simulated_prices


def historical_and_parametric_var_and_cvar(data):
    """Returns VaR and CVaR for 0,95;0,99 and 0,999 confidence level both for historical and parametric calculation method"""

    data["Returns"] = data["Close"].pct_change()
    data = data[["Returns"]]
    data = data.dropna()
    std = data["Returns"].std()
    mean_return = data["Returns"].mean()

    # HISTORICAL

    var95 = data["Returns"].quantile(0.05)
    cvar95 = data.loc[data["Returns"] <= var95, "Returns"].mean()

    var99 = data["Returns"].quantile(0.01)
    cvar99 = data.loc[data["Returns"] <= var99, "Returns"].mean()

    var999 = data["Returns"].quantile(0.001)
    cvar999 = data.loc[data["Returns"] <= var999, "Returns"].mean()

    # PARAMETRIC

    p_var95 = mean_return - norm.ppf(0.95) * std
    p_cvar95 = mean_return - (norm.ppf(0.95) * std / (1 - 0.95))

    p_var99 = mean_return - norm.ppf(0.99) * std
    p_cvar99 = mean_return - (norm.ppf(0.99) * std / (1 - 0.99))

    p_var999 = mean_return - norm.ppf(0.999) * std
    p_cvar999 = mean_return - (norm.ppf(0.999) * std / (1 - 0.999))

    output = {
        "Historical": {
            "VaR": {"95": var95, "99": var99, "99.9": var999},
            "CVaR": {"95": cvar95, "99": cvar99, "99.9": cvar999},
        },
        "Parametric": {
            "VaR": {"95": p_var95, "99": p_var99, "99.9": p_var999},
            "CVaR": {"95": p_cvar95, "99": p_cvar99, "99.9": p_cvar999},
        },
    }

    return output

