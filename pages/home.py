from dash import html, callback, Output, Input, State
import dash_bootstrap_components as dbc

from pages.navbar import create_navbar

def create_layout():

    disclaimer_text = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. \nDonec et odio sit amet elit vulputate lobortis. Curabitur luctus in neque at feugiat. Sed a efficitur magna. Pellentesque id sollicitudin sapien, in congue risus. \nDuis sodales interdum massa, mattis ornare neque sagittis id. Vivamus a ornare lorem. In et sagittis libero, sed posuere lacus. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Curabitur risus nisi, lobortis vitae posuere eu, hendrerit a ipsum. Donec odio mauris, laoreet eget molestie sed, porttitor non lacus. Donec id elementum massa. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus vestibulum ullamcorper elit vel bibendum. Donec pulvinar fermentum quam, a imperdiet sem tristique in. Nullam varius eros eget tincidunt faucibus.Aliquam commodo porta orci. Aliquam vulputate nisl eu nunc accumsan, et imperdiet erat vulputate. Sed non posuere nisi. Nullam et scelerisque velit, nec laoreet diam. In iaculis nisl eget turpis consequat, vel finibus magna interdum. Vestibulum ultrices est sit amet mauris varius molestie. Ut diam diam, fermentum malesuada porta sed, congue nec ante. Integer imperdiet augue sit amet lorem mattis tincidunt. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.Quisque auctor ultrices laoreet. Ut ac augue laoreet, mollis diam eu, imperdiet dui. Nullam quis augue mollis, fringilla dui eget, mollis erat. Fusce quis felis ipsum. Morbi commodo risus a leo euismod tincidunt. Nunc semper ut nulla vitae lobortis. Quisque convallis ullamcorper lorem, sit amet euismod nisl convallis eu. '

    layout = html.Div([
        create_navbar(),
        html.Div(html.H3('Welcome to Climate Narrative Tool!'), className="mx-auto py-3 container"),
        html.Div(dbc.Button("Start", id="open", n_clicks=0), className="text-center"),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Disclaimer")),
                dbc.ModalBody([html.P(p) for p in disclaimer_text.split('\n')]),
                dbc.ModalFooter(
                    [
                        dbc.Button("Close", id="close", class_name="me-auto", n_clicks=0), 
                        dbc.Button("Next", id="next", class_name="ms-auto", href='/page-2')
                    ]
                ),
            ],
            id="modal",
            size="lg",
            is_open=False
        )
    ])
    return layout

@callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
