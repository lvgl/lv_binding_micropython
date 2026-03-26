from machine import I2C, SoftI2C, Pin
import st_ltdc
import touch_i2c
import lv_utils
import lvgl as lv

def init_display(panel, board, asynchronous=False, exception_sink=None):
    """Initialize LTDC + Touch using config panel + board."""

    if lv.is_initialized():
        lv.deinit()
    lv.init()
    event_loop = lv_utils.event_loop(
            asynchronous=asynchronous,
            exception_sink=exception_sink
    )

    # Display
    params = {
        "width":   panel.WIDTH,
        "height":  panel.HEIGHT,
        "hsync":   panel.HSYNC, "hbp": panel.HBP, "hfp": panel.HFP,
        "vsync":   panel.VSYNC, "vbp": panel.VBP, "vfp": panel.VFP,
        "fb_addr": getattr(board, 'FB_ADDR', 0xC0000000),
        "bl":      Pin(board.BL_PIN, Pin.OUT),
        "polarity": panel.POLARITY,
    }

    if hasattr(board, 'RST_PIN') and board.RST_PIN != "":
        params["rst"] = Pin(board.RST_PIN, Pin.OUT)

    disp = st_ltdc.LTDC(**params)
    disp_drv = lv.display_create(panel.WIDTH, panel.HEIGHT)
    disp_drv.set_color_format(lv.COLOR_FORMAT.RGB565)
    disp.init(disp_drv)
    buf1 = disp.framebuffer(1)
    buf2 = disp.framebuffer(2)
    disp_drv.set_buffers(buf1, buf2, len(buf1), lv.DISPLAY_RENDER_MODE.DIRECT)
    disp_drv.set_flush_cb(disp.flush)

    # Touch
    tp_rst = Pin(board.TP_RST_PIN, Pin.OUT)
    tp_int = Pin(board.TP_INT_PIN, Pin.IN)

    if hasattr(board, 'TP_I2C_NUM') and board.TP_I2C_NUM > 0:
        tp_i2c = I2C(board.TP_I2C_NUM)
    else:
        tp_i2c = SoftI2C(
            scl=Pin(board.TP_SCL_PIN),
            sda=Pin(board.TP_SDA_PIN),
            freq=100000
        )

    touch = touch_i2c.TP(device=panel.TOUCH_TYPE, i2c=tp_i2c, tp_rst=tp_rst, tp_int=tp_int)
    indev = lv.indev_create()
    indev.set_type(lv.INDEV_TYPE.POINTER)
    indev.set_read_cb(touch.tp_read)

    return disp, touch
