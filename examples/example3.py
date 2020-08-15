import pyb
import time
import rk043fn48h as lcd
import lvgl as lv
import lvstm32

hres = 480
vres = 272
lv.init()
tick = lvstm32.lvstm32()
lcd.init(w=hres, h=vres)
disp_buf1 = lv.disp_buf_t()
buf1_1 = bytearray(hres * 10 * lv.color_t.SIZE)
buf1_2 = bytearray(hres * 10 * lv.color_t.SIZE)
disp_buf1.init(buf1_1, buf1_2, len(buf1_1) // lv.color_t.SIZE)
disp_drv = lv.disp_drv_t()
disp_drv.init()
disp_drv.buffer = disp_buf1
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

scr1 = lv.obj()
scr2 = lv.obj()
lv.scr_load(scr1)

slider = lv.slider(scr2)
slider.set_width(150)
slider.align(scr2, lv.ALIGN.IN_TOP_MID, 0, 15)

btn1 = lv.btn(scr1)
btn1.align(scr1, lv.ALIGN.IN_TOP_RIGHT, -5, 5)
label = lv.label(btn1)
label.set_text(">")

btn2 = lv.btn(scr2)
btn2.align(scr2, lv.ALIGN.IN_TOP_LEFT, 5, 5)
label2 = lv.label(btn2)
label2.set_text("<")

led1 = lv.led(scr2)
led1.align(slider, lv.ALIGN.OUT_RIGHT_MID, 10, 10)
led1.set_bright(slider.get_value() * 2)
led1.set_drag(True)
led1.set_size(20,20)


def slider_event_cb(slider, event):
    if event == lv.EVENT.VALUE_CHANGED:
        led1.set_bright(slider.get_value() * 2)


def btn1_event_cb(btn1, event):
    if event == lv.EVENT.CLICKED:
        lv.scr_load(scr2)


def btn2_event_cb(btn2, event):
    if event == lv.EVENT.CLICKED:
        lv.scr_load(scr1)


slider.set_event_cb(slider_event_cb)
btn1.set_event_cb(btn1_event_cb)
btn2.set_event_cb(btn2_event_cb)

# Create a keyboard
kb = lv.keyboard(scr1)
kb.set_cursor_manage(True)

# Create a text area. The keyboard will write here
ta = lv.textarea(scr1)
ta.set_width(450)
ta.set_height(70)
ta.align(kb, lv.ALIGN.OUT_TOP_MID, 0, -10)
ta.set_text("")

# Assign the text area to the keyboard
kb.set_textarea(ta)

# Create a Spinner object
spin = lv.spinner(scr2)
spin.set_size(100, 100)
spin.align(None, lv.ALIGN.CENTER, -5, 5)
spin.set_type(lv.spinner.TYPE.FILLSPIN_ARC)

