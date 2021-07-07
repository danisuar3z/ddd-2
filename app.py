import numpy as np

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input, State

import plotly.graph_objects as go

app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])
# app = dash.Dash(__name__)
app.title = "DdD 2.0"


def instructions():
    return html.P([
        """
        - blabla
        - blabla"""],
        className="instructions-sidebar")


app.layout = html.Div(
    children=[
        html.Div(
            [
                html.Img(
                    src=app.get_asset_url("ga_white.png"), className="plotly-logo"
                    ),
                html.H1(children="DDD for SNPs"),
                instructions(),
                html.Div(
                    [
                        html.Button(
                            "LINK AL PAPER?",
                            className="button_instruction",
                            id="learn-more-button",
                            ),
                        html.Button(
                            "BOTON AL PEDO", className="demo_button", id="demo"
                            ),
                        ],
                    className="mobile_buttons",
                    ),
                html.Div(
                    # Empty child function for the callback
                    html.Div(id="demo-explanation", children=[])
                    ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Label("1- Upload Absorption Spectra"),
                                dcc.Upload(
                                    id="upload-AS",
                                    children=html.Div([
                                        'Drag and Drop or ',
                                        html.A('Select Files'), ],
                                        ),
                                    multiple=False,
                                    className="dcc_upload"),
                                ]
                            ),
                        html.Div(
                            [
                                html.Label("2- Upload Absorption Database"),
                                dcc.Upload(
                                    id="upload-AD",
                                    children=html.Div([
                                        'Drag and Drop or ',
                                        html.A('Select Files'), ],
                                        ),
                                    multiple=False,
                                    className="dcc_upload"),
                                ]
                            ),
                        html.Div(
                            [
                                html.Button(
                                    id="execute-nnls",
                                    children="3- Execute NNLS"),
                            ], style={"padding-top": 10, }
                            ),
                        html.Div(
                            [
                                html.Label("4- Upload Jacobian"),
                                dcc.Upload(
                                    id="upload-Jac",
                                    children=html.Div([
                                        'Drag and Drop or ',
                                        html.A('Select Files'), ],
                                        ),
                                    multiple=False,
                                    className="dcc_upload"),
                                ]
                            ),
                        ],
                    className="mobile_forms",
                    ),
                html.Div(
                    [
                        html.Hr(),
                        html.Label("5- Input treshold to filter (in nm)"),
                        dcc.Input(
                            id="overlap-stitch", type="number", value=2.45, min=0, max=10
                        ),
                        dcc.Checklist(
                            id="filter-data",
                            options=[{"label": "Filter data", "value": 1}],
                            value=[0],
                        ),
                    ],
                    ),
                html.Label("6- Export PSD data to .csv file"),
                # html.Br(),
                html.Button(
                    "Export data", id="button-stitch", className="button_submit"
                    ),
                html.Br(),
            ],
            className="four columns instruction",
        ),
        html.Div([
            dcc.Tabs(id="stitching-tabs",
                     value="AS-tab",
                     children=[
                         dcc.Tab(label="ABSORPTION SPECTRA", value="AS-tab"),
                         dcc.Tab(label="ABSORPTION DATABASE", value="AD-tab"),
                         dcc.Tab(label="FIT", value="NNLS-tab"),
                         dcc.Tab(label="PSD", value="PSD-tab"),
                         dcc.Tab(label="INSTRUCTIONS", value="instructions-tab"),
                         ], className="tabs"
                     ),
            html.Div(
                id="tabs-content-example",
                className="canvas",
                style={"text-align": "left", "margin": "auto"},
            ),
            html.Div(className="upload_zone", id="upload-stitch", children=[]),
            # dcc.Graph(id="tab-graph")
        ], className="eight columns result",)
    ], className="row twelve columns",

)


@app.callback(
    Output("upload-stitch", "children"),
    Input("stitching-tabs", "value")
)
def render_content(tab):
    if tab == "AS-tab":
        return dcc.Graph(figure=go.Figure(
            [go.Scatter(x=[1, 2, 3], y=[1, 4, 9], mode="lines")],
            go.Layout(dict(title="Absorption Spectra"), xaxis=dict(title="Wavelength (nm)"))
        ))
    elif tab == "AD-tab":
        return dcc.Graph(figure=go.Figure(
            [go.Scatter(x=[1, 2, 3], y=np.array([1, 4, 9])*i, mode="lines") for i in range(10)],
            go.Layout(dict(title="Absorption Database"), xaxis=dict(title="Wavelength (nm)"))
        ))
    elif tab == "PSD-tab":
        return dcc.Graph(figure=go.Figure([go.Bar(x=[1, 2, 3, 4, 5, 6], y=[2, 5, 3, 2, 0, 1])], go.Layout(dict(title="Particle Size Distribution"))))
    elif tab == "instructions-tab":
        return [html.Img(id="bla", src=app.get_asset_url("demo.gif"), style={"width": 700})]
    elif tab == "NNLS-tab":
        return dcc.Graph(figure=go.Figure(
            [go.Scatter(x=[1, 2, 3], y=np.array([1, 4, 9])*i, mode="lines") for i in range(10)]+[go.Scatter(x=[1,2,3], y=[20, 40, 60], mode="lines", name="fitted")],
            go.Layout(dict(title="Absorption Database"), xaxis=dict(title="Wavelength (nm)"))
        ))


@app.callback(Output("stitching-tabs", "value"), [Input("execute-nnls", "n_clicks")])
def change_focus(click):
    if click:
        return "PSD-tab"
    return "AS-tab"


# @app.callback(
#     Output()
# )


if __name__ == '__main__':
    # app.run_server(debug=True, port=5050)
    app.run_server(debug=True, host="0.0.0.0")
