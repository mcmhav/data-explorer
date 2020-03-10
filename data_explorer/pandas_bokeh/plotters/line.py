import datetime as dt
from math import floor
from typing import List

import pandas as pd
from bokeh.models import (CDSView, ColumnDataSource, CrosshairTool,
                          DataRange1d, GroupFilter, HoverTool, Legend, PanTool,
                          WheelZoomTool)
from bokeh.palettes import brewer, plasma
from bokeh.plotting import figure, show

MAX_COLORS = 12


def color(size: int) -> List[str]:
    if size < 3:
        return brewer['Set3'][3][:size]
    if size > MAX_COLORS:
        fraction = size % MAX_COLORS
        return brewer['Set3'][MAX_COLORS] * floor(
            size / MAX_COLORS) + color(fraction)
    return brewer['Set3'][size]


def line(
        df_in: pd.DataFrame,
        *args,
        plot_height: int = 500,
        plot_width: int = 1400,
        toolbar_location: str = 'below',
        legend_location: str = 'right',
        **kwargs,
) -> figure:
    """Lineplot in bokeh."""
    #df = df.reset_index()
    df = df_in.copy()
    if isinstance(df, pd.Series):
        df = pd.DataFrame(df)
        df.columns = ['data']
    if 'datetime' in df.columns:
        df = df.drop('datetime', axis=1)

    df.index.name = None

    for column in df.columns:
        if df[column].dtypes == 'object':
            for index, category in enumerate(
                    df[column].astype('category').cat.categories):
                print(index, category)
            df[column] = df[column].astype('category').cat.codes

    df_cds = ColumnDataSource(df)

    p = figure(
        x_axis_type='datetime',
        plot_height=plot_height,
        plot_width=plot_width,
        title='',
        x_axis_label='timestamp',
        y_axis_label='value',
        toolbar_location=toolbar_location,
        tools="reset,box_zoom",
        # buggy:
        # x_range=DataRange1d(
        #     # df.index[0],
        #     # df.index[-1],
        #     bounds=(df.index[0] - dt.timedelta(weeks=52),
        #             df.index[-1] + dt.timedelta(weeks=52)), ),
        x_range=DataRange1d(bounds='auto'),
    )

    col_num = 0
    colors = color(len(df.columns))
    legends = []
    tooltips = []
    for column in df.columns:
        r = p.line(
            x='index',
            y=column,
            name='value',
            color=colors[col_num],
            source=df_cds,
        )
        col_num += 1

        legends.append((column, [r]))

        tooltips.append((column, '@{%s}' % column))

    tooltips.append(('index', '@index{%F}'))

    p.add_tools(
        HoverTool(
            tooltips=tooltips,
            renderers=[r],
            mode='vline',
            point_policy='follow_mouse',
            line_policy='none',
            formatters={'index': 'datetime'},
        ))

    legend = Legend(items=legends, location=(0, 0))

    p.add_tools(CrosshairTool())

    wheel_zoom_tool = WheelZoomTool()
    wheel_zoom_tool.dimensions = 'width'
    p.add_tools(wheel_zoom_tool)
    p.toolbar.active_scroll = wheel_zoom_tool

    pan_tool = PanTool()
    pan_tool.dimensions = 'width'
    p.add_tools(pan_tool)

    p.add_layout(legend, legend_location)

    p.legend.click_policy = 'hide'

    show(p)

    return p
