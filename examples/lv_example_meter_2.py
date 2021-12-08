"""
slightly modified lv_example_meter_2.py
"""

import utime as time
import lvgl as lv

# TTGO T-Watch-2020 V2 using st7789 driver
#import twatch_portrait as driver
#import twatch_landscape as driver

# TTGO T-Display using st7789 driver
import tdisplay_portrait as driver
#import tdisplay_landscape as driver

# st7735 displays using ili9341 driver
#import portrait_128x160 as driver
#import portrait_128x128 as driver

# ili9342 on M5STACK display using st7789 driver
#import m5stack_portrait as driver
#import m5stack_landscape as driver

# ili9342 on M5 Core2 display using st7789 driver
#import core2_portrait as driver
#import core2_landscape as driver

driver.disp.init()
size = min(driver.disp.width, driver.disp.height)

def set_value(indic,v):
    meter.set_indicator_end_value(indic, v)

#
# A meter with multiple arcs
#

meter = lv.meter(lv.scr_act())
meter.center()
meter.set_size(size, size)

# Remove the circle from the middle
meter.remove_style(None, lv.PART.INDICATOR)

# Add a scale first
scale = meter.add_scale()
meter.set_scale_ticks(scale, 11, 2, 10, lv.palette_main(lv.PALETTE.GREY))
meter.set_scale_major_ticks(scale, 1, 2, 30, lv.color_hex3(0xeee), 10 if size > 135 else -35)
meter.set_scale_range(scale, 0, 100, 270, 90)

# Add a three arc indicator
if size > 135:
    indic1 = meter.add_arc(scale, 10, lv.palette_main(lv.PALETTE.RED), 0)
    indic2 = meter.add_arc(scale, 10, lv.palette_main(lv.PALETTE.GREEN), -10)
    indic3 = meter.add_arc(scale, 10, lv.palette_main(lv.PALETTE.BLUE), -20)
else:
    indic1 = meter.add_arc(scale, 5, lv.palette_main(lv.PALETTE.RED), -5)
    indic2 = meter.add_arc(scale, 5, lv.palette_main(lv.PALETTE.GREEN), -10)
    indic3 = meter.add_arc(scale, 5, lv.palette_main(lv.PALETTE.BLUE), -15)

# Create an animation to set the value
a1 = lv.anim_t()
a1.init()
a1.set_values(0, 100)
a1.set_time(2000)
a1.set_repeat_delay(100)
a1.set_playback_delay(100)
a1.set_playback_time(500)
a1.set_var(indic1)
a1.set_repeat_count(lv.ANIM_REPEAT.INFINITE)
a1.set_custom_exec_cb(lambda a,val: set_value(indic1,val))
lv.anim_t.start(a1)

a2 = lv.anim_t()
a2.init()
a2.set_values(0, 100)
a2.set_time(1000)
a2.set_repeat_delay(100)
a2.set_playback_delay(100)
a2.set_playback_time(1000)
a2.set_var(indic2)
a2.set_repeat_count(lv.ANIM_REPEAT.INFINITE)
a2.set_custom_exec_cb(lambda a,val: set_value(indic2,val))
lv.anim_t.start(a2)

a3 = lv.anim_t()
a3.init()
a3.set_values(0, 100)
a3.set_time(1000)
a3.set_repeat_delay(100)
a3.set_playback_delay(100)
a3.set_playback_time(2000)
a3.set_var(indic3)
a3.set_repeat_count(lv.ANIM_REPEAT.INFINITE)
a3.set_custom_exec_cb(lambda a,val: set_value(indic3,val))
lv.anim_t.start(a3)
