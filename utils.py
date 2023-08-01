import dash_bootstrap_components as dbc
from dash import html
import plotly.express as px
import matplotlib.pyplot as plt
import yfinance as yf
import numpy as np
from scipy.stats import norm
from statistics import mean

GREEN = "#00b51a"
RED = "#ff2d21"


def prepare_summary_tab_data(ticker_text, period=1):
    """Returns data needed for summary tab charts and some stats about price data"""

    price_data = yf.download(
        tickers=ticker_text,
        interval="1d",
        period=f"{period}y",
        prepost=False,
        threads=True,
    )
    price_data = price_data.reset_index()

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
        line_color = GREEN
    else:
        line_color = RED

    return {
        "Price data": price_data,
        "Line color": line_color,
        "Period change": period_change,
        "Period max": period_max,
        "Period min": period_min,
        "Max gain": max_gain,
        "Max surge": max_surge,
    }


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


def format_table_data(table_data, frequency):
    """Formats a financial data to the format matching Dash Table"""

    table_data.reset_index(inplace=True)
    table_data = table_data.transpose()
    table_data.reset_index(inplace=True)
    table_data.drop(0, 0, inplace=True)

    table_data.columns = table_data.iloc[0]
    table_data = table_data[1:]

    table_data.index = table_data.iloc[:, 0]
    table_data = table_data.iloc[:, 1:]

    rows_to_keep = []
    for i in range(len(table_data)):
        if not all(
            str(cell) == "" or cell == 0 or cell is None for cell in table_data.iloc[i]
        ):
            rows_to_keep.append(i)
    table_data = table_data.iloc[rows_to_keep]
    table_data.dropna(inplace=True)

    table_data.index.name = ""
    table_data.columns.name = "Date"

    columns_to_keep = []
    for x in range(len(table_data.columns)):
        if table_data.iloc[0, x] != "TTM":
            columns_to_keep.append(x)
    table_data = table_data.iloc[:, columns_to_keep]

    table_data.drop(table_data.index[1], 0, inplace=True)
    table_data.drop(table_data.index[0], 0, inplace=True)

    length = len(table_data.index)
    width = len(table_data.columns)

    for l in range(length):
        for w in range(width):
            if type(table_data.iloc[l, w]) == float:
                table_data.iloc[l, w] = format(table_data.iloc[l, w], ",")

    new_columns = []
    for x in range(len(table_data.columns)):
        if frequency == "a":
            new_label = str(table_data.columns[x])[:7]
        elif frequency == "q":
            new_label = str(table_data.columns[x])[:7]
        new_columns.append(new_label)

    table_data.columns = new_columns
    table_data = table_data.iloc[:, -4:]
    # # Deleting "EBITDA", it is always nan
    # table_data.drop("EBITDA", inplace=True)
    table_data.reset_index(inplace=True)

    # Formatting table labels text
    for r in range(len(table_data.index)):
        for c in range(len(table_data.columns)):
            new_x = ""
            x = table_data.iloc[r, c]
            for y in range(len(x)):
                if x[y].isupper() and x[y - 1].isupper() == False and y != 0:
                    z = f" {x[y]}"
                    new_x = new_x + z
                else:
                    new_x = new_x + x[y]
            table_data.iloc[r, c] = new_x

    return table_data


def prepare_distribution_and_price_data(ticker_text, interval, start_date, end_date):
    """Downloads price OHLC data for provided ticker, then formats it and calculates values needed for distribution and percentage returns charts"""

    price_data = yf.download(
        tickers=ticker_text,
        interval=interval,
        start=start_date,
        end=end_date,
        prepost=False,
        threads=True,
    )

    if price_data.empty:
        return None, True

    price_data["Daily returns"] = (
        (price_data["Close"] - price_data["Close"].shift(1))
        / price_data["Close"].shift(1)
        * 100
    )
    average_return = price_data["Daily returns"].mean()
    zeros_after_decimal = count_zeros_after_decimal(average_return)
    multiplier = float("0." + "0" * zeros_after_decimal + "5")

    price_data["Rounded daily returns"] = (
        round(price_data["Daily returns"] / multiplier) * multiplier
    )
    price_data["Counted returns"] = None
    for i in range(len(price_data.index)):
        price_data["Counted returns"].iloc[i] = price_data[
            price_data["Rounded daily returns"]
            == price_data["Rounded daily returns"].iloc[i]
        ]["Rounded daily returns"].count()

    distribution_data = price_data.iloc[:, -2:]
    distribution_data.drop_duplicates(subset=["Rounded daily returns"])
    distribution_data = distribution_data.set_index("Rounded daily returns")
    distribution_data.sort_index(inplace=True)

    price_data["Daily log returns"] = round(np.log(1 + price_data["Daily returns"]), 2)

    if price_data.index.name == "Datetime":
        x_values = price_data.index.strftime("%d-%m-%Y %H:%M")
    else:
        x_values = price_data.index.strftime("%d-%m-%Y")

    return {
        "Price data": price_data,
        "x values": x_values,
        "Distribution data": distribution_data,
    }


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
    max_down_candle = (data["Percentage returns"][data["Percentage returns"] > 0]).min()
    min_down_candle = (data["Percentage returns"][data["Percentage returns"] > 0]).min()
    longest_down_streak = calculate_streak(data, False)

    output = {
        "Number of candles": number_of_candles,
        "Number of up candles": number_of_up_candles,
        "Number of down candles": number_of_down_candles,
        "Longest up streak": longest_up_streak,
        "Longest down streak": longest_down_streak,
        "Average candle": f"{round(avg_candle, 2)}%",
        "Biggest candle": f"{round(max_candle, 2)}%",
        "Smallest candle": f"{round(min_candle, 2)}%",
        "Average up candle": f"{round(avg_up_candle, 2)}%",
        "Average down candle": f"{round(avg_down_candle, 2)}%",
        # "Biggest up candle": f"{round(max_up_candle, 2)}%",
        # "Smallest up candle": f"{round(min_up_candle, 2)}%",
        # "Biggest down candle": f"{round(max_down_candle, 2)}%",
        # "Smallest down candle": f"{round(min_down_candle, 2)}%",
    }

    return output


