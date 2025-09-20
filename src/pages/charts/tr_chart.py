import dash
from dash import html, dcc, Input, Output
import pandas as pd
import plotly.express as px

# Register the page
dash.register_page(__name__, path='/charts/tr_chart')

# Load data
df = pd.read_csv("src/assets/data/transition_risk_data.csv")

# Extract year columns
def get_years(df):
    return [int(col) for col in df.columns if str(col).isdigit()]

def layout():
    return html.Div([
        html.H1("Transition Risk Charting", className="container"),
        html.Div([
            html.Div([
                html.Label("Select Region"),
                dcc.Dropdown(id='region-dropdown'),

                html.Label("Select Variable"),
                dcc.Dropdown(id='variable-dropdown', style={'width': '100%', 'whiteSpace': 'normal'}),

                html.Label("Select Unit"),
                dcc.Dropdown(id='unit-dropdown', style={'width': '100%', 'whiteSpace': 'normal'}),

                html.Label("Select Model"),
                dcc.Dropdown(id='model-dropdown', style={'width': '100%', 'whiteSpace': 'normal'}),

                html.Label("Select Scenario"),
                dcc.Dropdown(id='scenario-dropdown'),

                html.Label("Select Year Range"),
                dcc.RangeSlider(
                    id='year-slider',
                    step=1,
                    tooltip={"placement": "bottom", "always_visible": True}
                ),

                html.Div([
                    html.Button("Reset Filters", id='reset-button', n_clicks=0, className='box-style')
                ], style={'marginTop': '20px'})
            ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),

            html.Div([
                dcc.Graph(id='line-chart'),
            ], style={'width': '68%', 'display': 'inline-block', 'padding': '10px'})
        ])
    ])

@dash.callback(
    Output('region-dropdown', 'options'),
    Output('region-dropdown', 'value'),
    Input('reset-button', 'n_clicks')
)
def update_region(reset_clicks):
    region_options = [{'label': r, 'value': r} for r in sorted(df['Region'].dropna().unique())]
    return region_options, None

@dash.callback(
    Output('variable-dropdown', 'options'),
    Output('variable-dropdown', 'value'),
    Input('region-dropdown', 'value')
)
def update_variable(region):
    if region is None:
        return [], None
    filtered_df = df[df['Region'] == region]
    variable_options = [{'label': v, 'value': v} for v in sorted(filtered_df['Variable'].dropna().unique())]
    return variable_options, None

@dash.callback(
    Output('unit-dropdown', 'options'),
    Output('unit-dropdown', 'value'),
    Input('region-dropdown', 'value'),
    Input('variable-dropdown', 'value')
)
def update_unit(region, variable):
    if region is None or variable is None:
        return [], None
    filtered_df = df[(df['Region'] == region) & (df['Variable'] == variable)]
    unit_options = [{'label': u, 'value': u} for u in sorted(filtered_df['Unit'].dropna().unique())]
    return unit_options, None

@dash.callback(
    Output('model-dropdown', 'options'),
    Output('model-dropdown', 'value'),
    Input('region-dropdown', 'value'),
    Input('variable-dropdown', 'value'),
    Input('unit-dropdown', 'value')
)
def update_model(region, variable, unit):
    if region is None or variable is None or unit is None:
        return [], None
    filtered_df = df[
        (df['Region'] == region) &
        (df['Variable'] == variable) &
        (df['Unit'] == unit)
    ]
    model_options = [{'label': m, 'value': m} for m in sorted(filtered_df['Model'].dropna().unique())]
    return model_options, None

@dash.callback(
    Output('scenario-dropdown', 'options'),
    Output('scenario-dropdown', 'value'),
    Input('region-dropdown', 'value'),
    Input('variable-dropdown', 'value'),
    Input('unit-dropdown', 'value'),
    Input('model-dropdown', 'value')
)
def update_scenario(region, variable, unit, model):
    if not all([region, variable, unit, model]):
        return [], None
    filtered_df = df[
        (df['Region'] == region) &
        (df['Variable'] == variable) &
        (df['Unit'] == unit) &
        (df['Model'] == model)
    ]
    scenario_options = [{'label': s, 'value': s} for s in sorted(filtered_df['Scenario'].dropna().unique())]
    return scenario_options, None

@dash.callback(
    Output('year-slider', 'min'),
    Output('year-slider', 'max'),
    Output('year-slider', 'value'),
    Output('year-slider', 'marks'),
    Input('region-dropdown', 'value'),
    Input('variable-dropdown', 'value'),
    Input('unit-dropdown', 'value'),
    Input('model-dropdown', 'value'),
    Input('scenario-dropdown', 'value')
)
def update_year_slider(region, variable, unit, model, scenario):
    if not all([region, variable, unit, model, scenario]):
        years = get_years(df)
    else:
        filtered_df = df[
            (df['Region'] == region) &
            (df['Variable'] == variable) &
            (df['Unit'] == unit) &
            (df['Model'] == model) &
            (df['Scenario'] == scenario)
        ]
        years = [int(col) for col in filtered_df.columns
                 if str(col).isdigit() and not filtered_df[col].isna().all()]
    if not years:
        return 2025, 2100, [2025, 2100], {2025: '2025', 2100: '2100'}
    marks = {year: str(year) for year in years if year % 10 == 0}
    return min(years), max(years), [min(years), max(years)], marks

@dash.callback(
    Output('line-chart', 'figure'),
    Input('region-dropdown', 'value'),
    Input('variable-dropdown', 'value'),
    Input('unit-dropdown', 'value'),
    Input('model-dropdown', 'value'),
    Input('scenario-dropdown', 'value'),
    Input('year-slider', 'value')
)
def update_chart(region, variable, unit, model, scenario, year_range):
    # Color palette
    palette = ['#00B050']
    background = '#FFFFFF'
    line_color = palette[-1]  # Use the darkest green for the single line

    def add_footer(fig, text, font_size=14):
        fig.update_layout(margin=dict(t=40, r=20, l=60, b=140))
        fig.add_annotation(
            text=text,
            x=0.5, y=-0.18,
            xref="paper", yref="paper",
            showarrow=False,
            xanchor="center", yanchor="top",
            align="center",
            font=dict(size=font_size)
        )
        return fig

    # Title helper to place title inside the figure at the top without overlapping
    def add_top_title(fig, text, font_size=16, band=0.12):
        """
        Reserve a top band inside the figure (not outside), and place a centered
        annotation in that band so it exports with the image and doesn't overlap the plot.
        """
        # clamp band between 6% and 30% of the figure height
        band = max(0.06, min(band, 0.30))
        top_of_plot = 1.0 - band

        # Ensure the plot area leaves room for the band
        # Keep gridcolor applied; don't overwrite existing yaxis settings beyond domain
        fig.update_layout(
            margin=dict(t=20, r=20, l=60, b=80),
        )
        # Merge/extend yaxis settings carefully to keep grid styling
        yaxis = fig.layout.yaxis.to_plotly_json() if fig.layout.yaxis else {}
        yaxis['domain'] = [0.0, top_of_plot]
        fig.update_layout(yaxis=yaxis)

        # Add the title annotation centered in the reserved band
        fig.add_annotation(
            text=text,
            x=0.5, y=top_of_plot + band / 2.0,
            xref="paper", yref="paper",
            showarrow=False,
            xanchor="center", yanchor="middle",
            align="center",
            font=dict(size=font_size),
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="rgba(0,0,0,0)",
            borderpad=6
        )
        return fig

    # Case: selections incomplete
    if not all([region, variable, unit, model, scenario]):
        fig = px.line(title=None)
        fig.update_layout(
            plot_bgcolor=background,
            paper_bgcolor=background,
            font=dict(color="#222"),
            xaxis=dict(gridcolor="#EEE"),
            yaxis=dict(gridcolor="#EEE"),
            showlegend=False
        )
        fig = add_footer(fig, "Please select all options to display the chart")
        return fig

    filtered_df = df[
        (df['Region'] == region) &
        (df['Variable'] == variable) &
        (df['Unit'] == unit) &
        (df['Model'] == model) &
        (df['Scenario'] == scenario)
    ]

    years = get_years(df)
    if not year_range:
        selected_years = years
    else:
        selected_years = [year for year in years if year_range[0] <= year <= year_range[1]]

    # Case: no data
    if filtered_df.empty or not selected_years:
        fig = px.line(title=None)
        fig.update_layout(
            plot_bgcolor=background,
            paper_bgcolor=background,
            font=dict(color="#222"),
            xaxis=dict(gridcolor="#EEE"),
            yaxis=dict(gridcolor="#EEE"),
            showlegend=False
        )
        fig = add_footer(fig, "No data available for the selected filters")
        return fig

    melted_df = filtered_df.melt(
        id_vars=['Region', 'Variable', 'Unit', 'Model', 'Scenario'],
        value_vars=[str(y) for y in selected_years],
        var_name='Year', value_name='Value'
    )

    # Plot a single line, no legend
    fig = px.line(
        melted_df,
        x='Year',
        y='Value',
        color_discrete_sequence=[line_color]
    )
    fig.update_traces(showlegend=False)
    fig.update_layout(
        title=None,
        plot_bgcolor=background,
        paper_bgcolor=background,
        font=dict(color="#222"),
        xaxis=dict(gridcolor="#EEE"),
        yaxis=dict(gridcolor="#EEE"),
        showlegend=False,
        yaxis_title=variable
    )

    title_text = (
        f"<b>Transition Risk</b> <br>"
        f"{region} - {variable} ({unit})<br>"
        f"<b>Model:</b> {model} <br>"
        f"<b>Scenario:</b> {scenario}"
    )

    fig = add_top_title(fig, title_text, font_size=16, band=0.26)
    return fig
