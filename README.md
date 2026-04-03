# MicroPython Button

A polling-based button handler for MicroPython with debounce, short press, long press, and multi-press sequence detection.

This library is a MicroPython port of the [EasyButton](https://github.com/evert-arias/EasyButton) Arduino library.

## Features

- **Debouncing**: Built-in configurable debouncing.
- **Short Press**: Detects single button presses.
- **Long Press**: Detects when a button is held for a specified duration.
- **Sequences**: Detects multiple presses within a time window (e.g., double tap, triple tap).
- **Polling-based**: Non-blocking design, ideal for main loops.
- **Flexible**: Supports active-low (with internal pull-up) or active-high configurations.

## Installation

### Using mip (MicroPython 1.19.1+)

You can install this library directly to your MicroPython board using `mip`:

```python
import mip
mip.install("github:yourusername/micropython-button")
```

Alternatively, you can manually upload `button.py` to the `lib` folder on your device.

## Quick Start

```python
from machine import Pin
from button import Button
import time

# Initialize button on Pin 0 (GP0)
btn = Button(0)

# Define callbacks
def on_press():
    print("Button pressed!")

def on_long_press():
    print("Button held for 2 seconds!")

# Register callbacks
btn.on_pressed(on_press)
btn.on_pressed_for(2000, on_long_press)

while True:
    # Read the button state (call this in your main loop)
    btn.read()
    time.sleep_ms(10)
```

## API Reference

### `Button(pin, debounce_ms=35, pull_up=True, active_low=True)`
- `pin`: GPIO number (int) or `machine.Pin` object.
- `debounce_ms`: Debounce window in milliseconds.
- `pull_up`: If `True`, enables internal pull-up resistor (only if `pin` is an int).
- `active_low`: Set to `True` if the button connects the pin to GND when pressed.

### Methods

- `read()`: Polls the button. Call this frequently in your main loop.
- `on_pressed(callback)`: Sets a callback for a short press (fires on release).
- `on_pressed_for(duration_ms, callback)`: Sets a callback for a long press (fires as soon as the duration is reached).
- `on_sequence(count, duration_ms, callback)`: Sets a callback for a sequence of presses (e.g., 2 presses within 500ms).
- `is_pressed()`: Returns `True` if the button is currently pressed.
- `is_released()`: Returns `True` if the button is currently released.
- `was_pressed()`: Returns `True` if the button transitioned to pressed in the last `read()`.
- `was_released()`: Returns `True` if the button transitioned to released in the last `read()`.
- `pressed_for(ms)`: Returns `True` if held for at least `ms`.
- `released_for(ms)`: Returns `True` if released for at least `ms`.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
