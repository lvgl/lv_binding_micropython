'''
Generic st7735 128x160 LCD module on esp32
'''

from ili9XXX import st7735, COLOR_MODE_RGB, MADCTL_MX, MADCTL_MY

disp = st7735(
    mhz=15, mosi=19, clk=18, cs=13, dc=12, rst=4, power=-1, backlight=15, backlight_on=1,
    width=128, height=160, initialize=False)
