import lvgl as lv
import sys
import asyncio
import os

sys.path.append("..")
sys.path.append(os.getcwd())
import testrunner

# Calibrate indev with canvas


class TestCanvas(lv.obj):
    def __init__(self, parent, display):
        super().__init__(parent)

        self.set_style_bg_color(lv.color_black(), 0)
        self.set_size(lv.pct(100), lv.pct(100))
        self.set_style_pad_all(0, 0)
        self.set_style_pad_top(0, 0)
        self.set_style_radius(0, 0)
        self.set_style_margin_bottom(0, 0)
        self.set_style_margin_top(0, 0)
        self.set_style_margin_left(0, 0)
        self.set_style_margin_right(0, 0)
        self.set_style_border_width(0, 0)
        self.set_style_outline_width(0, 0)
        self.center()
        self.WIDTH = display.width
        self.HEIGHT = display.width

        self.X_OFFSET = round(self.WIDTH / 2)
        self.Y_OFFSET = self.X_OFFSET
        self.debug = True
        self.event_press = asyncio.Event()

        self._cbuf = lv.draw_buf_create(
            self.WIDTH, self.HEIGHT, lv.COLOR_FORMAT.RGB888, 0
        )
        self.canvas = lv.canvas(self)
        self.canvas.set_draw_buf(self._cbuf)
        self.canvas.fill_bg(lv.color_white(), lv.OPA.TRANSP)
        self.canvas.center()

        # Coordinates label
        self._xy_lab = lv.label(self)
        self._xy_lab.align(lv.ALIGN.TOP_LEFT, 5, 10)  # FIX:
        self._xy_lab.set_text(f"X: {0} Y: {0}")
        self._xy_lab.set_style_text_color(lv.color_make(0, 255, 0), 0)

        # Draw callback
        def press_cb(event):
            indev = lv.indev_active()
            if indev:
                _point = lv.point_t()
                indev.get_point(_point)
                y = -self.canvas.get_y() + _point.y - round(self.HEIGHT / 2)
                x = -self.canvas.get_x() + _point.x - round(self.WIDTH / 2)
                if self.debug:
                    print(f"x:{x}, y:{y}")
                    # draw a red point
                self.canvas.set_px(
                    x + self.X_OFFSET,
                    y + self.Y_OFFSET,
                    lv.color_make(255, 0, 0),
                    lv.OPA.COVER,
                )

                self._xy_lab.set_text(f"X: {x} Y: {y}")
                self.event_press.set()

        self.canvas.add_event_cb(lambda event: press_cb(event), lv.EVENT.PRESSING, None)
        self.canvas.add_flag(lv.obj.FLAG.CLICKABLE)

        # Clear button
        self._cl_btn = lv.button(self)
        self._cl_btn.align(lv.ALIGN.BOTTOM_LEFT, 4, -4)

        self._cl_btn.set_style_bg_color(lv.color_make(0, 255, 0), 0)
        self._cl_btn.set_size(lv.pct(25), lv.pct(10))
        self._lab = lv.label(self._cl_btn)
        self._lab.set_text("CLEAR")
        self._lab.center()

        def clear_cb(event):
            self.canvas.fill_bg(lv.color_white(), lv.OPA.TRANSP)

        self._cl_btn.add_event_cb(lambda event: clear_cb(event), lv.EVENT.PRESSED, None)


async def calib(scr, display=None):
    tc = TestCanvas(scr, display.display_drv)
    print("INDEV CALIBRATION TOOL")
    while True:
        await tc.event_press.wait()
        tc.event_press.clear()
        await asyncio.sleep_ms(100)


__file__ = globals().get("__file__", "test")

try:
    import display_config

    display_config.MODE = "interactive"
    display_config.POINTER = "interactive"
except Exception:
    display_config = testrunner.display_config

testrunner.run(calib, __file__, disp_config=display_config)
testrunner.devicereset()
