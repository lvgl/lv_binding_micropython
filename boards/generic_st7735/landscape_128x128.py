'''
Generic st7735 128x128 LCD module on esp32
'''

from ili9XXX import st7735, MADCTL_MV, MADCTL_MY

disp = st7735(
    mhz=15, mosi=19, clk=18, cs=13, dc=12, rst=4, power=-1, backlight=15, backlight_on=1,
    width=128, height=128, start_x=2, start_y=1, initialize=False)
