# A simple test for Linux Frame Buffer
# Imports fb (frame buffer) module and uses it as lvgl display driver
# then show a button on screen.

import lvgl as lv
lv.init()
import fb
fb.init()
disp_drv = lv.disp_drv_t()
lv.disp_drv_init(disp_drv)
disp_drv.disp_flush = fb.flush
disp_drv.disp_fill = fb.fill
disp_drv.disp_map = fb.map
lv.disp_drv_register(disp_drv)

scr = lv.obj()
btn = lv.btn(scr)
btn.align(lv.scr_act(), lv.ALIGN.CENTER, 0, 0)
label = lv.label(btn)
label.set_text("Button")

# Load the screen

lv.scr_load(scr)

# while True:
#    pass
