import io
import base64

import numpy as np
import pandas as pd
from scipy.optimize import nnls, curve_fit

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input, State

import plotly.graph_objects as go

app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])
# app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True  # NOT WORKING
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
        return html.Div(id="graph-AS")
    elif tab == "AD-tab":
        return html.Div(id="graph-AD")
    elif tab == "NNLS-tab":
        return html.Div(id="graph-NNLS")
    elif tab == "PSD-tab":
        return dcc.Graph(figure=go.Figure([go.Bar(x=[1, 2, 3, 4, 5, 6], y=[2, 5, 3, 2, 0, 1])], go.Layout(dict(title="Particle Size Distribution"))))
    elif tab == "instructions-tab":
        return [html.Img(id="bla", src=app.get_asset_url("demo.gif"), style={"width": 700})]


#FUNCION NUEVA
@app.callback(
    Output("graph-NNLS", "children"),
    [Input("execute-nnls", "n_clicks")]
)
def update_NNLS(click):
    global df_AD
    global df_AS
    global df_PSD
    print("DEBUG: change_focus executed")
    if click:
        df_PSD = df_AD[df_AD.columns[1:]]
        NPsizes_frequency, _ = nnls(df_PSD, df_AS.Absorbance)
        trace_fit = go.Scatter(x=df_AS.Wavelength, y=np.matmul(df_PSD, NPsizes_frequency),
            mode="lines", name="Fit",)
        traces_AD_NNLS = [go.Scatter(x=df_AD.Wavelength, y=df_AD[col]*NPsizes_frequency[df_PSD.columns.get_loc(col)], name=col) for col in df_PSD.columns]
        trace_AS = go.Scatter(x=df_AS.Wavelength, y=df_AS.Absorbance, mode="lines", name="Data")
        traces = [trace_AS, trace_fit, *traces_AD_NNLS]
        layout = go.Layout(
            title="NNLS",
            xaxis=dict(title="Wavelength (nm)"),
            yaxis=dict(title="Absorbance")
        )
        return dcc.Graph(figure=go.Figure(traces, layout))


# FUNBCION ANTERIOR
# @app.callback(
#     [Output("stitching-tabs", "value"),
#      Output("graph-NNLS", "children")],
#     [Input("execute-nnls", "n_clicks")]
# )
# def change_focus(click):
#     print("DEBUG: change_focus executed")
#     if click:
#         df_PSD = df_AD[df_AD.columns[1:]]
#         NPsizes_frequency, _ = nnls(df_PSD, df_AS.Absorbance)
#         trace_fit = go.Scatter(x=df_AS.Wavelength, y=np.matmul(df_PSD, NPsizes_frequency),
#             mode="lines", name="Fit",)
#         traces_AD_NNLS = [go.Scatter(x=df_AD.Wavelength, y=df_AD[col]*NPsizes_frequency[df_PSD.columns.get_loc(col)], name=col) for col in df_PSD.columns]
#         trace_AS = go.Scatter(x=df_AS.Wavelength, y=df_AS.Absorbance, mode="lines", name="Data")
#         traces = [trace_AS, trace_fit, *traces_AD_NNLS]
#         layout = go.Layout(
#             title="NNLS",
#             xaxis=dict(title="Wavelength (nm)"),
#             yaxis=dict(title="Absorbance")
#         )
#         return [
#             "NNLS-tab",
#             dcc.Graph(figure=go.Figure(traces, layout))
#         ]
#     return ["AS-tab", None]


# ABSORPTION SPECTRA


def parse_AS(contents, filename):
    print("DEBUG: parse_AS being executed!")
    global df_AS
    _, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    try:
        if filename.endswith(".csv"):
            df_AS = pd.read_csv(
                io.StringIO(decoded.decode("utf-8"))
            )
        elif filename.endswith(".xls") or filename.endswith(".xlsx"):
            df_AS = pd.read_excel(
                io.BytesIO(decoded)
            )
    except Exception as e:
        print(e)  # TODO: Log? with open append mode datetime now() and exception
        return html.H1(["There was an error processing this file"])
    return dcc.Graph(
        figure = {
            "data": [go.Scatter(x=df_AS.Wavelength, y=df_AS.Absorbance, mode="lines")],
            "layout": {
                "title": "Absorption Spectra",
                "xaxis": dict(title="Wavelength (nm)"),
                "yaxis": dict(title="Absorbance")
            }
        }
    )


@app.callback(
    Output("graph-AS", "children"),
    Input("upload-AS", "contents"),
    State("upload-AS", "filename")
)
def update_AS(contents, filename):
    if contents:
        children = [
            html.H2([f"Using \"{filename}\""], style={"color": "black"}),
            parse_AS(contents, filename)
        ]
    else:
        children = html.H1(["First upload the Absorption Spectra"])
    return children


# ABSORPTION DATABASE


def parse_AD(contents, filename):
    print("DEBUG: parse_AD being executed!")
    global df_AD
    _, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    try:
        if filename.endswith(".csv"):
            df_AD = pd.read_csv(
                io.StringIO(decoded.decode("utf-8"))
            )
            df_AD.columns = ["Wavelength", *df_AD.columns[1:]]
        elif filename.endswith(".xls") or filename.endswith(".xlsx"):
            df_AD = pd.read_excel(
                io.BytesIO(decoded)
            )
            df_AD.columns = ["Wavelength", *df_AD.columns[1:]]
    except Exception as e:
        print(e)  # TODO: Log? with open append mode datetime now() and exception
        return html.H1(["There was an error processing this file"])
    return dcc.Graph(
        figure = {
            "data": [go.Scatter(x=df_AD.Wavelength, y=df_AD[col], mode="lines", name=col) for col in df_AD.columns[1:]],
            "layout": {
                "title": "Absorption Database",
                "xaxis": dict(title="Wavelength (nm)"),
                "yaxis": dict(title="Absorbance")
            }
        }
    )


@app.callback(
    Output("graph-AD", "children"),
    Input("upload-AD", "contents"),
    State("upload-AD", "filename")
)
def update_AD(contents, filename):
    if contents:
        children = [
            html.H2([f"Using \"{filename}\""], style={"color": "black"}),
            parse_AD(contents, filename)
        ]
    else:
        children = html.H1(["Please upload the Absorption Database"])
    return children


# NNLS


# @app.callback(
#     Output("graph-NNLS", "children"),
#     Input("execute-nnls", "n_clicks")
# )
# def update_NNLS(click):
#     if click:



if __name__ == '__main__':
    app.run_server(debug=True, port=5050)
    # app.run_server(debug=True, host="0.0.0.0")
