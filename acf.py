import numpy as np
import argparse
from bokeh.plotting import figure, show, curdoc
from bokeh.layouts import column, row
from bokeh.models import Slider, Span
from bokeh.models.widgets.markups import Div
from bokeh.events import Tap

parser = argparse.ArgumentParser(description='Fooling around with bokeh')
parser.add_argument('--no-server', action='store_true',  help="do not start a server")
args = parser.parse_args()

# prepare some data
Tp = 10E-3      #[s] Integration time
f_max = 150     #[Hz] acf window, max frequency 
c_max = 1.5     #[chip] acf window, max code delay
freq_linspace = np.linspace(-f_max, f_max, 250)
code_linspace = np.linspace(-c_max, c_max, 250)
xx, yy = np.meshgrid(freq_linspace, code_linspace)
selected_freq = 20
selected_code = 0.5

mp_alpha = 1.0 #Strenght of the multipath
mp_freq = 100 #[Hz]
mp_code = 0.5 #[chip]
mp_phase = np.pi #[rad]


# Find index of the element nearest to desired value
def find_nearest(value, from_array):
    idx = (np.abs(from_array-value)).argmin()
    return idx

@np.vectorize
def triangle(tau):
    
    if (abs(tau)>1):
        return 0.0
    else: 
        return 1.0 - abs(tau)

def acf(xx, yy, Tp, phase):
    # Autocorrelation of a BPSK signal, according to eq. 2.23 in [1]

    # Note numpy's sinc is defined as sin(pi*x)/(x*pi)
    # We need to divide the sinc argument by pi, to get the same sinc definition as used in 2.23
    # triangle(yy)*np.sinc( (2*pi*xx) * Tp/2 * 1/pi)) * i exp(i * phase)
    
    # [1] : Modeling and Simulating GNSS Signal Structures and Receivers, Jon Olafur Winkel
    return triangle(yy)*np.sinc(xx*Tp) * + 1.0j * np.exp(1.0j*phase)


def auto_correlation_fct (xx, yy, Tp, mp_alpha, mp_freq, mp_code, mp_phase):

    return np.abs(acf(xx,yy,Tp, 0) + mp_alpha * acf(xx-mp_freq, yy-mp_code, Tp, mp_phase))

auto_correlation = auto_correlation_fct(xx,yy,Tp,  mp_alpha, mp_freq, mp_code, mp_phase)

# Build the graph
p = figure(title="ACF",x_axis_label='delta f from true signal [Hz]', y_axis_label='code delay from true signal [chips]')
p.x_range.range_padding = p.y_range.range_padding = 0

acf_glyph = p.image(image=[auto_correlation], x=-f_max, y=-c_max, dw=2*f_max, dh=2*c_max, palette="Turbo256", level="image")
p.grid.grid_line_width = 0.5
p.toolbar.logo = None
p.toolbar_location = None

selected_freq_span = Span(location=selected_freq, dimension='height', line_color='black',line_dash='dashed', line_width=3)
p.add_layout(selected_freq_span)
selected_code_delay_span = Span(location=selected_code, dimension='width', line_color='#eb34c9',line_dash='dashed', line_width=3)
p.add_layout(selected_code_delay_span)

freq_idx = find_nearest(selected_freq, freq_linspace)
code_idx = find_nearest(selected_code, code_linspace)

freq_p = figure(title=f'freq slice @ code_delay: {selected_code} chips',x_axis_label='delta f [Hz]', y_axis_label='', plot_height=300)
freq_p_glyph = freq_p.line(freq_linspace, auto_correlation[code_idx,:], line_color='#eb34c9',line_dash='dashed')
freq_p_circle = freq_p.circle([selected_freq], [auto_correlation[code_idx, freq_idx]], color='black', size=10)

code_p = figure(title=f'code slice @ freq :{selected_freq} Hz',x_axis_label='code delay [chip]', y_axis_label='', plot_height=300)
code_p_glyph = code_p.line(code_linspace, auto_correlation[:, freq_idx],line_color='black',line_dash='dashed')
code_p_circle = code_p.circle([selected_code], [auto_correlation[code_idx, freq_idx]], color='#eb34c9', size=10)

