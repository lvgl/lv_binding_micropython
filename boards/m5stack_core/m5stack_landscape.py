from ili9XXX import st7789, LANDSCAPE

# Configure the ili9341 display using the st7789 driver
disp = st7789(
    mosi=23, clk=18, cs=14, dc=27, rst=33, power=-1, backlight=32,
    width=240, height=320, invert=True, rot=LANDSCAPE, initialize=False)
