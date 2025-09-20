# import dash
# from dash import html, callback, Output, Input, State, ctx
# import dash_bootstrap_components as dbc
# import dash_mantine_components as dmc
#
# dash.register_page(__name__, path='/page-4')
# min_step = 0
# max_step = 3
# active = 0
#
#
# def layout():
#     # navigation buttons
#     restart_button = dbc.Button("Restart", href='/page-3', id='select-report-restart-button', color="light")
#     previous_button = dbc.Button("Previous", id='select-report-previous-button')
#     next_button = dbc.Button("Next", id='select-report-next-button')
#     generate_report_button = dbc.Button("Generate Report", href='/page-5', id='generate-report-button', color="success")
#     button_bar = html.Div([restart_button, previous_button, next_button, generate_report_button], className="d-flex justify-content-between")
#
#     # stepper
#     stepper = dmc.MantineProvider(html.Div([dmc.Stepper(
#         id="select-report-stepper",
#         active=active,
#         color="green",
#         children=[
#             dmc.StepperStep(
#                 label="First step",
#                 description="Real Estate Exposures",
#             ),
#             dmc.StepperStep(
#                 label="Second step",
#                 description="Company Exposures",
#             ),
#             dmc.StepperStep(
#                 label="Final step",
#                 description="Individual Exposures",
#             ),
#             dmc.StepperCompleted(),
#         ],
#     )], style={
#         "border-radius": 15,
#         "border": f"1px solid {dmc.DEFAULT_THEME['colors']['gray'][4]}",
#         "padding": 20,
#     }))
#
#     # description
#     description = html.Div([html.P("Enter your firm's exposures", style={
#         "border-radius": 15,
#         "border": f"1px solid {dmc.DEFAULT_THEME['colors']['gray'][4]}",
#         "backgroundColor": f"{dmc.DEFAULT_THEME['colors']['gray'][1]}",
#         "padding": 10
#     })])
#
#     # user selection
#     user_selection = html.Div([
#         description,
#         html.Div([], style={"height": 10, "border": "0 none"}),
#         html.Div([], id='step-title')
#     ], style={
#         "border-radius": 15,
#         "border": f"1px solid {dmc.DEFAULT_THEME['colors']['gray'][4]}",
#         "padding": 10
#     })
#
#     # page layout
#     layout = html.Div([
#         html.H3('Institutional Report'),
#         html.Hr(),
#         stepper,
#         html.Div([], style={"height": 10, "border": "0 none"}),
#         user_selection,
#         html.Hr(),
#         button_bar,
#     ], className="mx-auto py-3 container")
#     return layout
#
#
# @callback(
#     Output("select-report-stepper", "active"),
#     Output("step-title", "children"),
#     Input("select-report-previous-button", "n_clicks"),
#     Input("select-report-next-button", "n_clicks"),
#     State("select-report-stepper", "active"),
#     State("select-report-stepper", "children"),
# )
# def update(back, next_, current, stepper_children):
#     if current is None:
#         current = 0
#
#     button_id = ctx.triggered_id
#     step = current
#
#     if button_id == "select-report-previous-button":
#         step = step - 1 if step > min_step else step
#     elif button_id == "select-report-next-button":
#         step = step + 1 if step < max_step else step
#
#     if step < max_step:
#         title = html.H4(f"Bank: {stepper_children[step]['props']['description']}")
#     else:
#         title = html.H4(
#             "End of Selection - Generate Report or Restart",
#             style={"text-align": "center"}
#         )
#     return step, title
#
# @callback(
#    Output(component_id='select-report-previous-button', component_property='style'),
#    Output(component_id='select-report-next-button', component_property='style'),
#    Input(component_id='select-report-previous-button', component_property='n_clicks'),
#    Input(component_id='select-report-next-button', component_property='n_clicks'),
#    Input(component_id='select-report-stepper', component_property='active'),
# )
# def show_hide_element(back, next_, current):
#     if current == 0:
#         return {'opacity': 0}, {}
#     elif current == max_step:
#         return {}, {'opacity': 0}
#     else:
#         return {}, {}
