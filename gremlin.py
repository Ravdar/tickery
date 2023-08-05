import datetime
from datetime import date, timedelta

import dash
import dash_bootstrap_components as dbc
from dash import dash_table
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from yahooquery import Ticker
from find_image import find_logo

from radar_ratings import (
    value_rating,
    debt_rating,
    stability_rating,
    dividend_rating,
    future_rating,
)

from utils import (
    add_indicator_button,
    prepare_price_statistics,
    get_linear_regression_params,
    get_percentage_returns_statistics,
    format_table_data,
    prepare_distribution_and_price_data,
    prepare_summary_tab_data,
    historical_and_parametric_var_and_cvar,
    datatable_settings_multiindex,
    monte_carlo_simulation,
    monte_carlo_statistics,
)

from indicators import add_moving_average, add_bollinger_bands, add_stochastic, add_macd

# Declaring constant variables
INTERVALS = ["1d", "1m", "1mo", "1wk", "3mo", "5m", "15m", "30m", "60m", "90m"]
INDICATORS = ["Moving average", "Bollinger Bands", "MACD", "Stochastic"]
ticker = pd.DataFrame(columns=["Datetime", "Open", "High", "Low", "Close", "Adj Close"])
TODAY_DATE = pd.Timestamp.now()
WEEK_AGO = pd.to_datetime(datetime.datetime.now() - timedelta(weeks=1))
GREEN = "#00b51a"
RED = "#ff2d21"
BG_COLOR = "#211F32"

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, "assets/styles.css"])

# Main layout
app.layout = html.Div(
    id="main_container",
    className="main-container",
    children=[
        html.Div(
            className="main-logo-container",
            children=[
                html.Img(
                    src="assets/tickerynet.png", alt="image", className="main-logo"
                ),
            ],
        ),
        html.P(
            "Explore the world of stocks",
            style={"text-align": "center", "color": "white"},
        ),
        html.Div(
            dcc.Input(
                id="input_ticker".format("search"),
                type="search",
                placeholder="Type ticker".format("search"),
                className="search-bar",
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
                            className="main-tab",
                            selected_className="main-selected-tab",
                        ),
                        dcc.Tab(
                            label="Chart",
                            value="main_chart_tab",
                            className="main-tab",
                            selected_className="main-selected-tab",
                        ),
                        dcc.Tab(
                            label="Financials",
                            value="financials_tab",
                            className="main-tab",
                            selected_className="main-selected-tab",
                        ),
                        dcc.Tab(
                            label="Statistics",
                            value="statistics_tab",
                            className="main-tab",
                            selected_className="main-selected-tab",
                        ),
                    ],
                    parent_className="main-tabs",
                    className="main-tabs-container",
                    style={"display": "none"},
                )
            ],
        ),
        html.H5(
            "Nothing is here yet, type stock ticker to start",
            className="welcome-message",
            id="welcome_message",
        ),
        html.Div(id="tabs_content"),
    ],
)


# SHORT INFO


@app.callback(
    Output("welcome_message", "children"),
    Output("welcome_message", "style"),
    Output("main_tabs", "style"),
    Output("short_info_container", "children"),
    Input("input_ticker", "value"),
)
def show_info(ticker_text):
    """Displaying basic data of stock based on provided ticker"""

    empty = "Nothing is here yet, type stock ticker to start"
    not_found = "We couldn't find your ticker :( Correct it and try again"
    style = {
        "color": "white",
        "margin-top": "150px",
        "justify-content": "center",
        "display": "flex",
        "font-size": "60px",
        "text-align": "center",
    }

    # Validation of ticker - returning according communicates
    if ticker_text:
        ticker = yf.Ticker(ticker_text)
        ticker_yq = Ticker(ticker_text, validate=True)
        validation = ticker_yq.symbols
    else:
        return empty, style, {"display": "none"}, None

    if validation == []:
        return not_found, style, {"display": "none"}, None

    # Collecting the data
    name = ticker.info["shortName"]
    currency = ticker.info["currency"]
    logo_url = find_logo(ticker_text)
    industry = (ticker.info["industry"]).replace("—", " ")
    exchange = ticker_yq.price[ticker_text]["exchangeName"]
    if exchange == "NasdaqGS":
        exchange = "Nasdaq"
    history = ticker.history(period="1m")
    last_price = round(history["Close"].iloc[-1], 2)
    prev_close = round(ticker.info["previousClose"], 2)
    change = round(last_price - prev_close, 2)

    # Change of price change labels colors whether is it up or down
    if change >= 0:
        change = f"+{change}"
        perc_change = f"+{round(((last_price - prev_close) / prev_close * 100),2)}%"
        font_color = GREEN
    else:
        change = f"{change}"
        perc_change = f"{round(((last_price - prev_close) / prev_close * 100),2)}%"
        font_color = RED

    content = (
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
                                    className="logo-img",
                                )
                            ],
                            className="logo-column",
                        ),
                        dbc.Col(
                            [
                                html.Div(
                                    children=[
                                        html.H1(name, className="company-name",),
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
                                            className="company-name",
                                        ),
                                    ]
                                ),
                                html.H5(industry, className="industry-and-exchange",),
                                html.H5(exchange, className="industry-and-exchange",),
                            ],
                            style={},
                        ),
                    ],
                    align="start",
                )
            ],
            className="short-info-container",
        ),
    )

    return content


