
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


# animation helper class

class anim(lv.anim_t):
    def __init__(self, obj, val, size, exec_cb, path_cb, time=500, playback = False, ready_cb=None):
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
        if ready_cb: lv.anim_set_ready_cb(self, ready_cb)
        lv.anim_create(self)

# animated button helper class 

class btn(lv.btn):
    def __init__(self, parent, text):
        super().__init__(parent)
        self.align(parent, lv.ALIGN.CENTER, 0, 0)
        label = lv.label(self)
        label.set_text(text)
        self.set_event_cb(self.btn_event)

    def btn_event(self, obj, ev):
        if ev == lv.EVENT.CLICKED:
            self.a1 = anim(
                    self, 
                    self.get_x(), 
                    50, 
                    lv.btn.set_x, # register built-in lvgl function
                    lv.anim_path_ease_out, 
                    playback=True)

            self.a2 = anim(
                    self, 
                    self.get_y(), 
                    50, 
                    lambda a, val, self=self: self.set_y(val), # register custom micropython function
                    lv.anim_path_ease_in, 
                    playback=True)
                   

# Helper function to animate chart

def animate_chart(chart, val, size):
    def anim_phase1():
        anim(
            chart, 
            val, 
            size, 
            lambda a, val: chart.set_range(0, val), 
            lv.anim_path_ease_in, 
            ready_cb=lambda a:anim_phase2(),
            time=2000)

    def anim_phase2():
        anim(
            chart, 
            val+size, 
            -size, 
            lambda a, val: chart.set_range(0, val), 
            lv.anim_path_ease_out, 
            ready_cb=lambda a:anim_phase1(),
            time=500)

    anim_phase1()

# Create a screen with a button and a label

lv.anim_core_init()

scr = lv.obj()
tabs = lv.tabview(scr)
tab1 = tabs.add_tab('Button')
tab2 = tabs.add_tab('Button')
tab3 = tabs.add_tab('Chart')
btn1 = btn(tab1, 'Button1')
btn2 = btn(tab2, 'Button2')

# Create chart

chart = lv.chart(tab3)
series1 = chart.add_series(lv.color_hex(0xFF0000))
chart.set_type(chart.TYPE.POINT | chart.TYPE.LINE)
chart.set_series_width(3)
chart.set_range(0,100)
chart.init_points(series1, 10)
chart.set_points(series1, [10,20,30,20,10,40,50,90,95,90])

# Load the screen and start animation

lv.scr_load(scr)
animate_chart(chart, 100, 1000)

