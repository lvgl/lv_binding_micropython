"""
slightly modified lv_example_label.py
"""

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

# Show line wrap, re-color, line align and text scrolling.

label1 = lv.label(lv.scr_act())
label1.set_long_mode(lv.label.LONG.WRAP)     # Break the long lines*/
# Enable re-coloring by commands in the text
label1.set_recolor(True)
label1.set_text("#0000ff Re-color# #ff00ff words# #ff0000 of a# label, align the lines to the center"
                " and  wrap long text automatically.")
# Set smaller width to make the lines wrap
label1.set_width(size)
label1.set_style_text_align(lv.ALIGN.CENTER, 0)
label1.align(lv.ALIGN.CENTER, 0, -20)

label2 = lv.label(lv.scr_act())
label2.set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)  # Circular scroll
label2.set_width(size)
label2.set_text("This is a circularly scrolling text.......")
label2.align(lv.ALIGN.CENTER, 0, 40)
