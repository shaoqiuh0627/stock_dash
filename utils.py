import json
import math
import matplotlib.pylab as plt
import matplotlib.pyplot as plt
import pandas as pd
import pandas_ta as ta
import requests
from ta.momentum import StochasticOscillator
from ta.trend import MACD
from termcolor import colored as cl
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Getting income statement and balance sheet data
def get_income_balance_sheet(stock):
    income_statement = requests.get(
        f"https://www.alphavantage.co/query?function=INCOME_STATEMENT"
        f"&symbol={stock}&apikey=KYGP0LUFEUKAPRGY"
    )
    income_statement = income_statement.json()
    print(income_statement.keys())
    income_statement_df = pd.DataFrame(income_statement["annualReports"])

    balance_sheet = requests.get(
        f"https://www.alphavantage.co/query?function=BALANCE_SHEET"
        f"&symbol={stock}&apikey=KYGP0LUFEUKAPRGY"
    )
    balance_sheet = balance_sheet.json()
    print(balance_sheet.keys())
    balance_sheet_df = pd.DataFrame(balance_sheet["annualReports"])

    overview = requests.get(
        f"https://www.alphavantage.co/query?function=OVERVIEW"
        f"&symbol={stock}&apikey=KYGP0LUFEUKAPRGY"
    )
    overview = overview.json()
    print(overview.keys())
    PERatio = overview["PERatio"]

    return income_statement_df, balance_sheet_df, PERatio

    
# Getting daily price for stock 
def get_stock_daily(stock):
    stock_daily = requests.get(
        f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY"
        f"&symbol={stock}&outputsize=full&apikey=KYGP0LUFEUKAPRGY"
    )
    stock_daily = stock_daily.json()
    print(stock_daily.keys())
    stock_daily_df = pd.DataFrame(stock_daily["Time Series (Daily)"])
    stock_daily_df = stock_daily_df.T.rename(
        columns={
            "1. open": "open",
            "2. high": "high",
            "3. low": "low",
            "4. close": "close",
            "5. volume": "volume",
        }
    )
    stock_daily_df = stock_daily_df.astype("float")
    stock_daily_df.index = pd.to_datetime(stock_daily_df.index)
    stock_daily_df = stock_daily_df.sort_index(ascending=True)

    return stock_daily_df


# Getting stock latest price
def get_stock_latest(stock):
    stock_latest = requests.get(
        f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE"
        f"&symbol={stock}&apikey=KYGP0LUFEUKAPRGY"
    )
    stock_latest = stock_latest.json()
    print(stock_latest.keys())
    stock_latest = stock_latest["Global Quote"]["05. price"]
    stock_latest = round(float(stock_latest), 2)

    return stock_latest


# Getting stock weekly price
def get_stock_weekly(stock):
    stock_weekly = requests.get(
        f"https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY"
        f"&symbol={stock}&apikey=KYGP0LUFEUKAPRGY"
    )
    stock_weekly = stock_weekly.json()
    stock_weekly_df = pd.DataFrame(stock_weekly["Weekly Time Series"]).T.rename(
        columns={
            "1. open": "open",
            "2. high": "high",
            "3. low": "low",
            "4. close": "close",
            "5. volume": "volume",
        }
    )
    stock_weekly_df = stock_weekly_df.astype("float")
    stock_weekly_df.index = pd.to_datetime(stock_weekly_df.index)
    stock_weekly_df = stock_weekly_df.sort_index(ascending=True)

    return stock_weekly_df


