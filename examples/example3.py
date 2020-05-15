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
lv.disp_buf_init(disp_buf1, buf1_1, buf1_2, len(buf1_1) // lv.color_t.SIZE)
disp_drv = lv.disp_drv_t()
lv.disp_drv_init(disp_drv)
disp_drv.buffer = disp_buf1
disp_drv.flush_cb = lcd.flush
disp_drv.gpu_blend_cb = lcd.gpu_blend
disp_drv.gpu_fill_cb = lcd.gpu_fill
disp_drv.hor_res = hres
disp_drv.ver_res = vres
lv.disp_drv_register(disp_drv)

indev_drv = lv.indev_drv_t()
lv.indev_drv_init(indev_drv)
indev_drv.type = lv.INDEV_TYPE.POINTER
indev_drv.read_cb = lcd.ts_read
lv.indev_drv_register(indev_drv)

th = lv.theme_material_init(10, lv.font_roboto_16)
# th = lv.theme_alien_init(160, lv.font_roboto_16)
# th = lv.theme_zen_init(120, lv.font_roboto_16)
# th = lv.theme_nemo_init(180, lv.font_roboto_16)
lv.theme_set_current(th)

scr1 = lv.obj()
scr2 = lv.obj()
lv.scr_load(scr1)

slider = lv.slider(scr2)
slider.set_width(200)
slider.align(scr2, lv.ALIGN.IN_TOP_MID, 0, 15)

btn1 = lv.btn(scr1)
btn1.align(scr1, lv.ALIGN.IN_TOP_RIGHT, -5, 5)
label = lv.label(btn1)
label.set_text(">")

btn2 = lv.btn(scr2)
btn2.align(scr2, lv.ALIGN.IN_TOP_LEFT, 5, 5)
label2 = lv.label(btn2)
label2.set_text("<")

style_led = lv.style_t()
lv.style_copy(style_led, lv.style_pretty_color)
style_led.body.radius = 800
style_led.body.main_color = lv.color_make(0xB5, 0x0F, 0x04)
style_led.body.grad_color = lv.color_make(0x50, 0x07, 0x02)
style_led.body.border.color = lv.color_make(0xFA, 0x0F, 0x00)
style_led.body.border.width = 3
style_led.body.border.opa = lv.OPA._30
style_led.body.shadow.color = lv.color_make(0xB5, 0x0F, 0x04)
style_led.body.shadow.width = 5

led1 = lv.led(scr2)
# led1.set_style(lv.led.STYLE.MAIN, style_led)
led1.align(slider, lv.ALIGN.OUT_RIGHT_MID, 10, 0)
led1.set_bright(slider.get_value() * 2)
led1.set_drag(True)


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

# Create styles for the keyboard
rel_style = lv.style_t()
pr_style = lv.style_t()

lv.style_copy(rel_style, lv.style_btn_rel)
rel_style.body.radius = 0
rel_style.body.border.width = 1

lv.style_copy(pr_style, lv.style_btn_pr)
pr_style.body.radius = 0
pr_style.body.border.width = 1

# Create a keyboard and apply the styles
kb = lv.kb(scr1)
kb.set_cursor_manage(True)

# Create a text area. The keyboard will write here
ta = lv.ta(scr1)
ta.set_width(450)
ta.set_height(70)
ta.align(kb, lv.ALIGN.OUT_TOP_MID, 0, -10)
ta.set_text("")

# Assign the text area to the keyboard
kb.set_ta(ta)

# Create a style for the Preloader
style = lv.style_t()
lv.style_copy(style, lv.style_plain)
style.line.width = 10  # 10 px thick arc
style.line.color = lv.color_hex3(0x258)  # Blueish arc color

style.body.border.color = lv.color_hex3(0xBBB)  # Gray background color
style.body.border.width = 0  # 11
style.body.padding.left = 0

# Create a Preloader object
preload = lv.preload(scr2)
preload.set_size(100, 100)
preload.align(None, lv.ALIGN.CENTER, -5, 5)
# preload.set_style(lv.preload.STYLE.MAIN, style)
preload.set_type(lv.preload.TYPE.FILLSPIN_ARC)

