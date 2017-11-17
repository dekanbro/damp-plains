#!/usr/bin/env python3

# Innocentive challenge - Colorado river basin data visualization
# 
# Dashboard of lower Colorado river hourly flow data (incuding YAO stream gages)
# The data consist of hourly flow rates (in CFS) and hourly river gage readings (in feet)
# from 9 stream gage sites. These data were compiled from DSET-71 and DSET-13 datasets.

import numpy as np
import pandas as pd

import bokeh.plotting as bk
import bokeh.io
import bokeh.layouts
import bokeh.models
import bokeh.palettes 

# Import dataset
source = "./locoflow/loco-flow-hourly-data.csv"
dat = pd.read_csv(source)

# Parse datetime
df = dat.assign(DateTime = pd.to_datetime(dat.DateTime))

# Split datasets into flow rates and gage heights
flow_rates = df[df["Variable"].str.contains("flow")].groupby("ShortName")
gage_heights = df[df["Variable"].str.contains("height")].groupby("ShortName")

# Extract data for each site
sites = ["bigbend", "parkergage", "wheel", "bridge", "mcintyre",
        "taylor", "oxbow", "picacho", "martinez"] # Sites from north-to-south
flow_dsets = [flow_rates.get_group(s).sort_values(by = "DateTime") for s in sites]
height_dsets = [gage_heights.get_group(s).sort_values(by = "DateTime") for s in sites]

n = 145 # Number of observations in each dataset

# Initialize plots
plot, elements = {}, {}
colors = bokeh.palettes.Category10_10
colors.pop(7)

# Top left: Sites on a map
plot["points"] = bk.figure(plot_height=500, plot_width=350,
        x_axis_label = "Longitude", y_axis_label = "Latitude")

# Top right: Flow rates 
plot["tapes"] = bk.figure(plot_height=500, plot_width=600,
                 title = "Hourly flow rates",
                 x_axis_type = "datetime",
                 y_range = plot["points"].y_range)

# Bottom right: Gage heights
plot["lines"] = bk.figure(plot_height=400, plot_width=600,
        x_axis_type = "datetime", x_range = plot["tapes"].x_range,
        y_axis_label = "Average gage height (feet)")

# Bottom left: legends
plot["guides"] = bk.figure(plot_height = 400, plot_width = 350)
plot["guides"].axis.visible = False
plot["guides"].grid.visible = False
plot["guides"].outline_line_color = None
#plot["guides"].yaxis.visible = False
#plot["guides"].ygrid.visible = False

# Add plot elements
points, tapes = [], []
for (j, dset) in enumerate(flow_dsets):
    #d = dset.iloc[:1]
    # Points on map
    points.append(plot["points"]
            .circle(x = dset.Longitude, y = dset.Latitude, 
                size = dset.Value/500, color = colors[j], 
                alpha = [0. for k in range(n)]))
    # Tape view of flow
    tapes.append(plot["tapes"]
            .circle(x = dset.DateTime, y = dset.Latitude,
                size= dset.Value/500, color = colors[j],
                alpha = [0. for k in range(n)]))

# Gage heights
xvals = [d.DateTime for d in height_dsets]
yvals = [d.Value for d in height_dsets]
lines = plot["lines"].multi_line(
        xs = [x[:1] for x in xvals], 
        ys = [y[:1] for y in yvals], 
        line_width = 2, line_color = colors)

elements = dict(points = points, tapes = tapes, lines = lines)
ds = dict(points = [p.data_source for p in points],
        tapes = [t.data_source for t in tapes],
        lines = lines.data_source)

index = 0

# Callback functions to animate plot elements

def redraw_points(k):
    """
    Update point data
    """
    for j, d in enumerate(ds["points"]):
        alpha = [1. if i == k else 0. for i in range(n)]
        d.data["fill_alpha"] = alpha

def redraw_tapes(k, lo = 0.2, hi = 0.9):
    """
    Change plot element alpha values to show values up to index k.
    Make the final glyph darker
    """
    for (j, d) in enumerate(ds["tapes"]):
        alpha = [lo if i < k else 0 for i in range(n)]
        alpha[k-1] = hi if k > 0 else 0
        d.data["fill_alpha"] = alpha

def redraw_lines(k):
    props = dict(ds["lines"].data)
    props["xs"] = [x[:k] for x in xvals]
    props["ys"] = [y[:k] for y in yvals]
    ds["lines"].data = props

def animate():
    """
    Simulate animation by changing plot element alphas
    """
    global index
    if index < n:
        index += 1
        redraw_points(index)
        redraw_tapes(index)
        redraw_lines(index)
    else:
        index = 0
    slider.value = index

def update(fps = 12):
    """
    Play/pause animation. fps is frames per second (higher = faster)
    """
    if button.label == "Play":
        button.label = "Pause"
        bk.curdoc().add_periodic_callback(animate, 1000/fps)
    else: 
        button.label = "Play"
        bk.curdoc().remove_periodic_callback(animate)

# Add button to play/pause animation
button = bokeh.models.Button(label = "Play")
button.on_click(update)

# Add slider to select time
def slider_update(attrname, old, new):
    global index
    index = slider.value
    redraw_points(index)
    redraw_tapes(index)
    redraw_lines(index)

slider = bokeh.models.Slider(start = 0, end = 144, step = 1, value = 0, title = "Hours")
slider.on_change("value", slider_update)

# Create layout
plots = bokeh.layouts.gridplot([[plot["points"], plot["tapes"]], [plot["guides"], plot["lines"]]],
        toolbar_location = "left")
layout = bokeh.layouts.layout([[button, slider], [plots]])

# Add to current document
bk.curdoc().add_root(layout)
bk.curdoc().title = "Lower Colorado hourly flow rates"

