import dash_bootstrap_components as dbc

def create_navbar():
    # Create the Navbar using Dash Bootstrap Components
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Home", href="/")),
            dbc.NavItem(dbc.NavLink("Scenarios", href="/page-13")),
            dbc.NavItem(dbc.NavLink("Chart1", href="/page-11")),
            dbc.NavItem(dbc.NavLink("Chart2", href="/page-12")),
            # dbc.DropdownMenu(
            #     nav=True,
            #     in_navbar=True,
            #     label="More", 
            #     children=[
            #         dbc.DropdownMenuItem("Home", href='/'), 
            #         dbc.DropdownMenuItem(divider=True), 
            #         dbc.DropdownMenuItem("Page 2", href='/page-2'), 
            #         dbc.DropdownMenuItem("Page 3", href='/page-3'), 
            #     ],
            # ),
        ],
        brand="Risk Forum",  
        brand_href="/",  
        sticky="top",  
        color="dark",  
        dark=True,
        # fluid = True  
    )

    return navbar