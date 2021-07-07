import io
import base64
import pandas as pd

import dash_core_components as dcc
import dash_html_components as html


def plotAS(contents, filename):
    # global AbsorptionSpectrum
    # global flag
    # flag = 1
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if filename.lower().endswith(".csv"):
            # Assume that the user uploaded a CSV file
            df_AS = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif filename.lower().endswith(".xls") or filename.lower().endswith(".xlsx"):
            # Assume that the user uploaded an excel file
            df_AS = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    else:
        return html.Div([
                    dcc.Graph(
                        figure={
                            'data': [
                            {'x': df_AS.iloc[:,0], 'y': df_AS.iloc[:,1], 'type': 'line'},
                            ],
                            'layout': {
                                'title': 'Absorption Spectrum',
                                # 'titlefont' : title_graph_style,
                            'xaxis': {
                                'title': 'Wavelength (nm)',
                                # 'titlefont' : axis_graph_style
                            },
                            'yaxis': {
                                'title': 'Absorption',
                                # 'titlefont' : axis_graph_style
                            },
                            }
                        }
                    )
                ]
        )
