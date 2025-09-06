import dash_bootstrap_components as dbc


def create_navbar():

    navbar = dbc.NavbarSimple(
        children=[
            dbc.DropdownMenu(
                nav=True,
                in_navbar=True,
                label="Purpose",
                children=[
                    dbc.DropdownMenuItem("Overview", href='/purpose/purpose-overview'),
                    dbc.DropdownMenuItem("Introduction to the tool", href='/purpose/introduction-to-the-tool'),
                    dbc.DropdownMenuItem("How to use the tool?", href='/purpose/how-to-use-the-tool'),
                    dbc.DropdownMenuItem("How can the reports be used?", href='/purpose/how-can-the-reports-be-used'),
                    dbc.DropdownMenuItem("What is next?", href='/purpose/what-is-next'),
                ],
            ),
            dbc.DropdownMenu(
                nav=True,
                in_navbar=True,
                label="Limitations",
                children=[
                    dbc.DropdownMenuItem("Overview", href='/limitations/limitations-overview'),
                    dbc.DropdownMenuItem("Introduction to the tool", href='/limitations/long-term-scenario-limitations'),
                    dbc.DropdownMenuItem("How to use the tool", href='/limitations/short-term-scenario-limitations'),
                ],
            ),
            dbc.DropdownMenu(
                nav=True,
                in_navbar=True,
                label="Scenarios",
                children=[
                    dbc.DropdownMenuItem("Long-term scenarios", href='/scenarios/long-term-scenarios'),
                    dbc.DropdownMenuItem("Short-term scenarios", href='/scenarios/short-term-scenarios'),
                ],
            ),
            dbc.NavItem(dbc.NavLink("Sectors", href="/sectors")),
            dbc.DropdownMenu(
                nav=True,
                in_navbar=True,
                label="Reports",
                children=[
                    dbc.DropdownMenuItem("Overview", href='/reports/report-overview'),
                    dbc.DropdownMenuItem("Generate report", href='/reports/generate-report'),
                    dbc.DropdownMenuItem("Institutional report", href='/reports/institutional-report'),
                    dbc.DropdownMenuItem("Sector report", href='/reports/sector-report'),
                    dbc.DropdownMenuItem("Scenario report", href='/reports/scenario-report'),
                    dbc.DropdownMenuItem("Full report", href='/reports/full-report'),
                ],
            ),
            dbc.NavItem(dbc.NavLink("Charts", href="/charts")),
            dbc.NavItem(dbc.NavLink("FAQs", href="/faqs")),
        ],
        brand=[
            dbc.NavItem(dbc.NavLink("CFRF", href="/"))
        ],
        brand_href="/",
        sticky="top",
        color="dark",
        dark=True,
        expand='xl',
        links_left=True,
        class_name="mb-4",
    )

    return navbar
