from dash import html
import dash_bootstrap_components as dbc

def getHeader(app):
    # button: learn more
    button_howto = dbc.Button(
        "Learn more",
        id="howto-open",
        outline=True,
        color="info",
        href="https://www.pik-potsdam.de/",
        # Turn off lowercase transformation for class .button in stylesheet
        style={"textTransform": "none"},
    )

    # button: github
    button_github = dbc.Button(
        "View Code on github",
        outline=True,
        color="primary",
        href="https://github.com/PhilippVerpoort/blue-green-H2",
        id="gh-link",
        style={"text-transform": "none"},
    )

    # header
    header = dbc.Navbar(
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            html.Img(
                                id="logo",
                                src=app.get_asset_url("logo.png"),
                                height="30px",
                            ),
                            md="auto",
                        ),
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        html.H3("Blue-green hydrogen competition"),
                                        html.P("An interactive plotting widget"),
                                    ],
                                    id="app-title",
                                )
                            ],
                            md=True,
                            align="center",
                        ),
                    ],
                    align="center",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.NavbarToggler(id="navbar-toggler"),
                                dbc.Collapse(
                                    dbc.Nav(
                                        [
                                            dbc.NavItem(button_howto),
                                            dbc.NavItem(button_github),
                                        ],
                                        navbar=True,
                                    ),
                                    id="navbar-collapse",
                                    navbar=True,
                                ),
                            ],
                            md=2,
                        ),
                    ],
                    align="center",
                ),
            ],
            fluid=True,
        ),
        dark=True,
        color="dark",
        sticky="top",
    )

    return header
