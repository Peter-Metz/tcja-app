import pandas as pd
import numpy as np
import bokeh
from bokeh.io import output_notebook, output_file, save, curdoc
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, NumeralTickFormatter, Span, HoverTool, LabelSet
from bokeh.layouts import column, row, WidgetBox
from re import sub
from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application
from bokeh.models.widgets import RadioButtonGroup, Slider, Dropdown, Div
from os.path import dirname, join

df = pd.read_csv(join(dirname(__file__), 'cruncher_output.csv'))


def find_val(mstat, deps, wages, salt, item):
    df_filter = df.loc[(df['depx'] == deps) & (df['mstat'] == mstat) & (
        df['Wages'] == wages) & (df['otheritem'] == salt) & (df['mortgage'] == item)]
    keep = ['itax base', 'itax repeal', 'itax salt']
    df_itax = df_filter[keep]
    df_transposed = df_itax.transpose()
    df_transposed.columns = ['itax']
    x_vals = [0.5, 1.5, 2.5]
    df_transposed['x_vals'] = x_vals
    return ColumnDataSource(df_transposed)


def make_plot(src):
    p = figure(x_range=["Current Law", "TCJA Repeal", "SALT Cap Repeal"],
               plot_height=300, plot_width=500, toolbar_location=None)
    p.vbar(source=src, x='x_vals', top='itax', fill_color='#ff7f0e', color='#ff7f0e',
           hover_fill_color='#ff7f0e', hover_fill_alpha=0.8, width=0.3, fill_alpha=0.5)
    hline = Span(location=0, dimension='width', line_color='black')
    p.renderers.extend([hline])
    p.xaxis.axis_line_color = '#d3d3d3'
    p.yaxis.axis_line_color = '#d3d3d3'
    p.xaxis.major_tick_line_color = None
    p.xaxis.minor_tick_line_color = None
    p.yaxis.minor_tick_line_color = None
    p.yaxis.major_tick_line_color = '#d3d3d3'
    p.yaxis[0].formatter = NumeralTickFormatter(format="$0,000")
    p.yaxis.axis_label = "Individual Income Tax"
    p.ygrid.grid_line_color = None
    p.xgrid.grid_line_color = None
    p.outline_line_color = None
    p.xaxis.axis_line_color = None

    labels = LabelSet(x=0.5, y='itax base', text='test', level='glyph',
                      x_offset=5, y_offset=5, source=src, render_mode='canvas')

    hover = HoverTool(tooltips='@itax{$0,000}')
    p.add_tools(hover)

    return p


def update(attr, old, new):
    if mstat_button.labels[mstat_button.active] == 'Single':
        mstat = 1
    else:
        mstat = 2

    if deps_button.labels[deps_button.active] == '0 Kids':
        deps = 0
    elif deps_button.labels[deps_button.active] == '1 Kid':
        deps = 1
    else:
        deps = 2

    wages_str = wages_button.labels[wages_button.active]
    wages = float(sub(r'[^\d.]', '', wages_str))
    salt_str = salt_button.labels[salt_button.active]
    salt = float(sub(r'[^\d.]', '', salt_str))
    item_str = item_button.labels[item_button.active]
    item = float(sub(r'[^\d.]', '', item_str))

    new_src = find_val(mstat=mstat, deps=deps,
                       wages=wages, salt=salt, item=item)

    src.data.update(new_src.data)

mstat_button = RadioButtonGroup(labels=["Single", "Married"], active=0)
deps_button = RadioButtonGroup(labels=['0 Kids', '1 Kid', '2 Kids'], active=0)
wages_button = RadioButtonGroup(labels=['$10,000', '$20,000', '$40,000', '$60,000',
                                        '$80,000', '$100,000', '$200,000', '$500,000', '$1,000,000', '$5,000,000'], active=3)
salt_button = RadioButtonGroup(labels=[
                               '$0', '$2,000', '$5,000', '$10,000', '$20,000', '$30,000', '$50,000', '$100,000'], active=0)
item_button = RadioButtonGroup(labels=[
                               '$0', '$2,000', '$5,000', '$10,000', '$20,000', '$30,000', '$50,000', '$100,000'], active=0)

mstat_button.on_change('active', update)
deps_button.on_change('active', update)
wages_button.on_change('active', update)
salt_button.on_change('active', update)
item_button.on_change('active', update)

space = Div(text="<br>")
wages_title = Div(text="<b>Filing unit wages:</b>")
salt_title = Div(text="<b>Itemizable state and local taxes:</b>")
item_title = Div(text="<b>Other itemizable expenses:</b>")

controls = WidgetBox(space, mstat_button, deps_button, wages_title,
                     wages_button, salt_title, salt_button, item_title, item_button)

src = find_val(mstat=1, deps=0, wages=60000, salt=0, item=0)

p = make_plot(src)

layout = column(p, controls)
curdoc().add_root(layout)
