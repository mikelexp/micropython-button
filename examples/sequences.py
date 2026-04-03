from button import Button
import time

# Initialize button on Pin 0 (GP0)
btn = Button(0)

# Callback for double press (within 500ms window)
def on_double_press():
    print("DOUBLE press detected!")

# Callback for triple press (within 1000ms window)
def on_triple_press():
    print("TRIPLE press detected!")

# Register sequences: count, window_ms, callback
btn.on_sequence(2, 500, on_double_press)
btn.on_sequence(3, 1000, on_triple_press)

print("Starting sequences example. Try double and triple clicks on GP0.")

while True:
    btn.read()
    time.sleep_ms(10)