# Packed data preparation into function
def prepare_data(stock):
    print(stock)
    income_statement, balance_sheet, PERatio = get_income_balance_sheet(stock)
    profitability = pd.DataFrame(
        income_statement.loc[:, "netIncome"].astype(float)
        / income_statement.loc[:, "totalRevenue"].astype(float),
        columns=["Profitability"],
    )
    profitability.loc[:, "fiscalDateEnding"] = pd.to_datetime(
        income_statement["fiscalDateEnding"], format="%Y-%m-%d"
    )
    profitability = profitability.iloc[:10, :]

    technical_efficiency = pd.DataFrame(
        income_statement["totalRevenue"].astype(float)
        / balance_sheet["totalAssets"].astype(float).rolling(2).mean().shift(-1),
        columns=["TechnicalEfficiency"],
    )
    technical_efficiency.loc[:, "fiscalDateEnding"] = pd.to_datetime(
        income_statement["fiscalDateEnding"], format="%Y-%m-%d"
    )
    technical_efficiency = technical_efficiency.iloc[:10, :]

    financial_structure = pd.DataFrame(
        balance_sheet["totalAssets"].astype(float).rolling(2).mean().shift(-1)
        / balance_sheet["totalShareholderEquity"]
        .astype(float)
        .rolling(2)
        .mean()
        .shift(-1),
        columns=["FinancialStructure"],
    )
    financial_structure.loc[:, "fiscalDateEnding"] = pd.to_datetime(
        income_statement["fiscalDateEnding"], format="%Y-%m-%d"
    )
    financial_structure = financial_structure.iloc[:10, :]

    ROE_decomposition = pd.DataFrame(
        profitability["Profitability"]
        * technical_efficiency["TechnicalEfficiency"]
        * financial_structure["FinancialStructure"],
        columns=["ROE"],
    )
    ROE_decomposition.loc[:, "fiscalDateEnding"] = pd.to_datetime(
        income_statement["fiscalDateEnding"], format="%Y-%m-%d"
    )
    ROE_decomposition = ROE_decomposition.iloc[:10, :]

    stock_weekly = get_stock_weekly(stock)
    stock_weekly_df = stock_weekly.iloc[-100:, :]

    stock_weekly_df[["dcl", "dcm", "dcu"]] = stock_weekly.ta.donchian(
        lower_length=40, upper_length=52
    ).iloc[-100:, :]

    stock_daily = get_stock_daily(stock)
    stock_daily_df = stock_daily.iloc[-400:, :]
    stock_daily_df.loc[:, "MA20"] = stock_daily_df["close"].rolling(window=20).mean()
    stock_daily_df.loc[:, "MA5"] = stock_daily_df["close"].rolling(window=5).mean()

    macd = MACD(
        close=stock_daily_df["close"], window_slow=26, window_fast=12, window_sign=9
    )

    stock_latest = get_stock_latest(stock)

    return (
        profitability,
        technical_efficiency,
        financial_structure,
        ROE_decomposition,
        PERatio,
        stock_daily_df,
        macd,
        stock_weekly_df,
        stock_latest,
    )  


