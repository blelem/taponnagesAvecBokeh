from bokeh.plotting import figure, show, curdoc

from bokeh.layouts import column
from bokeh.models import Button

# prepare some data
x = [1, 2, 3, 4, 5]
y = [6, 7, 2, 4, 5]

# create a new plot with a title and axis labels
p = figure(title="Simple line example", x_axis_label='x', y_axis_label='y')
# add a line renderer with legend and line thickness to the plot
p.line(x, y, legend_label="Temp.", line_width=2)
# show the results
# show(p)

r = p.text(x=[], y=[], text=[], text_color=[], text_font_size="26px",
           text_baseline="middle", text_align="center")
ds = r.data_source

# create a callback that adds a number in a random location
def callback():
    p.title("hello!")
    # global i

    # # BEST PRACTICE --- update .data in one step with a new dict
    # new_data = dict()
    # new_data['x'] = ds.data['x'] + [random()*70 + 15]
    # new_data['y'] = ds.data['y'] + [random()*70 + 15]
    # new_data['text_color'] = ds.data['text_color'] + [RdYlBu3[i%3]]
    # new_data['text'] = ds.data['text'] + [str(i)]
    # ds.data = new_data
    #i = i + 1

# add a button widget and configure with the call back
button = Button(label="Press Me")
button.on_click(callback)

# put the button and plot in a layout and add to the document
curdoc().add_root(column(button, p))
