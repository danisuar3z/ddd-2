import base64
import io
import numpy as np
import pandas as pd


# Lognormal function
def lognormal(x, mu, s):
    """
    Standard lognormal function to fit size distribution data
    with optimize.curve_fit.
    """
    return (1/(x*s*np.sqrt(2*np.pi))) * (np.exp(-(((np.log(x/mu))**2)/(2*s**2))))


def load_df(contents, filename, col_names=None):
    """
    Recieves file contents string from Upload component.
    Returns pandas.DataFrame or a string if unsupported file format.
    Supported filetypes: csv, xls, xlsx. Check templates in data folder.
    Parsing: assumes first row is headers and replaces it with
    col_names if passed.
    """
    _, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)

    if filename.endswith(".csv"):
        df = pd.read_csv(
            io.StringIO(decoded.decode("utf-8")),
            names=col_names,
            header=0
        )
    elif filename.endswith(".xls") or filename.endswith(".xlsx"):
        df = pd.read_excel(
            io.BytesIO(decoded),
            names=col_names,
            header=0
        )
    else:
        return "EXT_ERROR"

    return df


def extend_list(y_data, sizes, n=10000):  # , scaling=None):
    """
    This function creates a list to be able to plot an histogram
    using the frequencies obtained (y_data).
    'sizes' is the sizes pd.Series from the jacobian file
    """
    freqs = [round(i/y_data.sum()*n) for i in y_data]
    extended_list = []
    for i, freq in enumerate(freqs):
        if freq == 0:
            continue
        for _ in range(freq):
            # Append the corresponding particle size 'freq' times
            extended_list.append(sizes.iloc[i])
    return pd.Series(extended_list)
