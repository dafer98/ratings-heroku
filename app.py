import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.figure_factory as ff
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from imdb import IMDb
import numpy as np
import itertools

app = dash.Dash(external_stylesheets=[dbc.themes.LUX])
server = app.server
"""Navbar"""
nav_item = dbc.NavItem(dbc.NavLink('IMDb database', href='https://www.imdb.com/'))
dropdown = dbc.DropdownMenu(children=
    [
        dbc.DropdownMenuItem('Github', href='https://github.com/dafer98'),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem('Plotly / Dash', href='https://dash.plot.ly/')
    ],
    nav=True,
    in_navbar=True,
    label='Important Links'
)
navbar = dbc.Navbar(
    dbc.Container(
    [
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(dbc.NavbarBrand("Series Visualizer", className="ml-2")),
                ],
                align="left",
                no_gutters=True,
            ),
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(dbc.Nav([nav_item, dropdown], className='ml-auto', navbar=True),id="navbar-collapse", navbar=True),
    ],
    ),
    color="dark",
    dark=True,
    className='mb-5'
)
"""Navbar End"""

ia = IMDb()


def get_show_info(input_data):
    search = ia.search_movie(input_data)
    series = ia.get_movie(search[0].movieID)
    ia.update(series, 'episodes')
    keys = sorted(series['episodes'].keys())
    filtered = ['season' + str(item) for item in keys if item > 0]
    ratings = []
    dictionary = {}

    for i in range(1, len(filtered) + 1):
        print(i)
        for x in range(1, len(series['episodes'][i]) + 1):
            try:
                episode = series['episodes'][i][x]
                ratings.append(episode['rating'])
            except Exception:
                pass
        print(ratings)
        if not ratings:
            pass
        else:
            dictionary[filtered[i - 1]] = ratings
            ratings = []

    nest = [x for x in dictionary.values()]

    ratings_for_seasons = pd.DataFrame(data=(_ for _ in itertools.zip_longest(*nest)),
                                       columns=list(dictionary.keys()))

    ratings_for_seasons.index += 1

    data = [ratings_for_seasons['season' + str(x)].tolist() for x in \
            range(1, len(ratings_for_seasons.columns) + 1)]

    nan_removed = np.around(data, 1)
    nan_removed = np.where(np.isnan(nan_removed), '', nan_removed).tolist()
    # max_val = np.max(nan_removed)
    # mid_val = np.average(nan_removed)
    # min_val = np.nanmin(data)

    return ratings_for_seasons, data, nan_removed


def create_heatmap(data, ratings, name, nan_removed):
    fig = ff.create_annotated_heatmap(
        z=data,
        x=list(np.arange(1, len(ratings) + 1)),
        y=list(ratings.columns.values),
        annotation_text=nan_removed,
        font_colors=['black'],
        colorscale='RdYlGn',
        showscale=True
    )

    fig.update_yaxes(autorange="reversed")

    fig.update_layout(
        title=dict(text="Heatmap of {} episodes rating by season".format(name),
                   x=.5,
                   y=1),
        xaxis=dict(title="Episodes",
                   tickmode='linear',
                   position=1,
                   showgrid=False,
                   zeroline=False,
                   showline=False),
        yaxis=dict(title="Seasons",
                         showgrid=False,
                         zeroline=False,
                         showline=False),
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="#7f7f7f"
        ),
        height=700,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig


"""App Body"""

text_input = dbc.FormGroup(
    [
        dbc.Label("Enter Show Name:"),
        dbc.Input(id='input1', placeholder="", type="text", debounce=True, style={'width': "20%"}),
    ]
)

button = html.Div(
    [
        text_input,
        dbc.Button("Click me", id="example-button", className="mr-2"),
        html.Span(id="example-output", style={'width': "20%"}),
    ],
    style={'margin-left': '5%'}
)

"""End App Body"""

"""Final Layout Render"""
app.layout = html.Div(children=[
    navbar,
    html.H1(button),
    dcc.Loading(
            id="loading-1",
            type="default",
            children=html.Div(id='output',
                              style={'display': 'inline-block', 'width': '100%'})
        ),
])
"""App Callback"""


@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output('output', 'children'),
    [dash.dependencies.Input('input1', 'value'),
     Input('input1', 'value')]
)
def update_graph(value, _):

    ratings_for_seasons, data, nan_removed = get_show_info(value)

    fig = create_heatmap(data, ratings_for_seasons, value, nan_removed)

    return dcc.Graph(
        id='out-graph',
        figure=fig
    )

# @app.callback(
#     Output("example-output", "children"), [Input("example-button", "n_clicks")]
# )
# def on_button_click(n):
#     if n is None:
#         return "Not clicked."
#     else:
#         return f"Clicked {n} times."


"""End App Callback"""

if __name__ == '__main__':
    app.run_server(debug=True)