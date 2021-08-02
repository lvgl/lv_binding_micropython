import usys as sys
sys.path.append('') # See: https://github.com/micropython/micropython/issues/6419

import lv_utils
import lvgl as lv

try:
    import pyb
    import rk043fn48h as lcd

    hres = 480
    vres = 272
    lv.init()
    event_loop = lv_utils.event_loop()
    lcd.init(w=hres, h=vres)
    disp_buf1 = lv.disp_drwa_buf_t()
    buf1_1 = bytearray(hres * 10 * lv.color_t.__SIZE__)
    buf1_2 = bytearray(hres * 10 * lv.color_t.__SIZE__)
    disp_buf1.init(buf1_1, buf1_2, len(buf1_1) // lv.color_t.__SIZE__)
    disp_drv = lv.disp_drv_t()
    disp_drv.init()
    disp_drv.draw_buf = disp_buf1
    disp_drv.flush_cb = lcd.flush
    disp_drv.gpu_blend_cb = lcd.gpu_blend
    disp_drv.gpu_fill_cb = lcd.gpu_fill
    disp_drv.hor_res = hres
    disp_drv.ver_res = vres
    disp_drv.register()

    indev_drv = lv.indev_drv_t()
    indev_drv.init()
    indev_drv.type = lv.INDEV_TYPE.POINTER
    indev_drv.read_cb = lcd.ts_read
    indev_drv.register()

except ImportError:
    import display_driver


scr1 = lv.obj()
scr2 = lv.obj()
lv.scr_load(scr1)

slider = lv.slider(scr2)
slider.set_width(150)
slider.align(lv.ALIGN.TOP_MID, 0, 15)

btn1 = lv.btn(scr1)
btn1.align(lv.ALIGN.TOP_RIGHT, -5, 5)
label = lv.label(btn1)
label.set_text(">")

btn2 = lv.btn(scr2)
btn2.align(lv.ALIGN.TOP_LEFT, 5, 5)
label2 = lv.label(btn2)
label2.set_text("<")

led1 = lv.led(scr2)
led1.align(lv.ALIGN.CENTER, 0, 0)
led1.set_brightness(slider.get_value() * 2)
# led1.set_drag(True)
led1.set_size(20,20)


def slider_event_cb(event):
    led1.set_brightness(slider.get_value() * 2)

def btn1_event_cb(event):
    lv.scr_load(scr2)


def btn2_event_cb(event):
    lv.scr_load(scr1)

slider.add_event_cb(slider_event_cb, lv.EVENT.VALUE_CHANGED, None)
btn1.add_event_cb(btn1_event_cb, lv.EVENT.CLICKED, None)
btn2.add_event_cb(btn2_event_cb, lv.EVENT.CLICKED, None)

# Create a keyboard
kb = lv.keyboard(scr1)
# kb.set_cursor_manage(True)

# Create a text area. The keyboard will write here
ta = lv.textarea(scr1)
ta.set_width(450)
ta.set_height(70)
ta.align(lv.ALIGN.CENTER, 0, 0)
ta.set_text("")

# Assign the text area to the keyboard
kb.set_textarea(ta)

# Create a Spinner object
spin = lv.spinner(scr2, 1000, 100)
spin.set_size(100, 100)
spin.align(lv.ALIGN.CENTER, 0, 0)
# spin.set_type(lv.spinner.TYPE.FILLSPIN_ARC)
