"""
slightly modified lv_example_chart_1.py
"""

import lvgl as lv

# TTGO T-Watch-2020 V2 using st7789 driver
#import twatch_portrait as driver
#import twatch_landscape as driver

# TTGO T-Display using st7789 driver
#import tdisplay_portrait as driver
#import tdisplay_landscape as driver

# st7735 displays using ili9341 driver
import portrait_128x160 as driver
#import portrait_128x128 as driver

# ili9342 on M5STACK display using st7789 driver
#import m5stack_portrait as driver
#import m5stack_landscape as driver

# ili9342 on M5 Core2 display using st7789 driver
#import core2_portrait as driver
#import core2_landscape as driver

driver.disp.init()

# Create a chart
chart = lv.chart(lv.scr_act())
chart.set_size(driver.disp.width, driver.disp.height)
chart.center()
chart.set_type(lv.chart.TYPE.LINE)   # Show lines and points too

# Add two data series
ser1 = chart.add_series(lv.palette_main(lv.PALETTE.RED), lv.chart.AXIS.PRIMARY_Y);
ser2 = chart.add_series(lv.palette_main(lv.PALETTE.GREEN), lv.chart.AXIS.SECONDARY_Y)
print(ser2)
# Set next points on ser1
chart.set_next_value(ser1,10)
chart.set_next_value(ser1,10)
chart.set_next_value(ser1,10)
chart.set_next_value(ser1,10)
chart.set_next_value(ser1,10)
chart.set_next_value(ser1,10)
chart.set_next_value(ser1,10)
chart.set_next_value(ser1,30)
chart.set_next_value(ser1,70)
chart.set_next_value(ser1,90)

# Directly set points on 'ser2'
ser2.y_points = [90, 70, 65, 65, 65, 65, 65, 65, 65, 65]
chart.refresh()      #  Required after direct set

