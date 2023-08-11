# ![T logo](https://github.com/Ravdar/tickery/assets/97836782/096e1d4b-c95f-4019-b15b-f3de0054ed65) Tickery: Stock Analysis Dashboard

Tickery is a Python-based web application built with Plotly Dash that allows users to analyze stock data for a given company. The application provides comprehensive insights into price data, technical indicators, financial statements, and statistical analysis. Whether you're a trader, investor, or simply curious about stock trends, Tickery has something to offer.


https://github.com/Ravdar/tickery/assets/97836782/34ba3dab-bea8-4229-98d8-76ea3c5f03db

For a more detailed video with my commentary, click [here.](https://www.youtube.com/watch?v=VewCNybNQKE)

# Features

Tickery offers a variety of features to assist users in effectively analyzing stock data. These features are categorized into four areas:

## 1. Summary
The Summary tab provides basic information about the selected company's price data and overall stock rating. The stock is rated on a 5-point scale, offering a quick overview of its performance.
## 2. Main chart
In the Main Chart tab, users can perform in-depth analysis of price data. Key features include:

* Selecting a specific time period for analysis.
* Utilizing technical indicators such as Bollinger Bands, MACD, and stochastic indicators.
## 3. Financials
The Financials tab presents essential financial statements for the company:

* Balance Sheet
* Income Statement
* Cash Flow

Users can visualize the data as bar charts, enhancing their understanding of the company's financial health.
## 4. Statistics
The Statistics tab offers advanced analytical tools:

* Linear regression and correlation with the S&P 500 index.
* Customizable Monte Carlo simulation for risk assessment.
* Value at Risk (VaR) and Conditional Value at Risk (CVaR) data.
* Return distribution histogram.
* Percentage returns linear chart.

# Screenshots
![tickery - summary](https://github.com/Ravdar/tickery/assets/97836782/1c0e492c-cc8c-4d67-930b-6ff6b32762ad)
![tickery - main chart](https://github.com/Ravdar/tickery/assets/97836782/2b286c22-6af8-400e-8fcb-6f4799b8e22e)
![tickery - financials](https://github.com/Ravdar/tickery/assets/97836782/df081388-8879-481d-9af1-f83785d4420c)
![tickery - statistics](https://github.com/Ravdar/tickery/assets/97836782/94515924-6978-4e6d-b573-4f1b6b53c1e0)


# Installation
1. Clone the repository:
```git clone https://github.com/Ravdar/tickery```
2. Install the required libraries:
```pip install -r requirements.txt```
3. Run the application:
```python main.py```
4. Access the app in your web browser at **http://localhost:1023**

# Used libraries
* pandas
* numpy
* scipy
* yfinance
* yahooquery
* matplotlib
* plotly
