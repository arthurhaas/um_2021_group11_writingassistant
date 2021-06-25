import dash
# instead of dash for jupyter: from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash_html_components.Button import Button
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import requests
import pandas as pd



app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)
# for jupyter: app = JupyterDash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv')

app.layout = dbc.Container(
    fluid=False,
    children=[
        dbc.Jumbotron(
        [
            html.H1("Writing Assistant", className="display-3"),
            html.P(
                "Apply text style transfer models to  "
                "improve the scientificity.",
                className="lead",
            ),
            html.Hr(className="my-2"),
            html.P(
                "Researched and developed by Master Research Project group 11 "
                "at Maastricht University."
            ),
            html.P(dbc.Button("Learn more", color="primary",
                href="https://www.maastrichtuniversity.nl/meta/415976/research-project-dsdm-1",
                target="new_tab"
                ),
            className="lead"),
        ]),
        dbc.InputGroup(
            [
                dbc.InputGroupAddon("Model Options", addon_type="prepend"),
                dbc.Select(
                    id="model-options",
                    options=[
                        {"label": "Option 1", "value": "1"},
                        {"label": "Option 2", "value": "2"},
                        {"label": "Disabled option", "value": "3", "disabled": True},
                    ],
                    value="1",
                )
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Textarea(
                            id="source-text",
                            style={"margin-top": "15px", "height": "65vh"},
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        dbc.Textarea(
                            id="target-text",
                            style={"margin-top": "15px", "height": "65vh"},
                        ),
                    ]
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Button("Translate", id="button-translate", className="mr-2"),
                    ]
                )
            ]
        ),
        html.H3("Quality measures of the model's result of the model."),
        dcc.Graph(id='graph-with-slider'),
        dcc.Slider(
            id='year-slider',
            min=df['year'].min(),
            max=df['year'].max(),
            value=df['year'].min(),
            marks={str(year): str(year) for year in df['year'].unique()},
            step=None
        )
    ]
)



@app.callback(
    Output(component_id='target-text', component_property='value'),
    Input(component_id='button-translate', component_property='n_clicks'),
    State(component_id='source-text', component_property='value'),
)
def update_output_div(n_clicks,input_value):
    resp = requests.get("https://www.google.com")
    print(resp.status_code)
    return input_value


@app.callback(
    Output('graph-with-slider', 'figure'),
    Input('year-slider', 'value'))
def update_figure(selected_year):
    filtered_df = df[df.year == selected_year]

    fig = px.scatter(filtered_df, x="gdpPercap", y="lifeExp",
                     size="pop", color="continent", hover_name="country",
                     log_x=True, size_max=55)

    fig.update_layout(transition_duration=500)

    return fig



if __name__ == "__main__":
    app.run_server(debug=True)