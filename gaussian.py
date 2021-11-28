import numpy as np
import argparse
from bokeh.plotting import figure, show, curdoc
from bokeh.layouts import column, row
from bokeh.models import Button, Slider, Band, VArea

parser = argparse.ArgumentParser(description='Fooling around with bokeh')
parser.add_argument('--no-server', action='store_true',  help="do not start a server")
args = parser.parse_args()

# prepare some data
x = np.linspace(0, 10, num=100)

# a Gaussian
sigma = 2
mean = 5
f_gaussian = lambda x1: 1/(sigma * np.sqrt(2*np.pi)) * np.exp( (-1*((x1-mean) ** 2) / (2 * sigma**2)) )
y = f_gaussian(x)  


# create a new plot with a title and axis labels
p = figure(title="Basic Gaussian distribution", x_axis_label='x', y_axis_label='f(x)')
# add a line renderer with legend and line thickness to the plot
line_r = p.line(x, y, line_width=2)
varea_r = p.varea(x=x, y1=0, y2=y, fill_color="#03e3fc", alpha = 0.5)

def serve():

    line_ds = line_r.data_source
    varea_ds = varea_r.data_source

    def refresh_plot():
        
        # # BEST PRACTICE --- update .data in one step with a new dict
        new_data = dict()
        new_data['x'] = line_ds.data['x']
        new_data['y'] = f_gaussian(line_ds.data['x'])
        line_ds.data = new_data

        varea_new_data = dict()
        varea_new_data['x'] = new_data['x'] 
        varea_new_data['y2'] = new_data['y']
        varea_ds.data = varea_new_data

    def sigma_slider_callback(attr, old, new):
        global sigma
        sigma = new
        refresh_plot()

    def mean_slider_callback(attr, old, new):
        global mean
        mean = new
        refresh_plot()

    sigma_slider = Slider(title="Sigma", start=0, end=10, value=sigma, step=.1)
    sigma_slider.on_change('value', sigma_slider_callback)
    
    mean_slider = Slider(title="Mean", start=0, end=10, value=mean, step=.1)
    mean_slider.on_change('value', mean_slider_callback)

    # put the plot and sliders in a layout and add to the document
    curdoc().add_root(column(p, mean_slider, sigma_slider))


# show the results
if args.no_server:
    show(p)
else:
    serve()
