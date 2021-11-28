import numpy as np
import argparse
from bokeh.plotting import figure, show, curdoc
from bokeh.layouts import column, row
from bokeh.models import Button, Slider, Band, VArea

parser = argparse.ArgumentParser(description='Fooling around with bokeh')
parser.add_argument('--no-server', action='store_true',  help="do not start a server")
args = parser.parse_args()

# prepare some data
Tp = 100E-3     #[s] Integration time
f_max = 3/Tp   #[Hz]The amplitude of the sinc is negligeable beyond 3 zero crossings
c_max = 1.5      #Nothing of interest beyound delta code >1
freq = np.linspace(-f_max, f_max, 250)
code = np.linspace(-c_max, c_max, 250)
xx, yy = np.meshgrid(freq, code)

@np.vectorize
def triangle(tau):
    
    if (abs(tau)>1):
        return 0.0
    else: 
        return 1 - abs(tau)


#d = np.sin(xx/f_max)*np.cos(yy)
d = triangle(yy)*np.sinc(2*np.pi*xx*Tp/2)
#d = triangle(yy.T)
p = figure(title="ACF",x_axis_label='delta f', y_axis_label='delta code')
p.x_range.range_padding = p.y_range.range_padding = 0

p.image(image=[d], x=-f_max, y=-c_max, dw=2*f_max, dh=2*c_max, palette="Turbo256", level="image")
p.grid.grid_line_width = 0.5

show(p)



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

    # put the button and plot in a layout and add to the document
    curdoc().add_root(column(p, mean_slider, sigma_slider))


# show the results
if args.no_server:
    show(p)
else:
    serve()
