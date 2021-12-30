import numpy as np
import panel as pn
import param
import panel.widgets as pnw
from bokeh.plotting import figure
from bokeh.models import Span
from bokeh.events import Tap

# Basic parameters
f_max = 150     #[Hz] acf window, max frequency 
c_max = 1.5     #[chip] acf window, max code delay
tp = 10         #[ms] Integration time
mp_alpha = 1.0  # Strength of the multipath
mp_freq = 100   # Multipath delta freq [Hz]
mp_code = 0.5   # Multipath delta code [chip]
mp_phase = np.pi #Multipath phase [rad]
crosshair_freq = 0
crosshair_code = 0

# The mesh is never updated after initial creation
freq_linspace = np.linspace(-f_max, f_max, 250)
code_linspace = np.linspace(-c_max, c_max, 250)
xx, yy = np.meshgrid(freq_linspace, code_linspace)

# --- ACF simulation ---

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
    
def update_acf(tp, mp_alpha, mp_freq, mp_code, mp_phase):
    return auto_correlation_fct(xx, yy, tp*1E-3, mp_alpha, mp_freq, mp_code, mp_phase)

# --- ACF surface plot ---

def plot_acf(auto_correlation, crosshair):
    
    p = figure(title="ACF",x_axis_label='delta f from true signal [Hz]', y_axis_label='code delay from true signal [chips]', plot_height=500)
    p.x_range.range_padding = p.y_range.range_padding = 0

    p.image(image=[auto_correlation], x=-f_max, y=-c_max, dw=2*f_max, dh=2*c_max, palette="Turbo256", level="image")
    p.grid.grid_line_width = 0.5
    p.toolbar.logo = None
    p.toolbar_location = None
   
    selected_freq_span = Span(location=crosshair['freq'], dimension='height', line_color='black',line_dash='dashed', line_width=3)
    p.add_layout(selected_freq_span)
    selected_code_delay_span = Span(location=crosshair['code'], dimension='width', line_color='#eb34c9',line_dash='dashed', line_width=3)
    p.add_layout(selected_code_delay_span)

    # Catch click events on the plot to change the location of the crosshair
    def on_click_callback(event):
        global crosshair
        crosshair.update_position( float(event.x), float(event.y) )
    
    p.on_event(Tap, on_click_callback)
    return p

def plot_freq_slice(auto_correlation, crosshair):
    selected_freq = crosshair['freq']
    selected_code = crosshair['code']
    code_idx = crosshair['code_idx']
    freq_idx = crosshair['freq_idx']
    freq_p = figure(title=f'freq slice @ code_delay: {selected_code} chips',x_axis_label='', y_axis_label='magnitude', plot_height=200)
    freq_p.line(freq_linspace, auto_correlation[code_idx,:], line_color='#eb34c9',line_dash='dashed')
    freq_p.circle([selected_freq], [auto_correlation[code_idx, freq_idx]], color='black', size=10)
    freq_p.x_range.range_padding = 0
    freq_p.toolbar.logo = None
    freq_p.toolbar_location = None
    return freq_p

def plot_code_slice(auto_correlation, crosshair):
    selected_freq = crosshair['freq']
    selected_code = crosshair['code']
    code_idx = crosshair['code_idx']
    freq_idx = crosshair['freq_idx']
    code_p = figure(title=f'code slice @ freq :{selected_freq} Hz',x_axis_label='magnitude', y_axis_label='', plot_height=500, plot_width=200)
    code_p.line( auto_correlation[:, freq_idx], code_linspace, line_color='black',line_dash='dashed')
    code_p.circle([auto_correlation[code_idx, freq_idx]], [selected_code], color='#eb34c9', size=10)
    code_p.y_range.range_padding = 0
    code_p.toolbar.logo = None
    code_p.toolbar_location = None
    return code_p

# --- The crosshair functionality ---

# Find index of the element nearest to desired value
def find_nearest(value, from_array):
    idx = (np.abs(from_array-value)).argmin()
    return idx

# By inheriting from a Param class, an event will be raised when the value of the parameter is changed. The event can be bound as a dependency
class Crosshair(param.Parameterized):
    position = param.Parameter( {},  doc="A tuple (Frequency[Hz], Code phase[chips]) that defines the current position of the crosshair")

    def update_position(self, freq, code):
        self.position = {
            'freq' : freq,
            'code' : code,
            'freq_idx' : find_nearest(freq, freq_linspace),
            'code_idx' : find_nearest(code, code_linspace)
        }


crosshair = Crosshair()
crosshair.update_position(crosshair_freq, crosshair_code)

# --- The widgets ---
tp_slider  = pnw.FloatSlider(name='Integration time[ms]', value=tp, start=10, end=100, step=1)
mp_alpha_slider = pnw.FloatSlider(name="Strength", value=mp_alpha, start=0, end=1.0, step=0.01)
mp_freq_slider = pnw.FloatSlider(name="Delta freq [Hz]", value=mp_freq, start=0, end=200,  step=1)
mp_code_slider = pnw.FloatSlider(name="Delta code [chips]", value=mp_code, start=0, end=1.0, step=0.1)
mp_phase_slider = pnw.FloatSlider(name="Delta phase [rad]", start=0, end=2*np.pi, value=mp_phase, step = 0.01)

widgets   = pn.Column("<br>\n# Parameters", tp_slider, mp_alpha_slider, mp_freq_slider, mp_code_slider, mp_phase_slider)

# --- Bindings ---
reactive_acf = pn.bind( update_acf, tp=tp_slider, mp_alpha=mp_alpha_slider, mp_freq=mp_freq_slider, mp_code=mp_code_slider, mp_phase=mp_phase_slider)
reactive_plot_acf = pn.bind( plot_acf, reactive_acf, crosshair = crosshair.param.position)
reactive_plot_freq_slice = pn.bind (plot_freq_slice, auto_correlation = reactive_acf, crosshair = crosshair.param.position)
reactive_plot_code_slice = pn.bind (plot_code_slice, auto_correlation = reactive_acf, crosshair = crosshair.param.position)
acf_plot = pn.Row(widgets, pn.Column(pn.Row(reactive_plot_acf,reactive_plot_code_slice ), reactive_plot_freq_slice) )
acf_plot.show()
