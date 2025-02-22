from pichart import Chart, Container
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY

# Set up display
display = PicoGraphics(display=DISPLAY_PICO_DISPLAY)

# Create a chart
chart = Chart(display, title="Temp", values=[20, 25, 22, 28])
chart.x = 10
chart.y = 10
chart.width = 220
chart.height = 120
chart.data_colour = {'red': 255, 'green': 0, 'blue': 0}  # Red bars
chart.show_bars = True
chart.show_labels = True

# Add to a container
container = Container(display)
container.add_chart(chart)

# Draw it
container.update()