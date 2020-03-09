import pandas as pd
import numpy as np
import bokeh
from bokeh.io import output_notebook, output_file, save
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, NumeralTickFormatter, Span, HoverTool, LabelSet
from bokeh.layouts import column, row, WidgetBox
from re import sub
from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application
from bokeh.models.widgets import RadioButtonGroup, Slider, Dropdown, Div
from bokeh.palettes import Category20
from os.path import dirname, join

df = pd.read_csv(join(dirname(__file__), 'tcja_ext_data.csv'))

    
def find_val(mstat, deps, wages, salt, item):
    df_filter = df.loc[(df['depx'] == deps) & (df['mstat'] == mstat) & (df['Wages'] == wages) & (df['otheritem'] == salt) & (df['mortgage'] == item)]
    keep = ['itax base', 'itax ext']
    df_itax = df_filter[keep]
    df_itax['dol_cut'] = (df_itax.loc[:,'itax base'] - df_itax.loc[:,'itax ext'])
    df_transposed = df_itax.transpose()
    df_transposed.columns = ['itax']
    x_vals = [0.5, 1.5, 2.5]
    df_transposed['x_vals'] = x_vals
    return ColumnDataSource(df_transposed)

def make_plot(src):
    p = figure(x_range=["Current Law", "TCJA Extension", "Difference"], plot_height=250, plot_width=400, toolbar_location=None, tools="")
    p.vbar(source=src, x='x_vals', top='itax', color='#ff7f0e', hover_fill_color='#ff7f0e',hover_fill_alpha=0.8, width=0.3, fill_alpha=0.5)
    hline = Span(location=0, dimension='width', line_color='black')
    p.renderers.extend([hline])
    p.xaxis.axis_line_color = '#d3d3d3'
    p.yaxis.axis_line_color = '#d3d3d3'
    p.yaxis[0].ticker.desired_num_ticks = 2
    p.xaxis.major_tick_line_color = None
    p.xaxis.minor_tick_line_color = None
    p.yaxis.minor_tick_line_color = None
    p.yaxis.major_tick_line_color = '#d3d3d3'
    p.yaxis[0].formatter = NumeralTickFormatter(format="$0,000")
#         p.yaxis.axis_label = "Individual Income Tax"
    p.ygrid.grid_line_color = None
    p.xgrid.grid_line_color = None
    p.outline_line_color = None
    p.xaxis.axis_line_color = None
    
    hover = HoverTool(tooltips='@itax{$0,000}')
    p.add_tools(hover)

    return p

def update(attr, old, new):
    if mstat_button.labels[mstat_button.active] == 'Single':
        mstat = 1
    else:
        mstat = 2
        
    deps = deps_slider.value
    wages = wages_slider.value
    salt = salt_slider.value
    item = item_slider.value

    new_src = find_val(mstat=mstat, deps=deps, wages=wages, salt=salt, item=item)

    src.data.update(new_src.data)
    
mstat_button = RadioButtonGroup(labels=["Single", "Married"], active=0)
deps_slider = Slider(start=0, end=4, value=0, step=1, title="Number of Children")
wages_slider = Slider(start=0, end=500000, value=0, step=10000, title="Wage Income", format="$0,000")
salt_slider = Slider(start=0, end=50000, value=0, step=2000, title="State and Local Taxes Paid", format="$0,000")
item_slider = Slider(start=0, end=50000, value=0, step=2000, title="Other Itemizable Expenses", format="$0,000")

mstat_button.on_change('active', update)
deps_slider.on_change('value', update)
wages_slider.on_change('value', update)
salt_slider.on_change('value', update)
item_slider.on_change('value', update)

controls = WidgetBox(mstat_button, deps_slider, wages_slider, salt_slider, item_slider)

src = find_val(mstat=1, deps=0, wages=0, salt=0, item=0)

p = make_plot(src)

layout = row(controls, p)
curdoc.add_root(layout)