def monte_carlo_simulation(data, number_of_simulations=150, forecast_period=100):
    """Returns numpy array of simulated prices for provided forecast period and number of simulations"""

    returns = data["Close"].pct_change()
    initial_price = data["Close"].iloc[-1]
    average_return = returns.mean()
    return_std = returns.std()

    simulated_prices = np.zeros((forecast_period, number_of_simulations))

    for simulation in range(number_of_simulations):
        prices = [initial_price]
        for x in range(forecast_period):
            daily_return = np.random.normal(average_return, return_std)
            price = prices[-1] * (1 + daily_return)
            prices.append(price)
        simulated_prices[:, simulation] = prices[1:]

    ending_prices = []

    return simulated_prices

def monte_carlo_statistics(simulated_prices, initial_price):
    """Returns basic statistics of provided simulated prices"""

    ending_prices = []

    for simulation in simulated_prices:
        ending_prices.append(simulation[-1])

    max_ending_price = round(max(ending_prices),2)
    min_ending_price = round(min(ending_prices),2)
    average_ending_price = round(mean(ending_prices),2)
    no_ending_price_higher_than_initial = len([price for price in ending_prices if price > initial_price])
    perc_of_ending_price_above_initial = round(no_ending_price_higher_than_initial/len(ending_prices)*100,2)
    perc_of_ending_price_below_initial = 100 - perc_of_ending_price_above_initial

    return {"Max ending price":max_ending_price, "Min ending price":min_ending_price, "Average ending price":average_ending_price, "Perc of ending prices above initial price":f"{perc_of_ending_price_above_initial}%", "Perc of ending prices below initial price":f"{perc_of_ending_price_below_initial}%"}

def historical_and_parametric_var_and_cvar(data):
    """Returns VaR and CVaR for 0.95, 0.99 and 0.999 confidence level both for historical and parametric calculation method"""

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
    p_cvar95 = -(mean_return + (1 - 0.95) ** -1 * norm.pdf(norm.ppf(1 - 0.95)) * std)

    p_var99 = mean_return - norm.ppf(0.99) * std
    p_cvar99 = -(mean_return + (1 - 0.99) ** -1 * norm.pdf(norm.ppf(1 - 0.99)) * std)

    p_var999 = mean_return - norm.ppf(0.999) * std
    p_cvar999 = -(mean_return + (1 - 0.999) ** -1 * norm.pdf(norm.ppf(1 - 0.999)) * std)

    output = {
        "Historical": {
            "VaR": {
                "95": round(var95 * 100, 2),
                "99": round(var99 * 100, 2),
                "99.9": round(var999 * 100, 2),
            },
            "CVaR": {
                "95": round(cvar95 * 100, 2),
                "99": round(cvar99 * 100, 2),
                "99.9": round(cvar999 * 100, 2),
            },
        },
        "Parametric": {
            "VaR": {
                "95": round(p_var95 * 100, 2),
                "99": round(p_var99 * 100, 2),
                "99.9": round(p_var999 * 100, 2),
            },
            "CVaR": {
                "95": round(p_cvar95 * 100, 2),
                "99": round(p_cvar99 * 100, 2),
                "99.9": round(p_cvar999 * 100, 2),
            },
        },
    }

    return output


def datatable_settings_multiindex(df, flatten_char="_"):
    """ Plotly dash datatables do not natively handle multiindex dataframes. 
    This function generates a flattend column name list for the dataframe, 
    while structuring the columns to maintain their original multi-level format.

    Function returns the variables datatable_col_list, datatable_data for the columns and data parameters of
    the dash_table.DataTable"""
    datatable_col_list = []

    levels = df.columns.nlevels
    if levels == 1:
        for i in df.columns:
            datatable_col_list.append({"name": i, "id": i})
    else:
        columns_list = []
        for i in df.columns:
            col_id = flatten_char.join(i)
            datatable_col_list.append({"name": i, "id": col_id})
            columns_list.append(col_id)
        df.columns = columns_list

    datatable_data = df.to_dict("records")

    return datatable_col_list, datatable_data