# Packed figure preparation into function
def make_fig(
    profitability,
    technical_efficiency,
    financial_structure,
    ROE_decomposition,
    PERatio,
    stock_daily_df,
    macd,
    stock_weekly_df,
    stock_latest,
):

    # Fig 1
    fig_1 = go.Figure(
        go.Indicator(
            domain={"x": [0, 1], "y": [0, 1]},
            value=int(stock_latest),
            mode="gauge+number+delta",
            title={"text": ""},
            delta={"reference": round(stock_weekly_df["dcl"][-1], 2)},
            gauge={
                "axis": {"range": [None, round(stock_weekly_df["dcu"][-1], -2)]},
                "steps": [
                    {
                        "range": [0, round(stock_weekly_df["dcl"][-1], -1)],
                        "color": "lightgray",
                    },
                    {
                        "range": [
                            round(stock_weekly_df["dcu"][-1], -1),
                            round(stock_weekly_df["dcu"][-1], -2),
                        ],
                        "color": "gray",
                    },
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.5,
                    "value": round(stock_weekly_df["dcl"][-1], -1),
                },
            },
        )
    )
    fig_1.update_layout(
        margin=go.layout.Margin(
            l=1,  # left margin
            r=5,  # right margin
            b=0,  # bottom margin
            t=0,  # top margin
        ),
        height=200,
        width=260,
    )

    # Fig 2
    fig_2 = make_subplots(
        rows=8,
        cols=18,
        horizontal_spacing=0.05,
        vertical_spacing=0.03,
        specs=[
            [
                {"rowspan": 4, "colspan": 4},
                None,
                None,
                None,
                {"rowspan": 4, "colspan": 4},
                None,
                None,
                None,
                {"rowspan": 4, "colspan": 4},
                None,
                None,
                None,
                {"rowspan": 4, "colspan": 4},
                None,
                None,
                None,
                {"rowspan": 4, "colspan": 2},
                None,
            ],
            [
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
                None,
                None,
                None,
            ],
            [
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
                None,
                None,
                None,
            ],
            [
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
                None,
                None,
                None,
            ],
            [
                {"rowspan": 3, "colspan": 9},
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                {"rowspan": 4, "colspan": 9},
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ],
            [
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
                None,
                None,
                None,
            ],
            [
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
                None,
                None,
                None,
            ],
            [
                {"rowspan": 1, "colspan": 9},
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
                None,
                None,
            ],
        ],
        print_grid=True,
    )

    fig_2.add_trace(
        go.Bar(
            name="Profitability",
            x=profitability["fiscalDateEnding"],
            y=profitability["Profitability"],
        ),
        row=1,
        col=1,
    )
    fig_2.add_trace(
        go.Bar(
            name="TechnicalEfficiency",
            x=technical_efficiency["fiscalDateEnding"],
            y=technical_efficiency["TechnicalEfficiency"],
        ),
        row=1,
        col=5,
    )
    fig_2.add_trace(
        go.Bar(
            name="FinancialStructure",
            x=financial_structure["fiscalDateEnding"],
            y=financial_structure["FinancialStructure"],
        ),
        row=1,
        col=9,
    )
    fig_2.add_trace(
        go.Bar(
            name="ROE",
            x=ROE_decomposition["fiscalDateEnding"],
            y=ROE_decomposition["ROE"],
        ),
        row=1,
        col=13,
    )
    fig_2.add_trace(
        go.Bar(
            name="PE",
            x=["PERatio"],
            y=[float(PERatio)],
        ),
        row=1,
        col=17,
    )

    fig_2.add_trace(
        go.Candlestick(
            x=stock_daily_df.iloc[-90:, :].index,
            open=stock_daily_df.iloc[-90:, :]["open"],
            high=stock_daily_df.iloc[-90:, :]["high"],
            low=stock_daily_df.iloc[-90:, :]["low"],
            close=stock_daily_df.iloc[-90:, :]["close"],
            name="Daily",
        ),
        row=5,
        col=1,
    )
    fig_2.add_trace(
        go.Scatter(
            x=stock_daily_df.iloc[-90:, :].index,
            y=stock_daily_df.iloc[-90:, :]["MA5"],
            opacity=0.7,
            line=dict(color="orange", width=2),
            name="MA 5",
        ),
        row=5,
        col=1,
    )
    fig_2.add_trace(
        go.Scatter(
            x=stock_daily_df.iloc[-90:, :].index,
            y=stock_daily_df.iloc[-90:, :]["MA20"],
            opacity=0.7,
            line=dict(color="darkgoldenrod", width=2),
            name="MA 20",
        ),
        row=5,
        col=1,
    )

    dt_all = pd.date_range(start=stock_daily_df.index[0], end=stock_daily_df.index[-1])
    dt_obs = [d.strftime("%Y-%m-%d") for d in pd.to_datetime(stock_daily_df.index)]
    dt_breaks = [d for d in dt_all.strftime("%Y-%m-%d").tolist() if not d in dt_obs]

    fig_2.update_layout(xaxis6_showticklabels=False)
    fig_2.update_layout(xaxis6_rangeslider_visible=False)
    fig_2.update_layout(xaxis6_rangebreaks=[dict(values=dt_breaks)])
    fig_2.update_layout(xaxis6_rangebreaks=[dict(bounds=["sat", "mon"])])

    colors = ["green" if val >= 0 else "red" for val in macd.macd_diff()[-90::]]
    fig_2.add_trace(
        go.Bar(
            x=stock_daily_df.iloc[-90:, :].index,
            y=macd.macd_diff()[-90::],
            marker_color=colors,
            name="MACD",
        ),
        row=8,
        col=1,
    )
    fig_2.update_layout(xaxis8_rangeslider_visible=False)
    fig_2.update_layout(xaxis8_rangebreaks=[dict(values=dt_breaks)])
    fig_2.update_layout(xaxis8_rangebreaks=[dict(bounds=["sat", "mon"])])

    fig_2.add_trace(
        go.Scatter(
            x=stock_weekly_df.iloc[-60:, :].index,
            y=stock_weekly_df.iloc[-60:, :]["close"],
            line=dict(color="blue", width=2),
            name="Weekly",
        ),
        row=5,
        col=10,
    )
    fig_2.add_trace(
        go.Scatter(
            x=stock_weekly_df.iloc[-60:, :].index,
            y=stock_weekly_df.iloc[-60:, :]["dcl"],
            opacity=0.7,
            line=dict(color="red", width=2, dash="dash"),
            name="DCL",
        ),
        row=5,
        col=10,
    )
    fig_2.add_trace(
        go.Scatter(
            x=stock_weekly_df.iloc[-60:, :].index,
            y=stock_weekly_df.iloc[-60:, :]["dcm"],
            opacity=0.7,
            line=dict(color="blue", width=2, dash="dash"),
            name="DCM",
        ),
        row=5,
        col=10,
    )
    fig_2.add_trace(
        go.Scatter(
            x=stock_weekly_df.iloc[-60:, :].index,
            y=stock_weekly_df.iloc[-60:, :]["dcu"],
            opacity=0.7,
            line=dict(color="green", width=2, dash="dash"),
            name="DCU",
        ),
        row=5,
        col=10,
    )
    fig_2.add_annotation(
        x=stock_weekly_df.iloc[-60:, :].index[-1],
        y=round(stock_weekly_df["dcu"][-1], 2),
        text=f"DCU {(round(stock_weekly_df['dcu'][-1], 2)):.2f}",
        showarrow=True,
        arrowhead=2,
        yshift=1,
        row=5,
        col=10,
    )
    fig_2.add_annotation(
        x=stock_weekly_df.iloc[-60:, :].index[-1],
        y=round(stock_weekly_df["dcl"][-1], 2),
        text=f"DCL {(round(stock_weekly_df['dcl'][-1], 2)):.2f}",
        showarrow=True,
        arrowhead=2,
        yshift=1,
        row=5,
        col=10,
    )

    fig_2.update_layout(
        margin=go.layout.Margin(
            l=1,  # left margin
            r=1,  # right margin
            b=1,  # bottom margin
            t=1,  # top margin
        ),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=1),
        height=654,
        width=845,
    )

    return fig_1, fig_2    
