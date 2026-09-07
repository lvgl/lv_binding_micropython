# panels.py
# Polarity Bitmask:
# [bit 0] HSYNC: 0=Active Low, 1=Active High
# [bit 1] VSYNC: 0=Active Low, 1=Active High
# [bit 2] DE:    0=Active Low, 1=Active High
# [bit 3] PIXCLK: 0=Not Inverted, 1=Inverted

class IPS1024x600:
    WIDTH  = 1024
    HEIGHT = 600
    HSYNC, HBP, HFP = 7, 164, 149
    VSYNC, VBP, VFP = 5, 22, 11
    POLARITY = 0
    TOUCH_TYPE = "GT911"

class RGB043M2:
    WIDTH  = 800
    HEIGHT = 480
    HSYNC, HBP, HFP = 4, 40, 40
    VSYNC, VBP, VFP = 4, 13, 13
    POLARITY = 8 # Pixel Clock polarity = Inverted
    TOUCH_TYPE = "GT911"