from dash import html, dcc,Input, Output, callback
import dash_bootstrap_components as dbc



def create_navbar():
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(
                dbc.NavLink(
                    [
                        html.I(className="fa-solid fa-globe"),  # Font Awesome Icon
                        " "  # Text beside icon
                    ],
                    href="https://www.bodthai.net",
                    target="_blank"
                )

            ),
            dbc.NavItem(
                dbc.NavLink(
                    [
                        html.I(className="fa-brands fa-github"),  # Font Awesome Icon
                        " "  # Text beside icon
                    ],
                    href="https://github.iu.edu/thwong/PHIDS",
                    target="_blank"
                )

            ),
            
            dbc.NavItem(
                dbc.NavLink(
                    [
                        html.I(className="fa-brands fa-linkedin"),  # Font Awesome Icon
                        " "  # Text beside icon
                    ],
                    href="https://www.linkedin.com/in/dr-thanawat-wongphan-68296598/",
                    target="_blank"
                )

            ),
            dcc.Dropdown([
                {
                "label": html.Span(
                    [
                        html.Span("Trat", style={'font-size': 15, 'text-decoration': 'underline'})
                    ], style={'align-items': 'center', 'justify-content': 'center'}
                    ),"value": "Trat",
                },
                {"label": [
                        html.Span("Other province.", style={'font-size': 15})]
                    
                    ,"value": "Others",
                },
                ],'Trat', id='ChooseProvince',style={'display': 'block',
        'width': 200}),
        dcc.Store(id="hiddenProvinceName")
        ],
        brand=html.Div(":::",id="divProvinceName"),
        #brand_href="/",
        # sticky="top",  # Uncomment if you want the navbar to always appear at the top on scroll.
        color="dark",  # Change this to change color of the navbar e.g. "primary", "secondary" etc.
        dark=True,  # Change this to change color of text within the navbar (False for dark text)
        
    )

    return navbar

@callback(
    Output("hiddenProvinceName", "data"),
    Output("divProvinceName", "children"),
    Input("ChooseProvince","value")
)
def GraphClick_cdc(clickData):
    if(clickData=='Choose province'):
        RetText='to enjoy the analysis, Choose province on your right selection box first .'
    else:
        RetText=f'Province: {clickData}'
    return clickData,RetText


{
            "label": html.Span(
                [
                    html.Br()
                ]
            ),
            "value": "",
        }