# TABS
@app.callback(
    Output("tabs_content", "children"),
    Input("main_tabs", "value"),
    Input("input_ticker", "value"),
)
def render_tab(tab, ticker_text):
    """Displays content depending on selected tab"""

    if ticker_text == "":
        return None
    # Summary
    elif tab == "summary_tab":
        return html.Div(
            id="summary_container", children=[], className="summary-container",
        )
    # Chart tab
    elif tab == "main_chart_tab":
        return html.Div(
            id="main_chart_container",
            children=[
                html.Div(
                    children=[
                        dcc.Dropdown(
                            options=[{"label": i, "value": i} for i in INTERVALS],
                            id="interval_dropdown",
                            placeholder="Interval",
                            className="chart-dropdowns",
                        ),
                        dcc.Dropdown(
                            options=[{"label": i, "value": i} for i in INDICATORS],
                            id="indicator_dropdown",
                            placeholder="Indicators",
                            className="chart-dropdowns",
                        ),
                        dcc.DatePickerRange(
                            id="chart_date_picker",
                            min_date_allowed=date(1900, 1, 1,),
                            max_date_allowed=date(
                                TODAY_DATE.year, TODAY_DATE.month, TODAY_DATE.day
                            ),
                            initial_visible_month=date(
                                WEEK_AGO.year, WEEK_AGO.month, WEEK_AGO.day
                            ),
                            end_date=date(
                                TODAY_DATE.year, TODAY_DATE.month, TODAY_DATE.day
                            ),
                            className="chart-date-picker",
                        ),
                        dcc.Dropdown(
                            options=[
                                {"label": "Linear", "value": "linear"},
                                {"label": "Logarithmic", "value": "log"},
                            ],
                            id="scale_dropdown",
                            placeholder="Scale",
                            value="linear",
                            className="chart-dropdowns",
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
                            className="chart-dropdowns",
                        ),
                    ],
                    className="main-chart-container",
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
                            "ma", "Moving average", "", "Period", 0, 0, "none", "none",
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
                    className="modals-and-stats",
                ),
                html.Div(
                    id="stats_container", children=[], className="modals-and-stats",
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
                            margin=go.layout.Margin(l=40, r=40, b=5, t=5,),
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor=BG_COLOR,
                        ),
                    ),
                    className="main-chart",
                ),
                html.Div(id="stoch_container", children=[],),
                html.Div(id="macd_container", children=[],),
            ],
        )
    # Financials
    elif tab == "financials_tab":
        return html.Div(
            id="financials_tabs_container",
            children=[
                html.Div(
                    children=[
                        dcc.Tabs(
                            id="financials_sub_tab",
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
                            className="financials-sub-tab",
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
                            className="qora-tabs",
                        ),
                    ],
                    className="financials-tabs-container",
                ),
                html.Div(
                    id="financials_container",
                    children=[],
                    style={"backgroundColor": BG_COLOR},
                ),
            ],
        )
    # Statistics
    elif tab == "statistics_tab":
        return html.Div(
            id="statistics_container",
            children=[
                html.Div(
                    children=[
                        dcc.DatePickerSingle(
                            id="start_datepicker", placeholder="Start date"
                        ),
                        dcc.DatePickerSingle(
                            id="end_datepicker", placeholder="End date"
                        ),
                    ],
                    className="StatContainer",
                ),
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                dcc.Dropdown(
                                    options=[
                                        {"label": i, "value": i} for i in INTERVALS
                                    ],
                                    id="interval_dropdown_s",
                                    placeholder="Interval",
                                    className="interval-dropdown-s",
                                ),
                            ],
                            className="interval-dd-stat",
                        ),
                        html.Div(
                            dbc.Alert(
                                "Invalid data range. Please be aware that for shorter intervals, only the data from the past 7 days is available.",
                                id="error_alert_s",
                                color="danger",
                                dismissable=True,
                                is_open=False,
                                duration=5500,
                            ),
                            style={"display": "flex", "justify-content": "center"},
                        ),
                    ],
                    style={"margin-bottom": "40px"},
                ),
                html.Div(id="statistics_container2"),
            ],
            style={"backgroundColor": BG_COLOR},
        )


