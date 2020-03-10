from data_explorer.pandas_bokeh import plotters
from bokeh.io import output_notebook
from bokeh.plotting import figure

output_notebook()


def plot(df, *args, kind=None, **kwargs) -> figure:
    if not kind or kind == 'line':
        return plotters.line(df, *args, **kwargs)
