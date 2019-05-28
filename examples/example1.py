# init

import lvgl as lv
lv.init()

import SDL
SDL.init()

# Register SDL display driver.

disp_buf1 = lv.disp_buf_t()
buf1_1 = bytes(480*10)
lv.disp_buf_init(disp_buf1,buf1_1, None, len(buf1_1)//4)
disp_drv = lv.disp_drv_t()
lv.disp_drv_init(disp_drv)
disp_drv.buffer = disp_buf1
disp_drv.flush_cb = SDL.monitor_flush
disp_drv.hor_res = 480
disp_drv.ver_res = 320
lv.disp_drv_register(disp_drv)

# Regsiter SDL mouse driver

indev_drv = lv.indev_drv_t()
lv.indev_drv_init(indev_drv) 
indev_drv.type = lv.INDEV_TYPE.POINTER;
indev_drv.read_cb = SDL.mouse_read;
lv.indev_drv_register(indev_drv);

class anim(lv.anim_t):
    def __init__(self, obj, val, size, exec_cb, path_cb, time=500, playback = False):
        super().__init__()
        lv.anim_init(self)
        lv.anim_set_time(self, time, 0)
        lv.anim_set_values(self, val, val+size)
        try:
            lv.anim_set_exec_cb(self, obj, exec_cb)
        except TypeError:
            lv.anim_set_custom_exec_cb(self, exec_cb)
        lv.anim_set_path_cb(self, path_cb )
        if playback: lv.anim_set_playback(self, 0)
        lv.anim_create(self)

class btn(lv.btn):
    def __init__(self, parent, text):
        super().__init__(parent)
        self.align(parent, lv.ALIGN.CENTER, 0, 0)
        label = lv.label(self)
        label.set_text(text)
        self.set_event_cb(self.btn_event)

    def btn_event(self, obj, ev):
        if ev == lv.EVENT.CLICKED:
            print("CLICKED!")
            self.a1 = anim(self, self.get_x(), 50, lv.btn.set_x, lv.anim_path_ease_out, playback=True)
            self.a2 = anim(self, self.get_y(), 50, lambda a, val, self=self: self.set_y(val), lv.anim_path_ease_in, playback=True)
                   

# Create a screen with a button and a label

lv.anim_core_init()

scr = lv.obj()
tabs = lv.tabview(scr)
tab1 = tabs.add_tab('Tab1')
tab2 = tabs.add_tab('Tab2')
btn1 = btn(tab1, 'Button1')
btn2 = btn(tab2, 'Button2')

# Load the screen

lv.scr_load(scr)


