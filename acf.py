import numpy as np
import argparse
from bokeh.plotting import figure, show, curdoc
from bokeh.layouts import column, row
from bokeh.models import Slider, Span
from bokeh.events import Tap

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


# Build the graph
p = figure(title="ACF",x_axis_label='delta f [Hz]', y_axis_label='code delay [chips]')
p.x_range.range_padding = p.y_range.range_padding = 0

#color_mapper = LinearColorMapper(palette='Turbo256', low=-0.5, high=0.5)
acf_glyph = p.image(image=[acf(xx,yy,Tp)], x=-f_max, y=-c_max, dw=2*f_max, dh=2*c_max, palette="Turbo256", level="image")
p.grid.grid_line_width = 0.5
p.toolbar.logo = None
p.toolbar_location = None

selected_freq_span = Span(location=0, dimension='height', line_color='black',line_dash='dashed', line_width=3)
p.add_layout(selected_freq_span)
selected_code_delay_span = Span(location=0, dimension='width', line_color='#eb34c9',line_dash='dashed', line_width=3)
p.add_layout(selected_code_delay_span)

freq_p = figure(title="freq slice",x_axis_label='delta f [Hz]', y_axis_label='', plot_height=300)
freq_p_glyph = freq_p.line(xx[0], acf(xx[0], 0, Tp))

code_p = figure(title="code slice",x_axis_label='code delay [chip]', y_axis_label='', plot_height=300)
code_p_glyph = code_p.line(yy[:,0], acf(0, yy[:,0], Tp))

# Serve contains the callbacks for interractivity
def serve():

    acf_ds = acf_glyph.data_source
    freq_ds = freq_p_glyph.data_source
    code_ds = code_p_glyph.data_source

    def refresh_plot():
        # # BEST PRACTICE --- update .data in one step with a new dict
        new_data = dict()
        new_data['image'] = [acf(xx,yy,Tp*2)]
        acf_ds.data = new_data

    def Tp_slider_callback(attr, old, new):
        global Tp
        Tp = new * 1E-3
        refresh_plot()

    def on_click_callback(event):
        
        new_data = dict()
        new_data['x'] = xx[0,:]
        new_data['y'] = acf(xx[0,:], event.y, Tp)
        freq_ds.data = new_data

        new_data = dict()
        new_data['x'] = yy[:,0]
        new_data['y'] = acf(event.x,yy[:,0], Tp)
        code_ds.data = new_data
        

        selected_freq_span.location = event.x
        selected_code_delay_span.location = event.y


    p.on_event(Tap, on_click_callback)

    Tp_slider = Slider(title="Integration time[ms]", start=10, end=100, value=Tp, step=.1)
    Tp_slider.on_change('value_throttled', Tp_slider_callback)

    # put the button and plot in a layout and add to the document
    curdoc().add_root(row(column( p, Tp_slider), column(freq_p, code_p)))


# show the results
if args.no_server:
    show(p)
else:
    serve()
