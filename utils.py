import pandas as pd

def extend_list(y_data, sizes, n=10000):  #, scaling=None):
    """
    This function creates a list to be able to plot an histogram
    using the frequencies obtained (y_data).
    'sizes' is the sizes pd.Series from the jacobian file
    """
    # y_hist = y_data.copy().to_list()
    freqs = [round(i/y_data.sum()*n) for i in y_data]
    extended_list = []
    for i, freq in enumerate(freqs):
        if freq == 0:
            continue
        for _ in range(freq):
            # Append the corresponding particle size 'freq' times
            extended_list.append(sizes.iloc[i])
    return pd.Series(extended_list)
