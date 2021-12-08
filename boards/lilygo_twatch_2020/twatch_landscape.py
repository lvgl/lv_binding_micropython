from ili9XXX import st7789, REVERSE_LANDSCAPE
import axp202c

# init power manager, set backlight
axp = axp202c.PMU()
axp.enablePower(axp202c.AXP202_LDO2)
axp.setLDO2Voltage(2800)

# init display
disp = st7789(
    mosi=19, clk=18, cs=5, dc=27, rst=-1, backlight=12, power=-1,
    width=240, height=240, start_x=0, start_y=80,
    rot=REVERSE_LANDSCAPE, factor=4, initialize=False)
