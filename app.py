import dash
from dash import Dash, html, dcc, Input, Output, callback, dash_table,ctx
import dash_bootstrap_components as dbc
import pandas as pd
from navbar import create_navbar
from sidebar2 import *


FA621 = "https://use.fontawesome.com/releases/v6.2.1/css/all.css"
APP_TITLE = "First Dash App"

app = Dash(
    __name__,
    #suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.LUX,  # Dash Themes CSS
        FA621,  # Font Awesome Icons CSS
    ],
    title=APP_TITLE,
    use_pages=True,  # New in Dash 2.7 - Allows us to register pages
)
server = app.server
NAVBAR = create_navbar()
app.layout = dcc.Loading(  # <- Wrap App with Loading Component
    id='loading_page_content',
    children=[
        html.Div(
            [
                NAVBAR
            ]),
        html.Div(
            [
                dash.page_container
            ])
    ],
    color='primary',  # <- Color of the loading spinner
    fullscreen=True  # <- Loading Spinner should take up full screen
)

server = app.server
if __name__ == '__main__':
    app.run(debug=True)