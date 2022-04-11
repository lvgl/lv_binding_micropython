import sys
sys.path.append('.')
from st77xx import *
from xpt2046 import *


spi=machine.SPI(
    1,
    baudrate=24_000_000,
    polarity=0,
    phase=0,
    sck=machine.Pin(10,machine.Pin.OUT),
    mosi=machine.Pin(11,machine.Pin.OUT),
    miso=machine.Pin(12,machine.Pin.IN)
)

## TODO: measure fps gain w/ DMA
if 0:
    # with DMA, the repaints seem to be too slow? To be investigated
    # but we seem to be fine performance-wise without DMA anyway
    import rp2_dma
    rp2_dma=rp2_dma.DMA(0)
else: rp2_dma=None

import lvgl as lv
lv.init()

lcd=St7789(rot=3,res=(240,320),spi=spi,cs=9,dc=8,bl=13,rst=15,rp2_dma=rp2_dma)
lcd.set_backlight(30)
touch=Xpt2046(spi=spi,cs=16,rot=1)


def cb_btn(event): print("Hello World!")

scr=lv.obj()
btn=lv.btn(scr)
lbl=lv.label(btn)
lbl.set_text("Press me!")
btn.center()
btn.add_event_cb(cb_btn,lv.EVENT.CLICKED,None)
lv.scr_load(scr)

import lv_utils
import uasyncio
lv_utils.event_loop(refresh_cb=lv.task_handler,asynchronous=True)
uasyncio.Loop.run_forever()
