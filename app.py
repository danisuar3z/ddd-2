# Utility imports
# import io
# import base64
import pathlib

# Science imports
import numpy as np
import pandas as pd
from scipy.optimize import nnls, curve_fit
import plotly.graph_objects as go

# Web imports
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash_daq import BooleanSwitch
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate

# Project imports
from utils import lognormal, load_df, extend_list

PATH = pathlib.Path(__file__).parent

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)

# Server variable for heroku deployment
server = app.server

# To avoid "ID not found in layout" errors due to nested callbacks
app.config.suppress_callback_exceptions = True

# Browser tab name
app.title = "DdD 2.0"


# Web layout
app.layout = html.Div(
    children=[
        html.Div(
            [
                html.Div([
                    html.Img(src=app.get_asset_url("ddd.png"), className="ddd-logo"),
                    html.Img(src=app.get_asset_url("conicet_blanco.png"), className="conicet-logo"),
                    html.Img(src=app.get_asset_url("exactas_blanco.png"), className="exactas-logo"),
                ]),
                html.H1(children="Diameter distribution by Deconvolution for SNPs", style=dict(color="var(--creamy")),
                html.A([
                    """
                DOI: XX.XXXX/XXXXXXXX"""], href="https://pubs.rsc.org/en/content/articlelanding/2019/na/c9na00344d",
                    className="instructions-sidebar"),
                html.Div(
                    [
                        html.Button(
                            f"HOW TO CITE {chr(9660)}",
                            className="button_instruction",
                            id="learn-more-button",
                            ),
                        html.Button(
                            f"ABOUT DdD {chr(9660)}",
                            className="about-ddd",
                            id="btn-about",
                            ),
                        ],
                    className="mobile_buttons",
                    ),
                html.Div([
                    # Empty child function for the callback
                    html.Div(id="demo-explanation", children=[]),
                    html.Div(id="div-about", children=[])
                ]),
                html.Div(
                    [
                        html.A(
                            html.Button(
                                ["Start again"],
                                className="button_instruction start",
                                style={"background-color": "green", "margin-top": "2%"}
                            ),
                            href="/"
                        ),
                        html.Div(
                            [
                                html.Label("1- Upload Absorption Spectra", id="uno"),
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
                        html.Label("5- Input threshold to filter from left (nm)"),
                        dbc.Input(
                            id="input-filter", type="number",
                            value=None, min=0, max=10,
                            step=0.05,
                            # step="any",
                            placeholder="E.g. 2,4",
                            style={"width": "10vw"},
                            className="my_inputs"
                        ),
                        BooleanSwitch(
                            id="switch-filter",
                            on=False,
                            color="#BE4B53",
                            style={"display": "inline-block", "width": "10vh",
                                   "vertical-align": "bottom"}
                        ),
                        html.Label("6- Bin size for histogram", id="binsize"),
                        dbc.Input(
                            id="input-binsize", type="number",
                            value=0.35, min=0, max=1000,
                            step="any",  # placeholder="E.g. 0,25",
                            style={"width": "10vw"},
                            className="my_inputs"
                        ),
                        html.Label("7- Input value to scale (only for export)"),
                        dbc.Input(
                            id="input-scale", type="number",
                            value=None, min=0, max=1000,
                            step="any", placeholder="E.g. 30",
                            style={"width": "10vw"},
                            className="my_inputs"
                        ),
                        BooleanSwitch(
                            id="switch-scale",
                            on=False,
                            color="#BE4B53",
                            style={"display": "inline-block", "width": "10vh",
                                   "vertical-align": "bottom"}
                        ),
                        html.Label("8- Download PSD data to CSV file", id="ocho"),
                        dcc.Download(id="download-PSD"),
                        html.Button(
                            "Export data", id="btn-download", className="button_submit"
                            ),
                    ],
                    ),
                html.Div(["Web by ", html.A("Daniel T. Suárez", href="https://github.com/danisuar3z")],
                         style={"margin-left": "10%", "font-family": ["Geneva", "Tahoma", "Verdana", "sans-serif"],
                                "display": "none"})
            ],
            className="four columns instruction",
        ),
        html.Div([
            dcc.Tabs(id="stitching-tabs",
                     value="instructions-tab",
                     children=[
                         dcc.Tab(label="HOW TO USE", value="instructions-tab"),
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
    """
    Renders tab content when value of dcc.Tabs changes by click
    or change_focus function.
    """
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
            html.Div([
                html.Button(
                    [html.Img(src=app.get_asset_url("download.png"), className="download-icon"),
                     " Download templates"],
                    id="btn-template", style={"width": "160px", "background-color": "#2da135"},
                    className="btn-down-help",
                ),
                html.Button(
                    [html.Img(src=app.get_asset_url("download.png"), className="download-icon"),
                     " Download sample data"],
                    id="btn-sample", style={"width": "175px", "background-color": "#2da135"},
                    className="btn-down-help",
                ),
            ], style={"padding-top": "15px", "padding-bottom": "15px"}),
            dcc.Download(id="download-sample"),
            html.H1("Example animation", style={"margin-left": "2%", "color": "black"}),
            html.Img(id="demo-gif", src=app.get_asset_url("demo.gif"), className="demo-gif"),
        ]


def demo_explanation(name):
    """
    Loads markdown file and returns it in a Div.
    """
    with open(PATH.joinpath(name), "r") as file:
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
    """
    Simulates collapsable component adding the markdown text from
    demo_explanation.
    """
    if n_clicks is None:
        n_clicks = 0
    if (n_clicks % 2) == 1:
        n_clicks += 1
        return (
            html.Div(
                className="demo_container",
                style={"margin-bottom": "30px"},
                children=[demo_explanation("howtocite.md")],
            ),
            f"Close {chr(9650)}",
        )
    n_clicks += 1
    return (html.Div(), f"HOW TO CITE {chr(9660)}")


@app.callback(
    [Output("div-about", "children"),
     Output("btn-about", "children")],
    [Input("btn-about", "n_clicks")],
)
def about(n_clicks):
    """
    Simulates collapsable component adding the markdown text from
    demo_explanation.
    """
    if n_clicks is None:
        n_clicks = 0
    if (n_clicks % 2) == 1:
        n_clicks += 1
        return (
            html.Div(
                className="demo_container",
                style={"margin-bottom": "30px"},
                children=[demo_explanation("about.md")],
            ),
            f"Close {chr(9650)}",
        )
    n_clicks += 1
    return (html.Div(), f"ABOUT DdD {chr(9660)}")


# CHANGE_FOCUS

@app.callback(
    Output("stitching-tabs", "value"),
    Input("upload-AS", "filename"),
    Input("execute-nnls", "n_clicks"),
    Input("upload-AD", "filename"),
    Input("upload-Jac", "filename"),
)
def change_focus(filename_AS, click, filename_AD, filename_Jac):
    """
    Brings focus to the needed tab given the user inputs (file uploads,
    button presses).
    """
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


# ABSORPTION SPECTRA


def parse_AS(contents, filename):
    """
    Reads file uploaded from the user and parses it into a pandas
    DataFrame, then uses it to graph the absorption spectrum.
    Returns dcc.Graph with figure in it.
    """
    print("DEBUG: parse_AS being executed!")
    global df_AS

    try:
        df_AS = load_df(contents, filename, ["Wavelength", "Absorbance"])
    except Exception as e:
        print(e)  # TODO: Log? with open append mode --> datetime now() and exception
        return html.H1(["There was an error processing this file. Please check metadata required and templates provided."])
    if type(df_AS) == str:
        return html.H1("Only csv, xls and xlsx are supported.")
    return dcc.Graph(
        figure={
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
    [Input("upload-AS", "contents"),
     State("upload-AS", "filename")]
)
def update_AS(contents, filename):
    """
    Called when the user uploads absorption file and calls parse_AS
    to make and put the graph in the respective graph div.
    """
    print("DEBUG: CORRIENDO update_AS")
    if contents:
        children = [
            html.H6([f"Using \"{filename}\""]),
            parse_AS(contents, filename)
        ]
    else:
        children = [html.H1(["Please upload the Absorption Spectra with"]),
                    html.H1(["the specified format first"])
                    ]
    return children


# ABSORPTION DATABASE


def parse_AD(contents, filename):
    """
    Reads file uploaded from the user and parses it into a pandas
    DataFrame, then uses it to graph the database spectra.
    Returns dcc.Graph with figure in it.
    """
    print("DEBUG: parse_AD being executed!")
    global df_AD

    try:
        df_AD = load_df(contents, filename)
    except Exception as e:
        print(e)  # TODO: Log? with open append mode --> datetime now() and exception
        return html.H1(["There was an error processing this file. Please check metadata required and templates provided."])
    if type(df_AD) == str:
        return html.H1("Only csv, xls and xlsx are supported.")

    df_AD.columns = ["Wavelength", *df_AD.columns[1:]]

    return dcc.Graph(
        figure={
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
    """
    Called when the user uploads database file and calls parse_AD
    to make and put the graph in the respective graph div.
    """
    print("DEBUG: CORRIENDO update_AD")
    if contents:
        children = [
            html.H6([f"Using \"{filename}\""]),
            parse_AD(contents, filename)
        ]
    else:
        children = [html.H1(["Please upload the Absorption Database with"]),
                    html.H1(["the specified format first"]),
                    ]
    return children


# NNLS


@app.callback(
    Output("graph-NNLS", "children"),
    Input("execute-nnls", "n_clicks"),
    Input("upload-AS", "filename"),
    Input("upload-AD", "filename")
)
def update_NNLS(click, fn_AS, fn_AD):
    """
    Fits the data with non-negative least squares method
    and generates graph to return in the respective div.
    """
    global df_AD
    global df_AS
    global df_NNLS
    global NPsizes_frequency
    print("DEBUG: update_NNLS executed")
    if click and fn_AS and fn_AD:  # Workaround to the global vars problem

        # Dimension check. AS and AD should have same amount of rows
        if df_AS.shape[0] != df_AD.shape[0]:
            return html.H1(
                children=[
                    "Bad dimensions. Absorption Spectrum and Database should have the same amount of rows.",
                    html.Br(),
                    "Please check your files (and templates given) and upload again."
                ]
            )

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

def parse_Jac(contents, filename, filter_on, filter_value, bin_size):
    """
    Reads file uploaded from the user and parses it into a pandas
    DataFrame, then uses it to graph the PSD.
    Returns dcc.Graph with figure in it.
    """
    global df_Jac
    global NPsizes_frequency
    global y_data
    global extended_size
    print("DEBUG: parse_Jac being executed!")

    try:
        df_Jac = load_df(contents, filename, ["Size", "J"])
    except Exception as e:
        print(e)
        return html.H1(["There was an error processing this file. Please check metadata required and templates provided."])

    if type(df_Jac) == str:
        return html.H1("Only csv, xls and xlsx are supported.")

    # Dimensions check (Jac values should match AD columns, ergo match NPsizes_frequency)
    if df_Jac.shape[0] != NPsizes_frequency.shape[0]:
        return html.H1(
            ["Bad dimensions. Jacobian values should match the database columns.",
             html.Br(),
             f"Amount of known sizes in your database: {NPsizes_frequency.shape[0]}",
             html.Br(),
             f"Amount of values in your Jacobian file: {df_Jac.shape[0]}",
             html.Br(),
             f"Please check your files (and templates provided) and upload again."]
        )

    fit_x_values = np.linspace(df_Jac['Size'].min(), df_Jac['Size'].max(), 50)
    y_data = NPsizes_frequency*df_Jac["J"]
    y_data /= y_data.max()

    if filter_on:
        for i in df_Jac["Size"].index:
            if df_Jac["Size"].iloc[i] < filter_value:
                y_data.iloc[i] = 0

    params, _ = curve_fit(lognormal, df_Jac["Size"], y_data)
    y_fit = lognormal(fit_x_values, params[0], params[1])

    # Convert the data to use histogram
    extended_size = extend_list(y_data, df_Jac.Size)

    factor = extended_size.value_counts().iloc[0]/extended_size.shape[0]

    trace_hist = go.Histogram(
        x=extended_size, name="PSD by DdD",
        histnorm="probability", xbins={"size": bin_size},
        marker_line_width=1,
    )
    traces = [
        trace_hist,
        go.Scatter(
            x=fit_x_values, y=y_fit*factor,
            name="Lognormal fit")
    ]

    mean = np.exp(np.log(params[0])+0.5*params[1]*params[1])
    dev = np.exp(np.log(params[0])+0.5*params[1]*params[1])*np.sqrt(np.exp(params[1]*params[1])-1)

    annotation_mean = {
        "x": 4/5*df_Jac["Size"].max(),
        "y": 4.1/5*y_data.max()*factor,
        "text": f"Mean = {mean:.2f} nm",
        "showarrow": False,
        "font": {"size": 25, "color": "black"}
    }
    annotation_dev = {
        "x": 4/5*df_Jac["Size"].max(),
        "y": 4.9/7*y_data.max()*factor,
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
                yaxis=dict(title="Density distribution"),
                annotations=[annotation_mean, annotation_dev]
            )
        }
    )


@app.callback(
    Output("graph-PSD", "children"),
    Input("upload-Jac", "contents"),
    Input("switch-filter", "on"),
    Input("input-filter", "value"),
    Input("input-binsize", "value"),
    Input("upload-AS", "filename"),
    Input("upload-AD", "filename"),
    State("upload-Jac", "filename"),
)
def update_Jac(contents, filter_on, filter_value, bin_size, fn_AS, fn_AD, filename):
    """
    Called when the user uploads jacobian file and calls parse_Jac
    to make and put the graph in the respective graph div.
    """
    print("DEBUG: FILTER VALUE:", filter_value)
    print("DEBUG: BIN SIZE:", bin_size)
    if contents and fn_AS and fn_AD:  # Workaround to the global vars problem
        try:
            psd_graph = parse_Jac(contents, filename, filter_on, filter_value, bin_size)
            children = [
                html.H6([f"Using \"{filename}\""]),
                psd_graph
            ]
        except Exception as e:
            print("update_Jac:", e)
            children = [html.H1("There was an error."),
                        html.H1("Please check metadata required and templates provided.")
                        ]
    else:
        children = [html.H1(["Please upload the Jacobian file with"]),
                    html.H1(["the specified format first."])
                    ]
    return children


# EXPORT

@app.callback(
    Output("download-PSD", "data"),
    Input("btn-download", "n_clicks"),
    State("switch-scale", "on"),
    State("input-scale", "value"),
)
def download_df(click, scale_on, scale_value):
    """
    Sends the PSD data to a Download component when
    export button is clicked.
    """
    if click is None:
        raise PreventUpdate
    print("DEBUG: CORRIENDO download_df")
    global y_data
    if scale_on:
        data = y_data/y_data.sum()*scale_value
    else:
        data = y_data/y_data.sum()
    df = pd.DataFrame(data=dict(freq=data.values), index=df_Jac["Size"])
    df.index.name = "size"
    if click:
        return dcc.send_data_frame(df.to_csv, "PSD_data.csv")


@app.callback(
    Output("download-template", "data"),
    Input("btn-template", "n_clicks")
)
def download_template(click):
    """
    Sends the templates.zip file to the Download component
    when the respective button is clicked
    """
    if click:
        return dcc.send_file(PATH / "data" / "templates.zip")


@app.callback(
    Output("download-sample", "data"),
    Input("btn-sample", "n_clicks")
)
def download_sample(click):
    """
    Sends the sample_data.zip file to the Download component
    when the respective button is clicked
    """
    if click is None:
        raise PreventUpdate
    return dcc.send_file(PATH / "data" / "sample_data.zip")


if __name__ == '__main__':
    app.run_server(port=5050, debug=True)
    # app.run_server(host="0.0.0.0", debug=True)
