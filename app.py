import io
import base64
import pathlib
# from dash_core_components.RadioItems import RadioItems

import numpy as np
import pandas as pd
from scipy.optimize import nnls, curve_fit

import dash
from dash_daq import BooleanSwitch
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate

import plotly.graph_objects as go

PATH = pathlib.Path(__file__).parent

app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])
# app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True  # NOT WORKING?
app.title = "DdD 2.0"
# FLAG = 0  # Determines the state of the app in the user instance

def lognormal(x, mu, s):
    return (1/(x*s*np.sqrt(2*np.pi))) * (np.exp(-(((np.log(x/mu))**2)/(2*s**2))))


def instructions():
    return html.A([
        """
        DOI: 10.1039/C9NA00344D"""], href="https://pubs.rsc.org/en/content/articlelanding/2019/na/c9na00344d",
        # style={"margin-left": "2.4vw", "font-family": ["Geneva", "Tahoma", "Verdana", "sans-serif"]})
        className="instructions-sidebar")


app.layout = html.Div(
    children=[
        dcc.Store(id="FLAG", storage_type="memory", data=0),
        html.Div(
            [
                html.Img(
                    src=app.get_asset_url("ga_white.png"), className="ddd-logo"
                    ),
                html.H1(children="Diameter distribution for SNPs", style=dict(color="var(--cremita")),
                instructions(),
                html.Div(
                    [
                        html.Button(
                            f"HOW TO CITE {chr(9660)}",
                            className="button_instruction",
                            id="learn-more-button",
                            ),
                        html.Button(
                            "EXAMPLE DATA?", className="demo_button", id="demo", style={"display": "none"}
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
                                # html.Label("3- Fit"),
                                html.Button(
                                    id="execute-nnls",
                                    children="3- Execute NNLS"),
                            ], className="btn-nnls"
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
                        dbc.Input(
                            id="input-filter", type="number",
                            value=None, min=0, max=10,
                            step=0.05,
                            # step="any",
                            placeholder="E.g. 2,4",
                            style={"width": "10vw"}
                        ),
                        BooleanSwitch(
                            id="switch-filter",
                            on=False,
                            color="#BE4B53",
                            style={"display": "inline-block", "width": "10vh",
                                   "vertical-align": "bottom"}
                        ),
                        html.Label("6- Input value to scale"),
                        dbc.Input(
                            id="input-scale", type="number",
                            value=None, min=0, max=1000,
                            step="any", placeholder="E.g. 30",
                            style={"width": "10vw"}
                        ),
                        BooleanSwitch(
                            id="switch-scale",
                            on=False,
                            color="#BE4B53",
                            style={"display": "inline-block", "width": "10vh",
                                   "vertical-align": "bottom"}
                        )
                    ],
                    ),
                html.Label("7- Download PSD data to CSV file"),
                # html.Div([
                #     # dcc.RadioItems(
                #     dcc.Dropdown(
                #         id="radio-download",
                #         options=[
                #             dict(label="Excel file", value="xlsx"),
                #             dict(label="CSV file", value="csv"),
                #         ],
                #         # labelStyle={'display': 'inline-block'},  # This was for RadioItems
                #         value="xlsx",
                #         # style={
                #         #     'display': 'block', "margin-left": "1.3vw", "padding-bottom": "1vh",
                #         #     # "border": "2px red solid", "padding-top":"0px",
                #         #     # "width": "80%", "font-family": ["Geneva", "Tahoma", "Verdana", "sans-serif"]
                #         # }
                #     ),
                # ], style={"width": "45%", "margin-left": "2.7vw", "padding-bottom": "1vh",
                #           "font-family": ["Geneva", "Tahoma", "Verdana", "sans-serif"]}
                # ),
                dcc.Download(id="download-PSD"),
                html.Button(
                    "Export data", id="btn-download", className="button_submit"
                    ),
                # html.Br(),
            ],
            className="four columns instruction",
        ),
        html.Div([
            dcc.Tabs(id="stitching-tabs",
                     value="instructions-tab",
                     children=[
                         dcc.Tab(label="INSTRUCTIONS", value="instructions-tab"),
                         dcc.Tab(label="ABSORPTION SPECTRA", value="AS-tab"),
                         dcc.Tab(label="ABSORPTION DATABASE", value="AD-tab"),
                         dcc.Tab(label="FIT", value="NNLS-tab"),
                         dcc.Tab(label="PSD", value="PSD-tab"),
                         ], className="tabs"
                     ),
            html.Div(
                id="tabs-content-example",
                className="canvas",
                style={"text-align": "left", "margin": "auto"},
            ),
            html.Div(className="upload_zone", id="upload-stitch", children=[]),
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
        return html.Div(id="graph-PSD")
    elif tab == "instructions-tab":
        return [
            dcc.Download(id="download-template"),
            # html.Br(),
            html.Div([
                html.Button("Download templates", id="btn-template", style={"width": "155px", "background-color": "#2da135"}),
                html.Button("Download sample data", id="btn-sample", style={"width": "170px", "background-color": "#2da135"}),
            ], style={"padding-top": "15px", "padding-bottom": "15px"}),
            dcc.Download(id="download-sample"),
            # html.Br(),
            # html.Label("Demonstration"),
            html.Img(id="demo-gif", src=app.get_asset_url("demo.gif"), style={"width": 700}),]


def demo_explanation():
    # Markdown files
    with open(PATH.joinpath("demo.md"), "r") as file:
        demo_md = file.read()

    return html.Div(
        html.Div([dcc.Markdown(demo_md, className="markdown")]),
        style={"margin": "12px"},
    )


@app.callback(
    [Output("demo-explanation", "children"),
    Output("learn-more-button", "children")],
    [Input("learn-more-button", "n_clicks")],
)
def learn_more(n_clicks):
    if n_clicks is None:
        n_clicks = 0
    if (n_clicks % 2) == 1:
        n_clicks += 1
        return (
            html.Div(
                className="demo_container",
                style={"margin-bottom": "30px"},
                children=[demo_explanation()],
            ),
            f"Close {chr(9650)}",
        )
    n_clicks += 1
    return (html.Div(), f"HOW TO CITE {chr(9660)}")


# OLD CHANGE_FOCUS

@app.callback(
    Output("stitching-tabs", "value"),
    Input("upload-AS", "filename"),
    Input("execute-nnls", "n_clicks"),
    Input("upload-AD", "filename"),
    Input("upload-Jac", "filename"),
    State("FLAG", "data")
)
def change_focus(filename_AS, click, filename_AD, filename_Jac, FLAG):
    print("DEBUG:", FLAG)
    # Return order is key to the correct behavior
    if filename_Jac:
        return "PSD-tab"
    elif click:
        return "NNLS-tab"
    elif filename_AD:
        return "AD-tab"
    elif filename_AS:
        return "AS-tab"
    return "instructions-tab"


# NEW CHANGE_FOCUS

# @app.callback(
#     Output("stitching-tabs", "value"),
#     Input("FLAG", "data"),
#     # State("FLAG", "data")
# )
# def change_focus(FLAG):#, state):
#     print("Changing focus:", FLAG)
#     # return "instructions-tab"
#     # if not FLAG:
#     #     return "instructions-tab"
#     if FLAG == 1:
#         return "AS-tab"
#     return "instructions-tab"
#     # elif FLAG == 2:
#     #     return "AD-tab"
#     # elif FLAG == 3:
#     #     return "NNLS-tab"
#     # elif FLAG == 4:
#     #     return "PSD-tab"


# ABSORPTION SPECTRA


def parse_AS(contents, filename):
    print("DEBUG: parse_AS being executed!")
    global df_AS
    _, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    try:
        if filename.endswith(".csv"):
            df_AS = pd.read_csv(
                io.StringIO(decoded.decode("utf-8")),
                names=["Wavelength", "Absorbance"],
                header=0  # Worst case it drops first row if it doesn't have headers
            )
        elif filename.endswith(".xls") or filename.endswith(".xlsx"):
            df_AS = pd.read_excel(
                io.BytesIO(decoded),
                names=["Wavelength", "Absorbance"],
                header=0  # Worst case it drops first row if it doesn't have headers
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
    [Output("graph-AS", "children"),
    Output("FLAG", "data")],
    [Input("upload-AS", "contents"),
    State("upload-AS", "filename")]
)
def update_AS(contents, filename):
    print("DEBUG: CORRIENDO update_AS")
    if not contents:
        raise PreventUpdate
    elif contents:
        children = [
            html.H6([f"Using \"{filename}\""]),
            parse_AS(contents, filename)
        ]
        print("Debería estar cambiando el FLAG a 1")
        FLAG = 1
    else:
        children = [html.H1(["Please upload the Absorption Spectra with"]),
                    html.H1(["only two columns: wavelength and absorbance"])
        ]
        FLAG = 0
    return children, FLAG


# ABSORPTION DATABASE


def parse_AD(contents, filename):
    print("DEBUG: parse_AD being executed!")
    global df_AD
    _, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    try:
        if filename.endswith(".csv"):
            df_AD = pd.read_csv(
                io.StringIO(decoded.decode("utf-8")),
                header=0
            )
            
        elif filename.endswith(".xls") or filename.endswith(".xlsx"):
            df_AD = pd.read_excel(
                io.BytesIO(decoded),
                header=0
            )
    except Exception as e:
        print(e)  # TODO: Log? with open append mode datetime now() and exception
        return html.H1(["There was an error processing this file"])
    df_AD.columns = ["Wavelength", *df_AD.columns[1:]]
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
    print("DEBUG: CORRIENDO update_AD")
    if contents:
        children = [
            html.H6([f"Using \"{filename}\""]),
            parse_AD(contents, filename)
        ]
    else:
        children = [html.H1(["Please upload the Absorption Database with"]),
                    html.H1(["wavelength and the diameters in header"]),
                    html.H1(["using dot separator"]),
        ]
    return children


# NNLS


@app.callback(
    Output("graph-NNLS", "children"),
    [Input("execute-nnls", "n_clicks")]
)
def update_NNLS(click):
    global df_AD
    global df_AS
    global df_NNLS
    global NPsizes_frequency
    print("DEBUG: update_NNLS executed")
    if click:
        df_NNLS = df_AD[df_AD.columns[1:]]
        NPsizes_frequency, _ = nnls(df_NNLS, df_AS.Absorbance)
        trace_fit = go.Scatter(x=df_AS.Wavelength, y=np.matmul(df_NNLS, NPsizes_frequency),
            mode="lines", name="Fit",)
        traces_AD_NNLS = [go.Scatter(x=df_AD.Wavelength, y=df_AD[col]*NPsizes_frequency[df_NNLS.columns.get_loc(col)], name=col) for col in df_NNLS.columns]
        trace_AS = go.Scatter(x=df_AS.Wavelength, y=df_AS.Absorbance, mode="lines", name="Data")
        traces = [trace_AS, trace_fit, *traces_AD_NNLS]
        layout ={
                "title": "Absorption Spectra",
                "xaxis": dict(title="Wavelength (nm)"),
                "yaxis": dict(title="Absorbance")
            }
        return dcc.Graph(figure={"data": traces, "layout": layout})
    else:
        return [html.H1("First upload Absorption Spectra and Database,"),
                html.H1("then click EXECUTE NNLS"),
        ]


# PSD

def parse_Jac(contents, filename, filter_on, filter_value, scale_on, scale_value):
    global df_Jac
    global NPsizes_frequency
    global y_data
    print("DEBUG: parse_Jac being executed!")
    _, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    try:
        if filename.endswith(".csv"):
            df_Jac = pd.read_csv(
                io.StringIO(decoded.decode("utf-8")),
                names=["Size", "J"],
                header=0,  # It may drop the first row if it hasn't headers
            )
        elif filename.endswith(".xls") or filename.endswith(".xlsx"):
            df_Jac = pd.read_excel(
                io.BytesIO(decoded),
                names=["Size", "J"],
                header=0,  # It may drop the first row if it hasn't headers
            )
    except Exception as e:
        print(e)  # TODO: Log? with open append mode datetime now() and exception
        return html.H1(["There was an error processing this file"])
    fit_x_values = np.linspace(min(df_Jac['Size']), max(df_Jac['Size']), 50)
    y_data = NPsizes_frequency*df_Jac["J"]
    y_data /= y_data.max()
    if filter_on:
        for i in df_Jac["Size"].index:
            if df_Jac["Size"].iloc[i] < filter_value:
                y_data.iloc[i] = 0
            elif scale_on:
                y_data.iloc[i] *= scale_value
    else:
        if scale_on:
            for i in df_Jac["Size"].index:
                y_data.iloc[i] *= scale_value
    params, _ = curve_fit(lognormal, df_Jac["Size"], y_data)
    traces = [
        go.Bar(x=df_Jac["Size"], y=y_data, name="DdD"),
        go.Scatter(x=fit_x_values, y=lognormal(fit_x_values, params[0], params[1]), name="Lognormal fit")
    ]
    mean = np.exp(np.log(params[0]) + 0.5*params[1]*params[1])
    dev = np.exp(np.log(params[0]) + 0.5*params[1]*params[1]) * np.sqrt(np.exp(params[1]*params[1]) - 1)
    annotation_mean = {
        "x": 4/5*df_Jac["Size"].max(),
        "y": 4/5*y_data.max(),
        "text": f"Mean = {mean:.2f} nm",
        "showarrow": False,
        "font": {"size": 25, "color": "black"}
    }
    annotation_dev = {
        "x": 4/5*df_Jac["Size"].max(),
        "y": 5/7*y_data.max(),
        "text": f"Deviation = {dev:.2f} nm",
        "showarrow": False,
        "font": {"size": 25, "color": "black"}
    }
    return dcc.Graph(
        figure={
            "data": traces,
            "layout": go.Layout(
                title="Particle Size Distribution by DdD",
                xaxis=dict(title="Particle size (nm)"),
                annotations=[annotation_mean, annotation_dev]
            )
        }
    )


@app.callback(
    Output("graph-PSD", "children"),
    Input("upload-Jac", "contents"),
    Input("switch-filter", "on"),
    Input("input-filter", "value"),
    Input("switch-scale", "on"),
    Input("input-scale", "value"),
    State("upload-Jac", "filename"),
)
def update_Jac(contents, filter_on, filter_value, scale_on, scale_value, filename):
    print("DEBUG: FILTER VALUE:", filter_value)
    if contents:
        try:
            children = [
                html.H6([f"Using \"{filename}\""]),
                parse_Jac(contents, filename, filter_on, filter_value, scale_on, scale_value)
            ]
        except Exception as e:
            print(e)
            children = [html.H1("There was an error."),
                        html.H1("Make sure your Jacobian file has headers")
            ]
    else:
        children = [html.H1(["Please upload the Jacobian file with"]),
                    html.H1(["only two columns: Size and J value"])
        ]
    return children


# EXPORT

@app.callback(
    Output("download-PSD", "data"),
    Input("btn-download", "n_clicks"),
    # State("radio-download", "value")
)
def download_df(click):
    if click is None:
        raise PreventUpdate
    print("DEBUG: CORRIENDO download_df")
    global df_Jac
    global y_data
    # print(y_data)
    df = pd.DataFrame(data=dict(freq=y_data.values), index=df_Jac["Size"])
    df.index.name = "diameter"
    # print(df)
    if click:
        # if type == "xlsx":
        #     return dcc.send_data_frame(df.to_excel, "PSD_data.xlsx")
        # elif type == "csv":
        return dcc.send_data_frame(df.to_csv, "PSD_data.csv")


@app.callback(
    Output("download-template", "data"),
    Input("btn-template", "n_clicks")
)
def download_template(click):
    if click is None:
        raise PreventUpdate
    return dcc.send_file(PATH / "data" / "templates.zip")


@app.callback(
    Output("download-sample", "data"),
    Input("btn-sample", "n_clicks")
)
def download_sample(click):
    if click is None:
        raise PreventUpdate
    return dcc.send_file(PATH / "data" / "sample_data.zip")


if __name__ == '__main__':
    app.run_server(debug=True, port=5050)
    # app.run_server(host="0.0.0.0", debug=True)
