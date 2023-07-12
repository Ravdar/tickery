import dash
from dash import dcc
from dash import html

app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1("Animated Bar Graphs"),
        html.Div(
            className="chartBarsWrap",
            children=[
                html.Div(
                    className="chartBars chartBars1",
                    children=[
                        html.Div(
                            className="bars",
                            children=[
                                html.Ul(
                                    children=[
                                        html.Li(
                                            children=[
                                                html.Div(
                                                    className="bar greenBar",
                                                    style={"height": "50%"},
                                                    children=[html.B("50%")],
                                                )
                                            ]
                                        ),
                                        html.Li(
                                            children=[
                                                html.Div(
                                                    className="bar blueBar",
                                                    style={"height": "70%"},
                                                    children=[html.B("70%")],
                                                )
                                            ]
                                        ),
                                        html.Li(
                                            children=[
                                                html.Div(
                                                    className="bar orangeBar",
                                                    style={"height": "90%"},
                                                    children=[html.B("90%")],
                                                )
                                            ]
                                        ),
                                        html.Li(
                                            children=[
                                                html.Div(
                                                    className="bar purpleBar",
                                                    style={"height": "60%"},
                                                    children=[html.B("60%")],
                                                )
                                            ]
                                        ),
                                    ]
                                ),
                                html.Ul(
                                    className="numbers",
                                    children=[
                                        html.Li("0%"),
                                        html.Li("25%"),
                                        html.Li("50%"),
                                        html.Li("75%"),
                                        html.Li("100%"),
                                    ],
                                ),
                            ],
                        )
                    ],
                )
            ],
        ),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
