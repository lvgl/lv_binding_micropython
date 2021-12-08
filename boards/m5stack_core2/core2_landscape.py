from ili9XXX import st7789, LANDSCAPE
import axp202c

axp = axp202c.PMU(address=0x34)         # Init power management unit
axp.enablePower(axp202c.AXP192_LDO2)    # Turn on backlight
axp.setDC3Voltage(3000)                 # Set backlight voltage

# Configure the ili9341 display using the st7789 driver
disp = st7789(
    mosi=23, clk=18, cs=5, dc=15, rst=33, power=-1, backlight=-1, backlight_on=1,
    width=240, height=320, invert=True, rot=LANDSCAPE, initialize=False)
