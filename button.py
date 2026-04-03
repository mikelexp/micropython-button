# MicroPython Button Library
# Polling-based button handler with debounce, short press, long press, and sequences.
# Port of EasyButton (https://github.com/evert-arias/EasyButton)
#
# MIT License
# Copyright (c) 2024 Your Name

from machine import Pin
from time import ticks_ms, ticks_diff

_MAX_SEQUENCES = 5


class _Sequence:
    def __init__(self, count, duration_ms):
        self._count = count
        self._duration = duration_ms
        self._first_press_time = 0
        self._press_count = 0

    def reset(self):
        self._press_count = 0
        self._first_press_time = 0

    def new_press(self, now):
        """Call on each release. Returns True when sequence completes."""
        if self._first_press_time == 0:
            self._first_press_time = now
            self._press_count = 1
        elif ticks_diff(now, self._first_press_time) > self._duration:
            # Window expired — restart count from this press
            self._first_press_time = now
            self._press_count = 1
        else:
            self._press_count += 1

        if self._press_count >= self._count:
            self.reset()
            return True
        return False


class Button:
    """
    Polling-based button handler with debounce, short press, long press,
    and multi-press sequence detection.

    Parameters
    ----------
    pin         : int or machine.Pin  — GPIO number or Pin object
    debounce_ms : int  — debounce window in ms (default 35)
    pull_up     : bool — enable internal pull-up (default True)
    active_low  : bool — LOW = pressed (default True)
    """

    def __init__(self, pin, debounce_ms=35, pull_up=True, active_low=True):
        if isinstance(pin, int):
            pull = Pin.PULL_UP if pull_up else None
            self._pin = Pin(pin, Pin.IN, pull)
        else:
            self._pin = pin

        self._db_time = debounce_ms
        self._active_low = active_low

        self._pressed_cb = None
        self._pressed_for_cb = None
        self._held_threshold = 0

        self._sequences = []
        self._sequence_cbs = []

        self._was_held = False
        self._held_cb_called = False

        now = ticks_ms()
        raw = self._pin.value()
        self._current_state = bool(raw ^ self._active_low)
        self._last_state = self._current_state
        self._changed = False
        self._time = now
        self._last_change = now

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def on_pressed(self, callback):
        """Callback fires on release after a short press (suppressed after long press)."""
        self._pressed_cb = callback

    def on_pressed_for(self, duration_ms, callback):
        """Callback fires once when button is held for duration_ms (while still held)."""
        self._held_threshold = duration_ms
        self._pressed_for_cb = callback

    def on_sequence(self, count, duration_ms, callback):
        """Callback fires when button is pressed count times within duration_ms.
        Up to _MAX_SEQUENCES sequences can be registered."""
        if len(self._sequences) >= _MAX_SEQUENCES:
            return
        self._sequences.append(_Sequence(count, duration_ms))
        self._sequence_cbs.append(callback)

    # ------------------------------------------------------------------
    # State queries  (valid after read())
    # ------------------------------------------------------------------

    def is_pressed(self):
        """Button is currently pressed."""
        return self._current_state

    def is_released(self):
        """Button is currently released."""
        return not self._current_state

    def was_pressed(self):
        """Button transitioned to pressed on the last read()."""
        return self._current_state and self._changed

    def was_released(self):
        """Button transitioned to released on the last read()."""
        return not self._current_state and self._changed

    def pressed_for(self, duration_ms):
        """Currently pressed AND held for at least duration_ms."""
        return self._current_state and ticks_diff(self._time, self._last_change) >= duration_ms

    def released_for(self, duration_ms):
        """Currently released AND has been released for at least duration_ms."""
        return not self._current_state and ticks_diff(self._time, self._last_change) >= duration_ms

    # ------------------------------------------------------------------
    # Main poll method — call every loop iteration
    # ------------------------------------------------------------------

    def read(self):
        """Poll the button. Returns True if currently pressed."""
        now = ticks_ms()
        self._time = now

        raw = self._pin.value()
        current = bool(raw ^ self._active_low)

        # Debounce: ignore transitions within db_time of the last one
        if ticks_diff(now, self._last_change) < self._db_time:
            self._changed = False
            return self._current_state

        self._last_state = self._current_state
        self._current_state = current
        self._changed = self._last_state != self._current_state
        if self._changed:
            self._last_change = now

        if self.was_released():
            if not self._was_held:
                # Short press
                if self._pressed_cb:
                    self._pressed_cb()
                # Sequence detection
                for i, seq in enumerate(self._sequences):
                    if seq.new_press(now):
                        cb = self._sequence_cbs[i]
                        if cb:
                            cb()
            else:
                self._was_held = False
            self._held_cb_called = False

        if self._current_state:
            self._check_pressed_time(now)

        return self._current_state

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _check_pressed_time(self, now):
        """Fires the long-press callback exactly once per hold event."""
        if (self._pressed_for_cb
                and not self._held_cb_called
                and self._held_threshold > 0
                and ticks_diff(now, self._last_change) >= self._held_threshold):
            self._was_held = True
            self._held_cb_called = True
            # Long press clears all sequence counters
            for seq in self._sequences:
                seq.reset()
            self._pressed_for_cb()
