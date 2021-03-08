##################################################################################################
#
# Example of LVGL with uasyncio event loop on unix and esp32 ports
#
# Running on Linux: (need micropython-dev for uasyncio):
#   ports/unix/micropython-dev -i lib/lv_bindings/examples/uasyncio_example1.py
#
#
##################################################################################################

# Workaround for including frozen modules when running micropython with a script argument
# https://github.com/micropython/micropython/issues/6419
import sys
sys.path.append("")

# Imports

from urandom import getrandbits, seed
from utime import ticks_us
from uasyncio import sleep, create_task, Loop, CancelledError
from async_utils import lv_async
import lvgl as lv

seed(ticks_us())
lv.init()

##################################################################################################
# Display initialization
##################################################################################################

# Default resolution match ili9341
HOR_RES = 240
VER_RES = 320

# Try initialize ili9341/xpt2046
try:
    from ili9XXX import ili9341
    from xpt2046 import xpt2046

    # Initialize and register drivers

    disp = ili9341(dc=32, cs=33, power=-1, backlight=-1, asynchronous=True, initialize=True)
    touch = xpt2046()

    # Call LVGL event loop from uasyncio task

    lva = lv_async()

except ImportError:
    pass

# Try to initialize SDL
try:
    import SDL

    # Initialize driver

    SDL.init(w=HOR_RES, h=VER_RES, auto_refresh=False)

    # Register SDL display driver.

    disp_buf1 = lv.disp_buf_t()
    buf1_1 = bytearray(HOR_RES * 10)
    disp_buf1.init(buf1_1, None, len(buf1_1)//4)
    disp_drv = lv.disp_drv_t()
    disp_drv.init()
    disp_drv.buffer = disp_buf1
    disp_drv.flush_cb = SDL.monitor_flush
    disp_drv.hor_res = HOR_RES
    disp_drv.ver_res = VER_RES
    disp_drv.register()

    # Regsiter SDL mouse driver

    indev_drv = lv.indev_drv_t()
    indev_drv.init() 
    indev_drv.type = lv.INDEV_TYPE.POINTER
    indev_drv.read_cb = SDL.mouse_read
    indev_drv.register();

    # Call LVGL event loop from uasyncio task

    lva = lv_async(refresh_func = SDL.refresh)

except ImportError:
    pass


##################################################################################################
# Stylized Message Box class
##################################################################################################

class MsgBox(lv.win):
    def __init__(self, parent):

        super().__init__(parent)
        self.set_title("Pop")
        msg_box_close_btn = self.add_btn_right(lv.SYMBOL.CLOSE)
        msg_box_close_btn.set_event_cb(lambda obj,e:  e == lv.EVENT.RELEASED and self.close_msg_box())
        self.set_style_local_pad_left(self.PART.HEADER, lv.STATE.DEFAULT, 20)
        self.set_style_local_bg_color(self.PART.HEADER, lv.STATE.DEFAULT, lv.color_hex3(0xFEE))
        self.set_style_local_bg_color(self.PART.BG, lv.STATE.DEFAULT, lv.color_hex3(0xFFF))
        self.set_style_local_border_side(self.PART.HEADER, lv.STATE.DEFAULT, lv.BORDER_SIDE.LEFT | lv.BORDER_SIDE.RIGHT | lv.BORDER_SIDE.TOP)
        self.set_style_local_border_width(self.PART.HEADER, lv.STATE.DEFAULT, 4)
        self.set_style_local_border_color(self.PART.HEADER, lv.STATE.DEFAULT, lv.color_hex3(0xF88))
        self.set_style_local_border_width(self.PART.BG, lv.STATE.DEFAULT, 4)
        self.set_style_local_border_color(self.PART.BG, lv.STATE.DEFAULT, lv.color_hex3(0xF88))
        self.set_style_local_shadow_color(self.PART.BG, lv.STATE.DEFAULT, lv.color_hex3(0x000))
        self.set_style_local_shadow_opa(self.PART.BG, lv.STATE.DEFAULT, 50)
        self.set_style_local_shadow_width(self.PART.BG, lv.STATE.DEFAULT, 20)
        self.set_style_local_shadow_ofs_x(self.PART.BG, lv.STATE.DEFAULT, 10)
        self.set_style_local_shadow_ofs_y(self.PART.BG, lv.STATE.DEFAULT, 10)
        self.set_style_local_shadow_spread(self.PART.BG, lv.STATE.DEFAULT, 0)
        self.set_style_local_radius(self.PART.HEADER, lv.STATE.DEFAULT, 10)
        self.set_style_local_radius(self.PART.BG, lv.STATE.DEFAULT, 10)
        self.set_content_size(100,40)
        self.set_layout(lv.LAYOUT.CENTER)
        self.label = lv.label(self)
        self.set_top(True)
        self.set_drag(True)

        self.opened = True;

    def is_open(self):
        return self.opened

    def close_msg_box(self):
        if self.is_open():
            self.anim = lv.anim_t()
            self.anim.init()
            self.anim.set_var(self)
            self.anim.set_time(500)
            self.anim.set_values(lv.OPA.COVER,lv.OPA.TRANSP)
            self.anim.set_custom_exec_cb(lambda obj, val:
                    self.set_style_local_opa_scale(self.PART.BG, lv.STATE.DEFAULT, val))
            self.anim.set_path(
                    lv.anim_path_t({'cb': lv.anim_path_t.ease_in}))
            self.anim.set_ready_cb(lambda a: self.del_async())
            lv.anim_t.start(self.anim)
            self.opened = False

    def set_text(self, txt):

        # If the msg box is already closed, cancel the calling task
        if not self.is_open():
            raise CancelledError()

        self.label.set_text(txt)

##################################################################################################
# Async task
##################################################################################################

async def btn_event_task(obj=None, event=-1):

    # Create and position the a new msg box

    msg_box = MsgBox(scr)
    msg_box.align(scr, lv.ALIGN.CENTER, getrandbits(7) - 64, getrandbits(7) - 64)

    # Countdown

    for i in range(10, 0, -1):
        msg_box.set_text(str(i))
        await sleep(1)

    # Close the msg box

    msg_box.close_msg_box()

##################################################################################################
# Create objects and screen
##################################################################################################

scr = lv.obj()
btn = lv.btn(scr)
btn.align(scr, lv.ALIGN.IN_TOP_MID, 0, 10)
btn.set_event_cb(
        lambda obj,e: e == lv.EVENT.CLICKED and create_task(btn_event_task()))
label = lv.label(btn)
label.set_text('Click Me Again!')
lv.scr_load(scr)

##################################################################################################
# Start event loop
##################################################################################################

Loop.run_forever()

