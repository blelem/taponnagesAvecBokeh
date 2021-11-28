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
f_max = 3/Tp    #[Hz]The amplitude of the sinc is negligeable beyond 3 zero crossings
c_max = 1.5     #[chip] Nothing of interest beyond code delay >1 chip
freq = np.linspace(-f_max, f_max, 250)
code = np.linspace(-c_max, c_max, 250)
xx, yy = np.meshgrid(freq, code)

@np.vectorize
def triangle(tau):
    
    if (abs(tau)>1):
        return 0.0
    else: 
        return 1.0 - abs(tau)

def acf(xx, yy, Tp):
    return triangle(yy)*np.sinc(2*np.pi*xx*Tp/2)


p = figure(title="ACF",x_axis_label='delta f [Hz]', y_axis_label='code delay [chips]')
p.x_range.range_padding = p.y_range.range_padding = 0

acf_glyph = p.image(image=[acf(xx,yy,Tp)], x=-f_max, y=-c_max, dw=2*f_max, dh=2*c_max, palette="Turbo256", level="image")
p.grid.grid_line_width = 0.5

def serve():

    acf_ds = acf_glyph.data_source

    def refresh_plot():
        print("Hi")
        # # BEST PRACTICE --- update .data in one step with a new dict
        new_data = dict()
        new_data['image'] = [acf(xx,yy,Tp*2)]
        acf_ds.data = new_data

    def Tp_slider_callback(attr, old, new):
        global Tp
        Tp = new * 1E-3
        refresh_plot()

    Tp_slider = Slider(title="Integration time[ms]", start=10, end=100, value=Tp, step=.1)
    Tp_slider.on_change('value_throttled', Tp_slider_callback)

    # put the button and plot in a layout and add to the document
    curdoc().add_root(column( p, Tp_slider))


# show the results
if args.no_server:
    show(p)
else:
    serve()