# Serve contains the callbacks for interractivity
def serve():

    acf_ds = acf_glyph.data_source
    freq_ds = freq_p_glyph.data_source
    freq_circle_ds = freq_p_circle.data_source
    code_ds = code_p_glyph.data_source
    code_circle_ds = code_p_circle.data_source

    def refresh_plot():
        #ACF plot
        new_data = dict()
        new_data['image'] = [auto_correlation]
        acf_ds.data = new_data

        code_idx = find_nearest(selected_code, code_linspace)
        freq_idx = find_nearest(selected_freq, freq_linspace)


        #Frequency slice plot
        freq_p.title.text = f'freq slice @ code_delay:{selected_code:.2f} chips'

        new_data = dict()
        new_data['x'] = freq_linspace
        new_data['y'] = auto_correlation[code_idx, :]
        freq_ds.data = new_data

        new_data = dict()
        new_data['x'] = [selected_freq]
        new_data['y'] = [auto_correlation[code_idx, freq_idx]]
        freq_circle_ds.data = new_data

        #Code slice plot
        code_p.title.text = f'code slice @ freq :{selected_freq:.2f} Hz'
        new_data = dict()
        new_data['x'] = code_linspace
        new_data['y'] = auto_correlation[:,freq_idx]
        code_ds.data = new_data

        new_data = dict()
        new_data['x'] = [selected_code]
        new_data['y'] = [auto_correlation[code_idx, freq_idx]]
        code_circle_ds.data = new_data

        selected_freq_span.location = selected_freq
        selected_code_delay_span.location = selected_code

    def Tp_slider_callback(attr, old, new):
        global Tp, auto_correlation
        Tp = new * 1E-3
        auto_correlation = auto_correlation_fct(xx, yy, Tp, mp_alpha, mp_freq, mp_code, mp_phase)
        refresh_plot()

    def mp_alpha_slider_callback(attr, old, new):
        global mp_alpha, auto_correlation
        mp_alpha = new
        auto_correlation = auto_correlation_fct(xx, yy, Tp, mp_alpha, mp_freq, mp_code, mp_phase)
        refresh_plot()

    def mp_freq_slider_callback(attr, old, new):
        global mp_freq, auto_correlation
        mp_freq = new
        auto_correlation = auto_correlation_fct(xx, yy, Tp, mp_alpha, mp_freq, mp_code, mp_phase)
        refresh_plot()

    def mp_code_slider_callback(attr, old, new):
        global mp_code, auto_correlation
        mp_code = new
        auto_correlation = auto_correlation_fct(xx, yy, Tp, mp_alpha, mp_freq, mp_code, mp_phase)
        refresh_plot()

    def mp_phase_slider_callback(attr, old, new):
        global mp_phase, auto_correlation
        mp_phase= new
        auto_correlation = auto_correlation_fct(xx, yy, Tp, mp_alpha, mp_freq, mp_code, mp_phase)
        refresh_plot()

    # Change the location of the crosshair
    def on_click_callback(event):
        global selected_code, selected_freq
        selected_freq = float(event.x)
        selected_code = float(event.y)
        refresh_plot()
        
    p.on_event(Tap, on_click_callback)

    Tp_slider = Slider(title="Integration time[ms]", start=10, end=100, value=Tp*1E3, step=.1)
    Tp_slider.on_change('value_throttled', Tp_slider_callback)

    mp_alpha_slider = Slider(title="Strength", start=0, end=1.0, value=mp_alpha, step=0.01)
    mp_alpha_slider.on_change('value_throttled', mp_alpha_slider_callback)
    mp_freq_slider = Slider(title="Delta freq [Hz]", start=0, end=200, value=mp_freq, step=1)
    mp_freq_slider.on_change('value_throttled', mp_freq_slider_callback)
    mp_code_slider = Slider(title="Delta code [chips]", start=0, end=1.0, value=mp_code, step=0.1)
    mp_code_slider.on_change('value_throttled', mp_code_slider_callback)
    mp_phase_slider = Slider(title="Delta phase [rad]", start=0, end=2*np.pi, value=mp_phase, step = 0.01)
    mp_phase_slider.on_change('value_throttled', mp_phase_slider_callback)

    mp_title = Div(text='<h3 style="text-align: center">Multipath</h3>')
    mp_panel = column(mp_title, mp_alpha_slider, mp_freq_slider, mp_code_slider, mp_phase_slider)
    mp_panel.background = "beige"

    # put the button and plot in a layout and add to the document
    curdoc().add_root(row(column( p, Tp_slider, mp_panel), column(freq_p, code_p)))


# show the results
if args.no_server:
    show(p)
else:
    serve()
