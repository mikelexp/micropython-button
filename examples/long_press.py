from button import Button
import time

# Initialize button on Pin 0 (GP0)
btn = Button(0)

# Callback function to run for short presses (fires on release)
def on_short_press():
    print("Detected a short press!")

# Callback function to run for long presses (fires exactly once during hold)
def on_long_press():
    print("Detected a long press! (held for 1.5 seconds)")

# Register the callbacks
btn.on_pressed(on_short_press)
btn.on_pressed_for(1500, on_long_press)

print("Starting long_press example. Try both short and long presses on GP0.")

while True:
    btn.read()
    time.sleep_ms(10)
