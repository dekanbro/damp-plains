#!/usr/bin/env python3

# Innocentive challenge - Colorado river basin data visualization
#
# Dashboard of lower Colorado dam projection (DSET-7)
# The data are from 4 sites (Davis dam/Lake Mohave and Parker dam/Lake Havasu)
# and contain projected hourly energy production and water release for a 72 hour period

import numpy as np
import pandas as pd

import bokeh.plotting as bk
import bokeh.io
import bokeh.layouts
import bokeh.models
import bokeh.palettes

# Import dataset
source = "./locodams/dset-7-data.csv" 
dat = pd.read_csv(source)

# Parse datetime
df = dat.assign(DateTime = pd.to_datetime(dat.DateTime))

# # At each site compute time difference from initial time
# # (i.e. time of projecion - initial time) in hours
# df = (dat
#         .groupby("Site")
#         .apply(lambda x: x.assign(Delta = (x.DateTime - x.iloc[0].DateTime)/pd.Timedelta(1, "h")))
#         .reset_index(drop = True))

# Group data by site
gf = df.groupby("ShortName")

# Extract data for each site
sites = ["mohave", "davis", "havasu", "parker"]
dsets = [gf.get_group(s).sort_values(by = "DateTime").reset_index() for s in sites]
n = [d.shape[0] for d in dsets]

# Initialize plots
plots, elements = [], []
palette = bokeh.palettes.Spectral10
colors = [palette[j] for j in [1, -1, 2, -2]]

# Top left: Lake Mohave - Release
plots.append(bk.figure(plot_width = 450, plot_height = 125,
    title = "Lake Mohave: Projected release (CFS)",
    x_axis_type = "datetime",
    y_axis_label = "Total release (CFS)"))
plots[0].yaxis.visible = False
plots[0].ygrid.visible = False
# Add circles
elements.append(plots[0].
        circle(x = dsets[0].DateTime, y = 100, color = colors[0],
            size = dsets[0].Value/500, alpha = [0. for j in range(n[0])]))

# Bottom left: Davis dam - Energy
plots.append(bk.figure(plot_width = 450, plot_height = 300,
        title = "Davis dam: Projected energy (MWH)",
        x_axis_type = "datetime", x_range = plots[0].x_range,
        y_axis_label = "Total energy (MWH)"))
# Add bar chart
w = pd.Timedelta(0.5, unit="h") # bar width
elements.append(plots[1].
        vbar(x = dsets[1].DateTime, top = dsets[1].Value, width = w,
        color = colors[1], alpha = [0. for j in range(n[1])]))

# Top right: Lake Havasu - Release
plots.append(bk.figure(plot_width = 450, plot_height = 125,
    title = "Lake Havasu: Projected release (CFS)",
    x_axis_type = "datetime", x_range = plots[0].x_range,
    y_axis_label = "Total release (CFS)", y_range = plots[0].y_range))
plots[2].yaxis.visible = False
plots[2].ygrid.visible = False
# Add circles
elements.append(plots[2].
        circle(x = dsets[2].DateTime, y = 100, color = colors[2],
            size = dsets[2].Value/500, alpha = [0. for j in range(n[0])]))

# Bottom right: Parker dam - Energy
plots.append(bk.figure(plot_width = 450, plot_height = 300,
        title = "Parker dam: Projected energy (MWH)",
        x_axis_type = "datetime", x_range = plots[0].x_range,
        y_axis_label = "Total energy (MWH)", y_range = plots[1].y_range))
# Add bar chart
w = pd.Timedelta(0.5, unit="h") # bar width
elements.append(plots[3].
        vbar(x = dsets[3].DateTime, top = dsets[3].Value, width = w,
        color = colors[3], alpha = [0. for j in range(n[1])]))

ds = [e.data_source for e in elements]
index = 0

# Callback functions to animate plot elements
def redraw2(k, lo = 0.3, hi = 0.9):
    for (j, d) in enumerate(ds):
        props = dict(d.data)
        alpha = [lo if i < k else 0 for i in range(n[j])]
        alpha[k-1] = hi
        props["fill_alpha"] = alpha
        d.data = props

def animate():
    global index
    if index < n[0]:
        index += 1
        redraw2(index)
    else:
        for (j, d) in enumerate(ds):
            d.data["fill_alpha"] = [0. for k in range(n[j])]
        index = 0
    slider.value = index

def update(fps = 15):
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
    redraw2(index)

slider = bokeh.models.Slider(start = 0, end = 72, step = 1, value = 0, title = "Hours")
slider.on_change("value", slider_update)

# Create layout
grid = bk.gridplot([[plots[0], plots[2]], [plots[1], plots[3]]],
        toolbar_location = "left")
layout = bokeh.layouts.layout([grid, [button, slider]])

# Add to current document
bk.curdoc().add_root(layout)
bk.curdoc().title = "Lower Colorado dams: Projected hourly relase"
