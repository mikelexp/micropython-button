from button import Button
import time

# Initialize button on Pin 0 (GP0)
# Default is active-low (connect to GND) with internal pull-up enabled.
btn = Button(0)

# Callback function to run when the button is pressed
def on_press():
    print("Button was pressed!")

# Register the callback
btn.on_pressed(on_press)

print("Starting basic_press example. Press the button on GP0.")

while True:
    # Polling: the read() method must be called repeatedly in the loop.
    btn.read()
    
    # Small delay to prevent CPU from spinning unnecessarily
    time.sleep_ms(10)
