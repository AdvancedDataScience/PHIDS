import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 92,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}
 

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("Main Menu:", className="display-8"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                html.Hr(),
                dbc.NavLink("Out-patients", href="/outpatients", active="exact"),
                dbc.NavLink("In-pateints", href="/inpatients", active="exact"),
                dbc.NavLink("Communicable Diseases", href="/cdc", active="exact"),
                dbc.NavLink("Death statatistics", href="/deathstat", active="exact"),
                html.Hr(),
                dbc.NavLink("Burden of Diseases", href="/daly", active="exact"),
                html.Hr(),
                dbc.NavLink("Global Health", href="/globalhealth", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)
