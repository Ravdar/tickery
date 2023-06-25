import yahooquery as yq
from yahooquery import Ticker
import numpy as np
import yfinance as yf


def value_rating(ticker_text):
    ticker = Ticker(ticker_text)
    try:
        pe_ratio = ticker.summary_detail[ticker_text]["trailingPE"]
    except KeyError:
        return 0
    if pe_ratio < 20:
        return 5
    elif pe_ratio < 30:
        return 4
    elif pe_ratio < 50:
        return 3
    elif pe_ratio < 70:
        return 2
    else:
        return 1


def debt_rating(ticker_text):
    ticker = Ticker(ticker_text)
    try:
        de_ratio = ticker.financial_data[ticker_text]["debtToEquity"] / 100
    except KeyError:
        return 0
    if de_ratio < 0.25:
        return 5
    elif de_ratio < 0.5:
        return 4
    elif de_ratio < 1:
        return 3
    elif de_ratio < 3:
        return 2
    else:
        return 1


def stability_rating(ohlc_data):
    try:
        data_length = len(ohlc_data.index)
        ohlc_data["Log Returns"] = np.log(
            ohlc_data["Close"] / ohlc_data["Close"].shift(1)
        )
        volatility = ohlc_data["Log Returns"].std() * np.sqrt(data_length)
    except:
        return 0
    if volatility < 0.3:
        return 5
    elif volatility < 0.4:
        return 4
    elif volatility < 0.6:
        return 3
    elif volatility < 0.7:
        return 2
    else:
        return 1


def dividend_rating(ticker_text):
    ticker = Ticker(ticker_text)
    try:
        dividend_yield = (
            ticker.summary_detail[ticker_text]["trailingAnnualDividendYield"] * 100
        )
    except KeyError:
        return 0
    if dividend_yield > 5:
        return 5
    elif dividend_yield > 3:
        return 4
    elif dividend_yield > 2:
        return 3
    elif dividend_yield > 1:
        return 2
    elif dividend_yield > 0:
        return 1
    else:
        return 0


def future_rating(ticker_text):

    ticker = Ticker(ticker_text)
    try:
        forward_eps = ticker.key_stats[ticker_text]["forwardEps"]
    except KeyError:
        return 0
    if forward_eps > 15:
        return 5
    elif forward_eps > 12:
        return 4
    elif forward_eps > 8:
        return 3
    elif forward_eps > 4:
        return 2
    else:
        return 1


def check_all(ticker_text):

    price_data = yf.download(
        tickers=ticker_text, interval="1d", period="1y", prepost=False, threads=True,
    )
    price_data = price_data.reset_index()

    value = value_rating(ticker_text)
    debt = debt_rating(ticker_text)
    stability = stability_rating(price_data)
    dividend = dividend_rating(ticker_text)
    future = future_rating(ticker_text)

    list = [value, debt, stability, dividend, future]

    print(list)

    return True

