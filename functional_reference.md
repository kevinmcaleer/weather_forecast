# PiChart Documentation

## Overview

PiChart is a lightweight dashboard charting library designed for MicroPython. It provides a simple interface for rendering bar charts, line charts, and data points on microcontroller displays.

### Author: Kevin McAleer  
### Date: June 2022

---

## Dependencies
PiChart relies on the `jpegdec` library, which is included in the Pimoroni Batteries-included MicroPython build.

```python
import jpegdec
```

---

## Class Overview

### `Chart`
The `Chart` class is responsible for rendering graphical charts. It supports features like:
- Customizable background, border, grid, and title colors
- Data scaling and mapping
- Optional grid, bars, and data point rendering
- Label display

#### Attributes
- `title`: Title of the chart.
- `x_values`: Data points for the X-axis.
- `x_offset`, `y_offset`: Chart position offsets.
- `background_colour`, `border_colour`, `grid_colour`, `title_colour`, `data_colour`: Customizable color settings.
- `data_point_radius`, `data_point_radius2`, `data_point_width`: Control the display of data points.
- `width`, `height`, `border_width`, `text_height`: Dimensions of the chart.
- `show_datapoints`, `show_lines`, `show_bars`, `grid`: Toggles for different chart features.
- `grid_spacing`, `bar_gap`: Layout properties for grid and bars.

#### Methods
- `__init__(self, display, title, x_label, y_label, x_values, y_values)`: Initializes the chart with optional labels and values.
- `show_labels(self)`: Property getter and setter for showing labels.
- `draw_border(self)`: Draws a border around the chart.
- `draw_grid(self)`: Renders the grid.
- `map(self, x, in_min, in_max, out_min, out_max)`: Maps values from one range to another.
- `scale_data(self)`: Adjusts data scaling for display.
- `update(self)`: Refreshes the chart display.

---

### `Card`
A subclass of `Chart`, the `Card` class is designed for displaying single-value information.

#### Attributes
- `text_scale`: Scaling factor for text.
- `margin`: Controls spacing around the card.

#### Methods
- `__init__(self, display, x, y, width, height, title)`: Initializes a card with a display and title.
- `scale_text(self)`: Adjusts text size to fit within the card.
- `update(self)`: Updates the card display.

---

### `Image_tile`
A class for rendering images on a display.

#### Attributes
- `image_file`: The filename of the image.
- `x`, `y`, `width`, `height`: Position and size of the image.
- `border_colour`, `border_width`: Customizable border settings.

#### Methods
- `__init__(self, display, filename)`: Initializes the image tile.
- `draw_border(self)`: Draws a border around the image.
- `update(self)`: Loads and renders an image file.

---

### `Container`
The `Container` class manages multiple `Chart` instances.

#### Attributes
- `charts`: A list of charts within the container.
- `cols`: Number of columns in the layout.
- `__background_colour`, `__title_colour`, `__data_colour`, `__grid_colour`: Customizable global color settings for all charts in the container.

#### Methods
- `__init__(self, display, width, height)`: Initializes the container with specified dimensions.
- `add_chart(self, item)`: Adds a chart to the container.
- `update(self)`: Updates all charts within the container.

#### Properties
- `background_colour`, `grid_colour`, `data_colour`, `title_colour`, `border_colour`, `border_width`: Property getters and setters for global styling.

---

## Usage
### Creating a Chart
```python
from pichart import Chart

display = ...  # Initialize display
chart = Chart(display, title="Example Chart", x_values=[10, 20, 30, 40, 50])
chart.show_bars = True
chart.update()
```

### Using a Card
```python
from pichart import Card

display = ...  # Initialize display
card = Card(display, x=10, y=10, width=100, height=50, title="Temperature")
card.update()
```

### Displaying an Image
```python
from pichart import Image_tile

display = ...  # Initialize display
image = Image_tile(display, filename="image.jpg")
image.update()
```

### Organizing Charts in a Container
```python
from pichart import Container, Chart

display = ...  # Initialize display
container = Container(display, width=200, height=200)
chart1 = Chart(display, title="Chart 1", x_values=[10, 20, 30])
chart2 = Chart(display, title="Chart 2", x_values=[5, 15, 25])

container.add_chart(chart1)
container.add_chart(chart2)
container.update()
```

---

## Conclusion
PiChart is a powerful yet lightweight solution for rendering graphical charts on microcontrollers using MicroPython. Its modular design allows users to create various types of data visualizations efficiently.

