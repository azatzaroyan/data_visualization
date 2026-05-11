import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

# Initialize the Dash app with multi-page support
app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True
)

server = app.server

# Navbar
navbar = dbc.Navbar(
    dbc.Container([
        dbc.Row([
            dbc.Col(html.I(className="fa-solid fa-hotel me-2", style={"fontSize": "1.5rem"})),
            dbc.Col(dbc.NavbarBrand("Hotel Bookings Dashboard", className="ms-1 fw-bold")),
        ], align="center", className="g-0"),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(
            dbc.Nav([
                dbc.NavItem(dbc.NavLink(
                    [html.I(className="fa-solid fa-chart-pie me-1"), " Overview"],
                    href="/", active="exact"
                )),
                dbc.NavItem(dbc.NavLink(
                    [html.I(className="fa-solid fa-chart-line me-1"), " Trends"],
                    href="/trends", active="exact"
                )),
                dbc.NavItem(dbc.NavLink(
                    [html.I(className="fa-solid fa-magnifying-glass-chart me-1"), " Cancellation Analysis"],
                    href="/cancellation-analysis", active="exact"
                )),
            ], className="ms-auto", navbar=True),
            id="navbar-collapse",
            navbar=True,
        ),
    ], fluid=True),
    color="dark",
    dark=True,
    className="mb-4",
)

# App layout
app.layout = dbc.Container([
    navbar,
    dash.page_container
], fluid=True)

if __name__ == '__main__':
    app.run(debug=True)
