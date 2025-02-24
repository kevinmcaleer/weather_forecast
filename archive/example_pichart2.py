from pichart import Chart, Container
from presto import Presto

presto = Presto()


# Set up display
display = presto.display
WIDTH, HEIGHT = display.get_bounds()

# Create a chart
chart = Chart(display, title="Temp", values=[20, 25, 22, 28])
chart.x = 10
chart.y = 10
chart.width = WIDTH
chart.height = HEIGHT
chart.data_colour = {'red': 255, 'green': 0, 'blue': 0}  # Red bars
chart.show_bars = False
chart.show_lines = True
chart.show_datapoints = True
chart.show_labels = False
chart.title = "Test"
chart.title_colour = {'red': 255, 'green': 255, 'blue': 255}
chart.scale_to_fit = False
chart.draw_grid()
chart.grid_colour = {'red': 10, 'green': 10, 'blue': 10}
chart.bar_gap = 20
chart.show_x_axis = True
chart.show_y_axis = True



# Add to a container
container = Container(display)
container.width = WIDTH
container.height = HEIGHT
container.add_chart(chart)

container.data_colour = {'red': 255, 'green': 255, 'blue': 255}  # Red bars

# Draw it
container.update()
presto.update()