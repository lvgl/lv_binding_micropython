# Module for advancing tick count and scheduling async event for lvgl
# Import after lvgl module.
#
# MIT license; Copyright (c) 2021 Amir Gonnen

import lvgl as lv
import micropython

# Try standard machine.Timer, or custom timer from lv_timer, if available

try:
    from machine import Timer
except:
    try:
        from lv_timer import Timer
    except:
        raise RuntimeError("Missing machine.Timer implementation!")

class event_loop():

    _is_running = False

    def __init__(self, freq=25, timer_id=4, max_scheduled=2, refresh_cb=None):
        if self.is_running():
            raise RuntimeError("Event loop is already running!")
        event_loop._is_running = True
        self.task_handler_ref = self.task_handler  # Allocation occurs here
        self.delay = 1000 // freq
        self.timer = Timer(timer_id)
        self.timer_cb_ref = self.timer_cb
        self.timer.init(mode=Timer.PERIODIC, period=self.delay, callback=self.timer_cb_ref)
        self.max_scheduled = max_scheduled
        self.scheduled = 0
        self.refresh_cb = refresh_cb

    def deinit(self):
        self.timer.deinit()
        event_loop._is_running = False

    @staticmethod
    def is_running():
        return event_loop._is_running

    def task_handler(self, _):
        lv.task_handler()
        if self.refresh_cb: self.refresh_cb()
        self.scheduled -= 1

    def timer_cb(self, t):
        # Can be called in Interrupt context
        # Use task_handler_ref since passing self.task_handler would cause allocation.
        lv.tick_inc(self.delay)
        if self.scheduled < 2:
            try:
                micropython.schedule(self.task_handler_ref, 0)
                self.scheduled += 1
            except:
                pass
