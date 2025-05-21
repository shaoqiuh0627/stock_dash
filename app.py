import json
import math
import matplotlib.pylab as plt
import matplotlib.pyplot as plt
import pandas as pd
import requests
from ta.momentum import StochasticOscillator
from ta.trend import MACD
from termcolor import colored as cl
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from utils import (
    get_income_balance_sheet,
    get_stock_daily,
    get_stock_latest,
    get_stock_weekly,
    prepare_data,
    make_fig,
)


# Dropdown list and radio button options set up
stocks = {
    "Apple": "AAPL",
    "Pepsi": "PEP",
}
stocks_dropdown = [{"label": i[0], "value": i[1]} for i in stocks.items()]


# Build App
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Div(
                                        [
                                            dbc.Card(
                                                dbc.CardBody(
                                                    [
                                                        html.Div(
                                                            [
                                                                html.H3(
                                                                    "Stock Finantial Fundamentals and Price Metrics"
                                                                ),
                                                            ],
                                                            style={
                                                                "textAlign": "center"
                                                            },
                                                        )
                                                    ]
                                                ),
                                                style={"width": 1165},
                                            ),
                                        ]
                                    )
                                ],
                                width=12,
                            ),
                        ],
                        align="center",
                    ),
                    html.Br(),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Div(
                                        [
                                            dbc.Card(
                                                dbc.CardBody(
                                                    [
                                                        html.P("Select A stock:"),
                                                        dcc.Dropdown(
                                                            id="stock-dropdown",
                                                            options=stocks_dropdown,
                                                            value="AAPL",
                                                            style={"height": 40},
                                                        ),
                                                        html.P((f"")),
                                                        html.P(
                                                            (
                                                                f"The price speedometer chart displays the latest price value "
                                                                f"to estimate the progress toward DCL value for 40 weeks and DCU "
                                                                f"value for 52 weeks. DuPont model shows a company's fundamental "
                                                                f"performance. It breaks out the different drivers of ROE into "
                                                                f"three ratio components. The candlestick patterns and MACD gauge "
                                                                f"the momentum of the price trend. Donchian channels can make "
                                                                f"natural partners for a crossover strategy."
                                                            )
                                                        ),
                                                        dcc.Graph(
                                                            id="g1",
                                                            config={
                                                                "displayModeBar": False
                                                            },
                                                        ),
                                                    ]
                                                ),
                                                style={"height": 695, "width": 280},
                                            ),
                                        ]
                                    )
                                ],
                                width=3,
                            ),
                            dbc.Col(
                                [
                                    html.Div(
                                        [
                                            dbc.Card(
                                                dbc.CardBody(
                                                    [
                                                        dcc.Graph(
                                                            id="g2",
                                                            config={
                                                                "displayModeBar": False
                                                            },
                                                        )
                                                    ]
                                                ),
                                                style={"height": 695, "width": 865},
                                            ),
                                        ]
                                    )
                                ],
                                width=9,
                            ),
                        ],
                        align="center",
                    ),
                ]
            ),
            color="dark",
            style={"height": 825, "width": 1200},
        )
    ]
)


@app.callback(
    [
        Output("g1", "figure"),
        Output("g2", "figure"),
    ],
    Input("stock-dropdown", "value"),
)
def display_graph(stock):
    (
        profitability,
        technical_efficiency,
        financial_structure,
        ROE_decomposition,
        PERatio,
        stock_daily_df,
        macd,
        stock_weekly_df,
        stock_latest,
    ) = prepare_data(stock)

    f1, f2 = make_fig(
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

    return f1, f2


# Run app and display result inline in the notebook
app.run()
