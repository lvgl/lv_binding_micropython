##############################################################################
# lv_async - helper class for using LVGL with asyncio
#
# Implements LVGL event loop using uasyncio
#
# Usage example:
#
#   import uasyncio
#   from async_utils import lv_async
#   lva = lv_async(refresh_func = SDL.refresh)
#   uasyncio.Loop.run_forever()
#

import uasyncio
import lvgl as lv

class lv_async:
    def __init__(self, refresh_func=None, refresh_rate=20):
        self.refresh_func = refresh_func
        self.refresh_rate = refresh_rate
        self.refresh_event = uasyncio.Event()
        self.refresh_task = uasyncio.create_task(self.refresh())
        self.timer_task = uasyncio.create_task(self.timer())

    async def refresh(self):
        while True:
            await self.refresh_event.wait()
            self.refresh_event.clear()
            lv.task_handler() 
            if self.refresh_func: self.refresh_func()

    async def timer(self):
        while True:
            await uasyncio.sleep_ms(self.refresh_rate)
            lv.tick_inc(self.refresh_rate)
            self.refresh_event.set()

