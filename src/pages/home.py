import dash
from dash import html, callback, Output, Input, State, dcc
import dash_bootstrap_components as dbc
from PIL import Image

dash.register_page(__name__, path='/')

def layout():

    disclaimer_text = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. \nDonec et odio sit amet elit vulputate lobortis. Curabitur luctus in neque at feugiat. Sed a efficitur magna. Pellentesque id sollicitudin sapien, in congue risus. \nDuis sodales interdum massa, mattis ornare neque sagittis id. Vivamus a ornare lorem. In et sagittis libero, sed posuere lacus. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Curabitur risus nisi, lobortis vitae posuere eu, hendrerit a ipsum. Donec odio mauris, laoreet eget molestie sed, porttitor non lacus. Donec id elementum massa. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus vestibulum ullamcorper elit vel bibendum. Donec pulvinar fermentum quam, a imperdiet sem tristique in. Nullam varius eros eget tincidunt faucibus.Aliquam commodo porta orci. Aliquam vulputate nisl eu nunc accumsan, et imperdiet erat vulputate. Sed non posuere nisi. Nullam et scelerisque velit, nec laoreet diam. In iaculis nisl eget turpis consequat, vel finibus magna interdum. Vestibulum ultrices est sit amet mauris varius molestie. Ut diam diam, fermentum malesuada porta sed, congue nec ante. Integer imperdiet augue sit amet lorem mattis tincidunt. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.Quisque auctor ultrices laoreet. Ut ac augue laoreet, mollis diam eu, imperdiet dui. Nullam quis augue mollis, fringilla dui eget, mollis erat. Fusce quis felis ipsum. Morbi commodo risus a leo euismod tincidunt. Nunc semper ut nulla vitae lobortis. Quisque convallis ullamcorper lorem, sit amet euismod nisl convallis eu. '

    layout = html.Div([
        
        #dcc.Location(id="redirect-home"),  # For redirecting after acknowledging the disclaimer
        dcc.Store(id="disclaimer-acknowledged", storage_type="local"),  # To store acknowledgment status

        html.Div(
    [
        html.H3('Climate Financial Risk Forum', style={"margin-bottom": "0", "color": "white"}),
        html.H6('Online Climate Scenario Analysis Narrative Tool', style={"margin-top": "0", "color": "white"})
    ],
    style={
            "background": "#000000",
            "color": "white",
            "padding": "8px 1px 8px 1px",
            "borderRadius": "0px",
            "textAlign": "center",
            "marginBottom": "0px",
            "marginTop": "0px",
            "width": "99%",
            "marginLeft": "auto",
            "marginRight": "auto",
            "boxSizing": "border-box"
    }
        ),

        html.Div(
            html.Img(src=Image.open("assets/logos/cfrf_logo.png"),
                style={
                    "display": "block",
                    "marginLeft": "auto",
                    "marginRight": "auto",
                    "height": "254px"
                },
                alt="CFRF Logo"
            ),
            style={
                "backgroundColor": "#000000",
                "width": "99%",
                "padding": "20px 0",
                "marginLeft": "auto",
                "marginRight": "auto"
                 }
        ),

        html.Div(dbc.Button("Start: Generate Report", 
                            id="open", 
                            n_clicks=0,
                            href='/reports/generate-report', 
                            style={
                                "backgroundColor": "#51C876", 
                                "color": "black",
                                "borderRadius": "8px",      
                                "border": "none"
                            }),
                            className="text-center", 
                            style={
                                "backgroundColor": "#000000",
                                "width": "99%",
                                "padding": "20px 0",
                                "marginLeft": "auto",
                                "marginRight": "auto",
                                "textAlign": "center"
                            }
                        ),

        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Disclaimer", style={"color": "white"}), style={"backgroundColor": "#51C876"}),
                dbc.ModalBody([html.P(p) for p in disclaimer_text.split('\n')], style={"backgroundColor": "#51C876", "color": "white"}),
                dbc.ModalFooter(
                    [
                        dbc.Button("Acknowledge", id="acknowledge", class_name="mx-auto")#, href='/')
                    ],
                    style={"backgroundColor": "#51C876", "color": "white"}
                ),
            ],
            id="modal",
            size="lg",
            is_open=True,
        )
    ], style={"marginTop": "0px", "paddingTop": "0px"})
    return layout

@callback(
    Output("modal", "is_open"),
    Output("disclaimer-acknowledged", "data"),
    Input("acknowledge", "n_clicks"),
    State("disclaimer-acknowledged", "data"),
    prevent_initial_call=False
)
def handle_modal(n_ack, ack_data):
    if ack_data:
        return False, ack_data
    if n_ack:
        return False, True
    return True, ack_data