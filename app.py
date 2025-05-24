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
    "Accidental Pet": "OXY",
    "Advanced Micro Devices Inc": "AMD",
    "Ally Finl Inc": "ALLY",
    "Alphabet Inc": "GOOG",
    "American Express Co": "AXP",
    "Amazon Com": "AMZN",
    "Apple Inc": "AAPL",
    "Bank of America": "BAC",
    "Chevron Corp": "CVX",
    "Chubb Limited": "CB",
    "Coca Cola Co": "KO",
    "Davita Inc": "DVA",
    "Home Depot": "HD",
    "Jpmorgan Chase": "JPM",
    "Kraft Heinz Co": "KHC",
    "Kroger": "KR",
    "Microsoft Corp": "MSFT",
    "Moody'S Corp": "MCO",
    "Nvidia Corporation": "NVDA",
    "Pepsi Inc": "PEP",
    "Progress Corp Oh": "PGR",
    "Sirius XM": "SIRI",
    "Starbucks Corp": "SBUX",
    "Target": "TGT",
    "Tesla Inc": "TSLA",
    "Verisign": "VRSN",
    "Walmart": "WMT",
}
stocks_dropdown = [{"label": i[0], "value": i[1]} for i in stocks.items()]


# Build App
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

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
                                                style={"width": 1515},
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
                                                        html.P("Select a stock:"),
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
                                                                f"value for 52 weeks. \nDuPont model shows a company's fundamental "
                                                                f"performance. It breaks out the different drivers of ROE into "
                                                                f"three ratio components. \nThe price-to-earnings (P/E) ratio measures " 
                                                                f"a company's share price relative to its earnings per share (EPS). "
                                                                f"\nThe candlestick patterns and MACD gauge the momentum of the price trend. " 
                                                                f"Donchian channels can make natural partners for a crossover strategy."
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
                                                style={"height": 695, "width": 370},
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
                                                style={"height": 695, "width": 1128},
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
            style={"height": 825, "width": 1550},
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


# Run app and display result in new page
if __name__ == '__main__':
    app.run(debug=True)