# SUMMARY TAB
@app.callback(
    Output("summary_container", "children", allow_duplicate=True),
    [Input("input_ticker", "value"), Input("main_tabs", "value"),],
    prevent_initial_call=True,
)
def update_summary(ticker_text, tab):
    """Returns content for  Summary tab based on provided ticker: simple price chart, radar chart and some statistics"""

    if ticker_text == "":
        return None

    validation = Ticker(ticker_text, validate=True).symbols
    if validation == []:
        return None

    current_year = int(TODAY_DATE.strftime("%Y"))
    if tab == "summary_tab" and ticker_text is not None:
        summary_tab_data = prepare_summary_tab_data(ticker_text)
        price_data = summary_tab_data["Price data"]
        line_color = summary_tab_data["Line color"]

        # Simple price chart
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
                    margin=go.layout.Margin(l=40, r=0, b=5, t=40,),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                ),
            ),
            className="simple-price-graph",
        )

        # Slider for simple price chart
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
                    id="range_slider",
                    className="range-slider",
                    disabled=False,
                )
            ],
            width=8,
        )

        # Calculating rates for company condition radar chart
        value = value_rating(ticker_text)
        debt = debt_rating(ticker_text)
        stability = stability_rating(price_data)
        dividend = dividend_rating(ticker_text)
        future = future_rating(ticker_text)

        # Formatting chart color depending on company condition
        ratings = [value, debt, stability, dividend, future]
        ratings_sum = sum(ratings)
        if ratings_sum >= 15:
            inside_color = "rgb(0,181,26)"
        elif ratings_sum >= 7:
            inside_color = "rgb(255,255,0)"
        else:
            inside_color = "rgb(255,45,33)"

        # Radar chart
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
            className="radar-chart",
        )

    # Basic price data statistics
    period = 52
    period_change = summary_tab_data["Period change"]
    period_max = summary_tab_data["Period max"]
    period_min = summary_tab_data["Period min"]
    max_gain = summary_tab_data["Max gain"]
    max_surge = summary_tab_data["Max surge"]

    infos = html.Div(
        id="infos_container",
        children=[
            html.H5(f"{period} Week change: {period_change}%", className="stat-labels"),
            html.H5(f"{period} Week max: {period_max}", className="stat-labels"),
            html.H5(f"{period} Week min: {period_min}", className="stat-labels"),
            html.H5(f"{period} Week max gain: {max_gain}%", className="stat-labels"),
            html.H5(f"{period} Week max surge: {max_surge}%", className="stat-labels"),
        ],
        className="stat-container",
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
        Output("simple_price_chart", "figure"),
        Output("range_slider", "value"),
        Output("infos_container", "children"),
    ],
    Input("range_slider", "value"),
    [State("price_graph_col", "children"), State("input_ticker", "value")],
    State("infos_container", "children"),
)
def update_simple_chart(year, graph, ticker_text, infos):
    """Updates simple price chart and basic price statistics based on range slider value, also limits range slider range"""

    # Block first dot of rangeslider to always remains as current year
    if year[1] != 4:
        return graph, [year[0], 4], infos
    # Block second dot of rangeslider never remains as current year
    if year[0] == 4:
        return graph, [3, 4], infos

    year_list = [4, 3, 2, 1, 0]
    year_rv = year[0]
    year_rv = year_list[year_rv]

    period = 52 * (year_rv)

    summary_tab_data = prepare_summary_tab_data(ticker_text, year_rv)
    price_data = summary_tab_data["Price data"]
    line_color = summary_tab_data["Line color"]

    # Updated figure for simple price chart
    figure = go.Figure(
        data=[
            go.Scatter(
                x=price_data["Date"], y=price_data["Close"], line={"color": line_color},
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
            margin=go.layout.Margin(l=40, r=40, b=5, t=40,),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        ),
    )

    # Update of basic price statistic
    period_change = summary_tab_data["Period change"]
    period_max = summary_tab_data["Period max"]
    period_min = summary_tab_data["Period min"]
    max_gain = summary_tab_data["Max gain"]
    max_surge = summary_tab_data["Max surge"]

    infos = [
        html.H5(f"{period} Week change: {period_change}%", className="stat-labels"),
        html.H5(
            f"{period} Week max: {period_max}",
            style={"color": "white", "margin-right": "20px",},
        ),
        html.H5(f"{period} Week min: {period_min}", className="stat-labels"),
        html.H5(f"{period} Week max gain: {max_gain}%", className="stat-labels"),
        html.H5(f"{period} max surge: {max_surge}%", className="stat-labels"),
    ]

    return figure, year, infos


# CHART TAB


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
    """Displays modal window for input of indicator settings"""

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
def add_ma(n_clicks):
    """After confirming settings in modal window, clears indicator dropdown and adds moving button and its clear button"""

    if n_clicks != None:
        n_clicks = None
        return (
            None,
            {
                "display": "flex",
                "margin-right": "0px",
                "padding": "5px",
                "background-color": BG_COLOR,
                "font-size": "12px",
            },
            {
                "display": "flex",
                "margin-left": "0px",
                "padding": "5px",
                "background-color": BG_COLOR,
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
def add_bb(n_clicks):
    """After confirming settings in modal window, clears indicator dropdown and adds bollinger bands button and its clear button"""

    if n_clicks != None:
        n_clicks = None
        return (
            None,
            {
                "display": "flex",
                "margin-right": "0px",
                "padding": "5px",
                "background-color": BG_COLOR,
                "font-size": "12px",
            },
            {
                "display": "flex",
                "margin-left": "0px",
                "padding": "5px",
                "background-color": BG_COLOR,
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
def add_st(n_clicks):
    """After confirming settings in modal window, clears indicator dropdown and adds stochastic button and its clear button"""

    if n_clicks != None:
        return (
            None,
            {
                "display": "flex",
                "margin-right": "0px",
                "padding": "5px",
                "background-color": BG_COLOR,
                "font-size": "12px",
            },
            {
                "display": "flex",
                "margin-left": "0px",
                "padding": "5px",
                "background-color": BG_COLOR,
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
def add_macd(n_clicks):
    """After confirming settings in modal window, clears indicator dropdown and adds MACD button and its clear button"""

    if n_clicks != None:
        return (
            None,
            {
                "display": "flex",
                "margin-right": "0px",
                "padding": "5px",
                "background-color": BG_COLOR,
                "font-size": "12px",
            },
            {
                "display": "flex",
                "margin-left": "0px",
                "padding": "5px",
                "background-color": BG_COLOR,
                "font-size": "12px",
            },
        )


# CHART BUTTONS PART

# Moving Average
@app.callback(Output("ma_modal", "is_open"), Input("ma_button", "n_clicks"))
def show_ma_modal(n_clicks):
    """Shows modal window again after clicking moving average button"""
    if n_clicks != None:
        n_clicks = None
        return True
    else:
        return False


@app.callback(
    [Output("ma_button", "n_clicks"), Output("ma_button", "children")],
    Input("ma_ok", "n_clicks"),
    [State("ma_param1", "value"), State("ma_button", "children")],
)
def update_indicator(n_clicks, indicator_param1, indicator_name):
    """Updates indiactor settings"""
    if n_clicks != None:
        button_value = f"{indicator_name[:14]}({indicator_param1})"
        n_clicks = None
        return None, button_value


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
    """After clicking "X" button, deletes indicator from chart, indicator button and clear button"""
    if n_clicks != None:
        return {"display": "none"}, {"display": "none"}, None


# Bollinger Bands
@app.callback(Output("bb_modal", "is_open"), Input("bb_button", "n_clicks"))
def show_bb_modal(n_clicks):
    """Shows modal window again after clicking bollinger bands button"""
    if n_clicks != None:
        n_clicks = None
        return True
    else:
        return False


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
    """Updates indiactor settings"""
    if n_clicks != None:
        button_value = f"{indicator_name[:15]}({indicator_param1}, {indicator_param2})"
        n_clicks = None
        return None, button_value


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
    """After clicking "X" button, deletes indicator from chart, indicator button and clear button"""
    if n_clicks != None:
        return {"display": "none"}, {"display": "none"}, None


# Stochastic
@app.callback(Output("st_modal", "is_open"), Input("st_button", "n_clicks"))
def show_st_modal(n_clicks):
    """Shows modal window again after clicking stochastic button"""
    if n_clicks != None:
        n_clicks = None
        return True
    else:
        return False


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
    """Updates indiactor settings"""
    if n_clicks != None:
        button_value = f"{indicator_name[:10]}({indicator_param1}, {indicator_param2})"
        n_clicks = None
        return None, button_value


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
    """After clicking "X" button, deletes indicator from chart, indicator button and clear button"""
    if n_clicks != None:
        n_clicks = None
        return {"display": "none"}, {"display": "none"}, [], None


# MACD
@app.callback(Output("macd_modal", "is_open"), Input("macd_button", "n_clicks"))
def show_macd_modal(n_clicks):
    """Shows modal window again after clicking MACD button"""
    if n_clicks != None:
        n_clicks = None
        return True
    else:
        return False


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
    """Updates indiactor settings"""
    if n_clicks != None:
        button_value = f"{indicator_name[:4]}({indicator_param1}, {indicator_param2})"
        n_clicks = None
        return None, button_value


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
    """After clicking "X" button, deletes indicator from chart, indicator button and clear button"""
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
        Output("stats_container", "children"),
    ],
    [
        Input("input_ticker", "value"),
        Input("interval_dropdown", "value"),
        Input("chart_date_picker", "start_date"),
        Input("chart_date_picker", "end_date"),
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
    """Draws charts based on the multiple settings provided by user"""
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

    if ticker.empty:
        return init_figure, True, stoch, macd, None

    ticker = ticker.reset_index()

    # Stats
    stats = prepare_price_statistics(ticker)

    # Setting x axis labels number
    length_df = len(ticker.index)
    if length_df < 25:
        tick_indices = [i for i in range(0, length_df, 1)]
    else:
        tick_indices = [i for i in range(0, length_df, length_df // 10)]
    tick_values = ticker.index[tick_indices]

    # Converting x-axis labels based on interval (date type)
    if ticker.columns[0] == "Datetime":
        ticktext = [str(val)[:19] for val in ticker.iloc[tick_indices, 0]]
        # Dropping last row beacuse it is called incorrectly for some reason
        if str(ticker.iloc[-1, 0])[:19] != str(ticker.iloc[-2, 0])[:19]:
            ticker = ticker[:-1]

    else:
        ticktext = [str(val)[:10] for val in ticker.iloc[tick_indices, 0]]

    # Creating figure based on provided chart type
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

    # Add MACD to the plot if selected
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

    # Moving x axis labels to the bottom of all charts
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

    # Constructing final figure
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
            margin=go.layout.Margin(l=40, r=40, b=5, t=5,),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        ),
    )

    return fig, False, stoch, macd, stats


# FINANCIALS TAB
@app.callback(
    Output("financials_container", "children"),
    [
        Input("input_ticker", "value"),
        Input("main_tabs", "value"),
        Input("financials_sub_tab", "value"),
        Input("qora_tabs", "value"),
    ],
)
def update_financials(ticker_text, tab1, tab2, tab3):
    """Returns table with financial data of selected settings"""

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

        table_data = format_table_data(table_data, frequency)

        initial_active_cell = {"row": 0, "column": 0, "column_id": "0", "row_id": 0}

        table = dash_table.DataTable(
            id="financials_table",
            data=table_data.to_dict("records"),
            active_cell=initial_active_cell,
            style_table={
                "maxWidth": "700px",
                "marginLeft": "auto",
                "marginRight": "auto",
            },
            style_cell={
                "whiteSpace": "normal",
                "textAlign": "center",
                "color": "white",
                "backgroundColor": BG_COLOR,
                "fontFamily": "Lato",
                "fontSize": "14px",
                "padding": "10px",
            },
            style_header={"fontWeight": "bold", "border": "1px blue"},
            style_data_conditional=[
                {"if": {"column_id": table_data.columns[0]}, "fontWeight": "bold",}
            ],
        )

        return html.Div(
            children=[html.Div(id="graph_container", children=[]), table],
            style={"text-align": "center", "backgroundColor": BG_COLOR},
        )


@app.callback(
    Output("graph_container", "children"),
    Input("financials_table", "active_cell"),
    State("financials_table", "data"),
)
def cell_clicked(active_cell, table):
    """Returns bar chart of financial data table selected position"""

    if active_cell is None:
        return None

    row = active_cell["row"]
    value = table[row][""]
    x_data = list(table[row].keys())
    y_data = list(table[row].values())

    fig = dcc.Graph(
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
                "xaxis": {"color": "white", "tickvals": x_data,},
                "yaxis": {"color": "white"},
                "plot_bgcolor": BG_COLOR,
                "paper_bgcolor": BG_COLOR,
            },
        },
    )

    return fig


# STATISTICS TAB
@app.callback(
    Output("statistics_container2", "children"),
    Output("error_alert_s", "is_open"),
    [
        Input("input_ticker", "value"),
        Input("main_tabs", "value"),
        Input("start_datepicker", "date"),
        Input("end_datepicker", "date"),
        Input("interval_dropdown_s", "value"),
    ],
)
def update_statistics(ticker_text, tab, start_date, end_date, interval):
    """Loads graphs and statistics of stock into statistics tab container, based on ticker and time range provided by user"""
    if tab == "statistics_tab":

        if None in (ticker_text, start_date, end_date, interval):
            return None, False

        data_for_distribution_and_price_charts = prepare_distribution_and_price_data(
            ticker_text, interval, start_date, end_date
        )
        price_data = data_for_distribution_and_price_charts["Price data"]
        x_values = data_for_distribution_and_price_charts["x values"]
        distribution_data = data_for_distribution_and_price_charts["Distribution data"]

        linear_regression_params = get_linear_regression_params(
            ticker_text, interval, start_date, end_date
        )
        returns = linear_regression_params["Returns"]
        correlation = linear_regression_params["Correlation"]
        trend = linear_regression_params["Trend"]

        percentage_returns_statistics = get_percentage_returns_statistics(price_data)

        stats_list = []

        # Preparing container with returns statistics
        for key in percentage_returns_statistics.keys():
            stat_label = html.H5(
                children=f"{key}: {percentage_returns_statistics[key]}",
                className="returns-stats-labels",
            )
            stats_list.append(stat_label)

        stats_container = html.Div(
            children=stats_list, className="returns-stats-container"
        )

        # Linear regression chart
        linear_regression_fig = dcc.Graph(
            id="linear_regression_chart",
            className="linear-regression-chart",
            figure={
                "data": [
                    {
                        "name": ticker_text,
                        "x": returns["SPY"],
                        "y": returns[ticker_text],
                        "mode": "markers",
                        "marker": {"color": "#3ad1b8"},
                    },
                    {
                        "name": "Trend",
                        "x": returns[ticker_text],
                        "y": trend,
                        "marker": {"color": "magenta"},
                    },
                ],
                "layout": {
                    "title": "Linear regression",
                    "titlefont": {"color": "white"},
                    "legend": {"font": {"color": "white"}},
                    "xaxis": {"color": "white", "title": ticker_text},
                    "yaxis": {"color": "white", "title": "S&P500"},
                    "plot_bgcolor": BG_COLOR,
                    "paper_bgcolor": BG_COLOR,
                },
            },
        )

        # Percentage returns chart
        percentage_returns_fig = dcc.Graph(
            id="percentage-returns-chart",
            className="percentage-returns-chart",
            figure={
                "data": [
                    {
                        "x": x_values,
                        "y": price_data["Daily returns"],
                        "line": {"color": "#3ad1b8"},
                    }
                ],
                "layout": go.Layout(
                    title="Percentage returns",
                    titlefont={"color": "white"},
                    xaxis={"color": "white", "dtick": len(x_values) // 10},
                    yaxis={"color": "white"},
                    plot_bgcolor=BG_COLOR,
                    paper_bgcolor=BG_COLOR,
                    margin=go.layout.Margin(r=0, t=25, b=25, l=0),
                ),
            },
        )

        # Distribution chart
        distribution_fig = dcc.Graph(
            id="distribution-chart",
            className="distribution-chart",
            figure={
                "data": [
                    {
                        "x": distribution_data.index,
                        "y": distribution_data["Counted returns"],
                        "type": "histogram",
                        "marker": {"color": "#3ad1b8"},
                    }
                ],
                "layout": go.Layout(
                    title="Return distributions",
                    titlefont={"color": "white"},
                    xaxis={"color": "white"},
                    yaxis={"color": "white"},
                    plot_bgcolor=BG_COLOR,
                    paper_bgcolor=BG_COLOR,
                    margin=go.layout.Margin(r=0, t=30),  # Set the desired margin values
                ),
            },
        )

        # VaR and CVaR data
        var = historical_and_parametric_var_and_cvar(price_data)
        data = {
            ("VaR (%)", "Historical"): [
                var["Historical"]["VaR"]["95"],
                var["Historical"]["VaR"]["99"],
                var["Historical"]["VaR"]["99.9"],
            ],
            ("VaR (%)", "Parametric"): [
                var["Parametric"]["VaR"]["95"],
                var["Parametric"]["VaR"]["99"],
                var["Parametric"]["VaR"]["99.9"],
            ],
            ("CVaR (%)", "Historical"): [
                var["Historical"]["CVaR"]["95"],
                var["Historical"]["CVaR"]["99"],
                var["Historical"]["CVaR"]["99.9"],
            ],
            ("CVaR (%)", "Parametric"): [
                var["Parametric"]["CVaR"]["95"],
                var["Parametric"]["CVaR"]["99"],
                var["Parametric"]["CVaR"]["99.9"],
            ],
        }

        # Convert data to DataFrame
        df = pd.DataFrame(data)
        df.index = ["95%", "99%", "99.9%"]
        df.index.name = "Confidence level"

        df.reset_index(inplace=True)

        df_columns, df_data = datatable_settings_multiindex(df)

        var_table = dash_table.DataTable(
            id="var-table",
            columns=df_columns,
            data=df_data,
            merge_duplicate_headers=True,
            style_table={
                "maxWidth": "700px",
                "marginLeft": "auto",
                "marginRight": "auto",
            },
            style_cell={
                "whiteSpace": "normal",
                "textAlign": "center",
                "color": "white",
                "backgroundColor": BG_COLOR,
                "fontFamily": "Lato",
                "fontSize": "20px",
                "padding": "20px",
            },
            style_header={"fontWeight": "bold", "border": "1px blue"},
            style_data={"minHeight": "50px",},
        )

        # Monte Carlo
        simulations_traces = []

        # Creating an empty graph
        monte_carlo_graph = dcc.Graph(
            id="monte_carlo_graph",
            figure=go.Figure(
                data=simulations_traces,
                layout=go.Layout(
                    showlegend=False,
                    title="",
                    yaxis=dict(
                        autorange=True,
                        title="Price",
                        titlefont=dict(color="white"),
                        tickfont=dict(color="white"),
                        gridcolor="grey",
                    ),
                    margin=go.layout.Margin(r=5, t=5,),
                    xaxis_rangeslider_visible=False,
                    xaxis=dict(
                        autorange=True,
                        title="Days",
                        titlefont=dict(color="white"),
                        tickfont=dict(color="white"),
                        gridcolor="grey",
                    ),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                ),
            ),
            className="monte-carlo-graph",
        )
        # Creating an empty container for monte carlo statistics
        monte_carlo_stats_container = html.Div(
            id="monte_carlo_stats_container", children=[]
        )

        # Final layout of elements in statistics tab
        final_layout = html.Div(
            id="stat-1-div",
            className="stat-1-div",
            children=[
                html.Div(
                    id="stat-2-div-upper",
                    className="stat-2-div",
                    children=[
                        html.Div(
                            id="regression_and_var_div",
                            className="stat-3-div",
                            children=[linear_regression_fig],
                        ),
                        html.Div(
                            id="monte_carlo_div",
                            className="stat-3-div",
                            children=[
                                html.Div(
                                    id="monte_carlo_menu",
                                    className="monte-carlo-menu",
                                    children=[
                                        html.H5(
                                            children=["Monte Carlo simulation"],
                                            className="monte-carlo-title",
                                        ),
                                        html.Div(
                                            id="monte-carlo-buttons-div",
                                            className="monte-carlo-buttons-div",
                                            children=[
                                                dcc.Input(
                                                    id="mc_no_simulations_input",
                                                    className="no-simulations-input",
                                                    placeholder="Number of simulations",
                                                ),
                                                dcc.Input(
                                                    id="mc_simulated_period_input",
                                                    className="simulated-period-input",
                                                    placeholder="Simulated period",
                                                ),
                                                html.Div(
                                                    dbc.Button(
                                                        "Run simulation",
                                                        id="mc_run_simulation_button",
                                                        className="run-simulation-button",
                                                    )
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                                monte_carlo_graph,
                            ],
                        ),
                    ],
                ),
                dbc.Row(
                    className="correlation-and-monte-carlo-row",
                    children=[
                        dbc.Col(
                            className="correlation-and-monte-carlo-col",
                            children=[
                                html.H5(
                                    children=[
                                        f"Correlation with S&P500 index: {round(correlation.iloc[0, 1],2)}"
                                    ],
                                    className="correlation-label",
                                )
                            ],
                        ),
                        dbc.Col(
                            className="correlation-and-monte-carlo-row",
                            children=[monte_carlo_stats_container],
                        ),
                    ],
                ),
                html.Div(
                    id="stat-2-div-lower",
                    className="stat-2-div",
                    children=[
                        html.Div(children=[var_table], style={"margin-top": "40px"}),
                        distribution_fig,
                    ],
                ),
                html.Div(className="stat-2-div", children=percentage_returns_fig),
                html.Div(className="stat-2-div", children=stats_container,),
            ],
        )

    return (
        final_layout,
        False,
    )


@app.callback(
    Output("monte_carlo_graph", "figure"),
    Output("monte_carlo_stats_container", "children"),
    Input("mc_run_simulation_button", "n_clicks"),
    State("mc_no_simulations_input", "value"),
    State("mc_simulated_period_input", "value"),
    State("input_ticker", "value"),
    State("start_datepicker", "date"),
    State("end_datepicker", "date"),
    State("interval_dropdown_s", "value"),
)
def run_simulation(
    n_clicks,
    number_of_simulations,
    simulated_period,
    ticker,
    start_date,
    end_date,
    interval,
):
    """Utilizing the given simulation count and period, the Python function conducts a Monte Carlo simulation. The results are graphed, and key statistics are computed and presented, offering insights into the simulation's outcome."""

    if n_clicks is None:
        return None
    else:
        data_for_distribution_and_price_charts = prepare_distribution_and_price_data(
            ticker, interval, start_date, end_date
        )
        price_data = data_for_distribution_and_price_charts["Price data"]
        initial_price = price_data["Close"].iloc[-1]
        monte_carlo_data = monte_carlo_simulation(
            price_data, int(number_of_simulations), int(simulated_period)
        )

        simulated_prices = []
        simulated_traces = []

        # Collecting traces and prices into the lists
        for simulation in range(int(number_of_simulations)):
            prices = monte_carlo_data[:, simulation]
            trace = go.Scatter(y=prices, mode="lines")
            simulated_prices.append(prices)
            simulated_traces.append(trace)

        # Updating chart figure with simulated traces
        fig = go.Figure(
            data=simulated_traces,
            layout=go.Layout(
                showlegend=False,
                title="",
                yaxis=dict(
                    autorange=True,
                    title="Price",
                    titlefont=dict(color="white"),
                    tickfont=dict(color="white"),
                    gridcolor="grey",
                ),
                margin=go.layout.Margin(r=5, t=5,),
                xaxis_rangeslider_visible=False,
                xaxis=dict(
                    autorange=True,
                    title="Days",
                    titlefont=dict(color="white"),
                    tickfont=dict(color="white"),
                    gridcolor="grey",
                ),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
            ),
        )

        monte_carlo_stats = monte_carlo_statistics(simulated_prices, initial_price)

        monte_carlo_stats_list = []

        # Filling statistics container with statistic labels and values
        for key in monte_carlo_stats.keys():
            monte_carlo_stats_label = html.H5(
                children=f"{key}  {monte_carlo_stats[key]}",
                className="monte-carlo-stats-labels",
            )
            monte_carlo_stats_list.append(monte_carlo_stats_label)

        return fig, monte_carlo_stats_list


if __name__ == "__main__":
    app.run_server(debug=True)
