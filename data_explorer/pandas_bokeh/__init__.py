import pandas as pd
from bokeh.io import curdoc
from bokeh.themes import built_in_themes
from pandas.core.accessor import CachedAccessor
from pandas.core.base import PandasObject

from data_explorer.pandas_bokeh import bokeh

curdoc().theme = 'dark_minimal'


class BasePlotMethods(PandasObject):
    """BasePlotMethods."""

    def __init__(self, data):
        self._parent = data # can be Series or DataFrame

    def __call__(self, *args, **kwargs):
        raise NotImplementedError


class FramePlotMethods(BasePlotMethods):
    """FramePlotMethods."""

    @property
    def df(self):
        dataframe = self._parent

        # Convert PySpark Dataframe to Pandas Dataframe:
        if hasattr(dataframe, "toPandas"):
            dataframe = dataframe.toPandas()

        return dataframe

    def __call__(self, *args, **kwargs):
        return bokeh.plot(self.df, *args, **kwargs)

    __call__.__doc__ = bokeh.plot.__doc__

    def line(self, *args, **kwargs):
        self(kind='line', *args, **kwargs)


ss_plot = CachedAccessor("ss_plot", FramePlotMethods)

pd.DataFrame.ss_plot = ss_plot
pd.Series.ss_plot = ss_plot
