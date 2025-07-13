# adapted from https://github.com/bdbarnett/mpdisplay
# utils/lv_mpdisplay.py

import lvgl as lv
import hashlib
from binascii import hexlify
import lv_utils
import sys
import asyncio


class TestDisplayConfig:
    WIDTH = 240
    HEIGHT = 320
    MODE = "sim"
    POINTER = "sim"
    COLOR_FORMAT = lv.COLOR_FORMAT.RGB888
    RENDER_MODE = lv.DISPLAY_RENDER_MODE.PARTIAL
    SHOW_INFO = True
    WINDOW_POS = (None, None)


class TestDisplayDriver:
    def __init__(
        self,
        display_drv,
        frame_buffer1,
        frame_buffer2,
        color_format=lv.COLOR_FORMAT.RGB565,
        mode="sim",
        pointer="sim",
        render_mode=lv.DISPLAY_RENDER_MODE.PARTIAL,
        fps=25,
    ):
        self.display_drv = display_drv
        self._color_size = lv.color_format_get_size(color_format)
        self._color_format = color_format
        self._frame_buffer1 = frame_buffer1
        self._frame_buffer2 = frame_buffer2
        self._x = 0
        self._y = 0
        self._dstate = None
        self._press_event = False
        self._release_event = False
        self._debug_press = True
        self._debug_release = True
        self.mode = mode

        if not lv_utils.event_loop.is_running():
            self.event_loop = lv_utils.event_loop(freq=fps, asynchronous=True)

        else:
            self.event_loop = lv_utils.event_loop.current_instance()
        self.event_loop.scheduled = 0

        if not lv.is_initialized():
            lv.init()

        if mode == "sim" or (
            mode == "interactive" and not isinstance(display_drv, DummyDisplay)
        ):
            if hasattr(display_drv, "blit"):
                self.lv_display = lv.display_create(
                    self.display_drv.width, self.display_drv.height
                )
                self.lv_display.set_color_format(color_format)
                self.lv_display.set_flush_cb(self._flush_cb)
                self.lv_display.set_buffers(
                    self._frame_buffer1,
                    self._frame_buffer2,
                    len(self._frame_buffer1),
                    render_mode,
                )
            if hasattr(display_drv, "set_frame_buffer"):
                display_drv.set_frame_buffer(self._frame_buffer1)

            if hasattr(display_drv, "set_display"):
                display_drv.set_display(self.lv_display)
            self.indev = lv.indev_create()
            self.indev.set_display(lv.display_get_default())
            self.indev.set_group(lv.group_get_default())
            # TODO: test other types of indev
            if pointer in ("sim", "interactive"):
                _indev_type = lv.INDEV_TYPE.POINTER

                if pointer == "interactive" and hasattr(display_drv, "indev_type"):
                    _indev_type = display_drv.indev_type
            else:
                _indev_type = getattr(lv.INDEV_TYPE, pointer.upper())

            self.indev.set_type(_indev_type)
            if hasattr(display_drv, "read_cb") and pointer != "sim":
                self.indev.set_read_cb(display_drv.read_cb)

            else:
                self.indev.set_read_cb(self._read_cb)

        else:  # interactive + DummyDisplay -> SDL
            self.group = lv.group_create()
            self.group.set_default()
            self.lv_display = lv.sdl_window_create(
                display_drv.width, display_drv.height
            )
            lv.sdl_window_set_title(self.lv_display, "MicroPython-LVGL")
            if hasattr(display_drv, "window_pos") and hasattr(
                lv, "sdl_window_set_position"
            ):
                if any(display_drv.window_pos):
                    lv.sdl_window_set_position(self.lv_display, *display_drv.window_pos)
                lv.sdl_window_set_opacity(self.lv_display, 1.0)
                lv.sdl_window_set_bordered(self.lv_display, 1)
            self.mouse = lv.sdl_mouse_create()
            self.keyboard = lv.sdl_keyboard_create()
            self.keyboard.set_group(self.group)
            if pointer in ("sim", "encoder"):
                self.indev = lv.indev_create()
                self.indev.set_display(self.lv_display)
                self.indev.set_group(self.group)
                self.indev.set_type(lv.INDEV_TYPE.POINTER)
                # NOTE: only one indev pointer allowed, use the keyboard
                # for interactive control
                self.indev.set_read_cb(self._read_cb)

    def set_test_name(self, name):
        self.display_drv.test_name = name

    def debug_indev(self, press=None, release=None):
        self._debug_press = press if press is not None else self._debug_press
        self._debug_release = release if release is not None else self._debug_release

    def debug_display(self, debug=True):
        if hasattr(self.display_drv, "debug"):
            self.display_drv.debug = debug

    async def touch(self, x, y, ms=100):
        self._x = x
        self._y = y
        self._dstate = lv.INDEV_STATE.PRESSED
        self._press_event = True
        await asyncio.sleep_ms(ms)

        self._dstate = lv.INDEV_STATE.RELEASED
        self._release_event = True
        await asyncio.sleep_ms(25)

    async def swipe(self, x1, y1, x2, y2, steps=5, ms=100):
        self._dstate = lv.INDEV_STATE.PRESSED
        if y1 == y2:  # HORIZONTAL
            self._y = y1
            self._x = x1
            if x2 < x1:
                steps = -steps  # RIGHT-LEFT
            for xi in range(x1, x2, steps):
                self._x = xi
                self._press_event = True
                await asyncio.sleep_ms(ms // steps)
        elif x1 == x2:
            self._y = y1
            self._x = x1
            if y2 < y1:
                steps = -steps  # BOTTOM-UP
            for yi in range(y1, y2, steps):
                self._y = yi
                self._press_event = True
                await asyncio.sleep_ms(ms // steps)

        self._dstate = lv.INDEV_STATE.RELEASED
        self._release_event = True
        await asyncio.sleep_ms(25)

    def _flush_cb(self, disp_drv, area, color_p):
        width = area.x2 - area.x1 + 1
        height = area.y2 - area.y1 + 1

        self.display_drv.blit(
            area.x1,
            area.y1,
            width,
            height,
            color_p.__dereference__(width * height * self._color_size),
        )
        self.lv_display.flush_ready()
        # FIXME: check if last in partial/direct render and call display.drv
        # show

    def _read_cb(self, indev, data):
        if self._press_event:
            self._press_event = False
            if self._debug_press:
                print(f"[PRESSED]: ({self._x},{self._y})")
            data.point = lv.point_t({"x": self._x, "y": self._y})
            data.state = self._dstate
        elif self._release_event:
            self._release_event = False
            if self._debug_release:
                print(f"[RELEASED]: ({self._x},{self._y})")
            data.state = self._dstate

    def screenshot(self, **kwargs):
        if hasattr(self.display_drv, "screenshot"):
            return self.display_drv.screenshot(**kwargs)


class DummyDisplay:
    def __init__(self, width=240, height=320, color_format=lv.COLOR_FORMAT.RGB565):
        self.width = width
        self.height = height
        self.color_depth = lv.color_format_get_bpp(color_format)
        self.color_size = lv.color_format_get_size(color_format)
        self.n = 0
        self.test_name = "testframe"
        self._header_set = True
        self._save_frame = sys.platform in ["darwin", "linux"]
        # TODO: use framebuf for snapshot
        self._debug = False
        if self._save_frame:
            self._pbuff = bytearray(self.color_size)
        self._save_frame = False

    @property
    def debug(self):
        return self._debug

    @debug.setter
    def debug(self, x):
        self._debug = x
        # self._save_frame = x

    def reverse_pixel(self, a):
        for i in range(len(a) - 1, -1, -1):
            self._pbuff[len(a) - 1 - i] = a[i]
        return self._pbuff

    def save_frame(self, data, w, h):
        if not self._header_set:
            self._header_set = True
            # print(self.test_name, f"{self.width}:{self.height}:{self.color_size}")
            with open(f"{self.test_name}.bin", "wb") as fr:
                fr.write(f"{self.width}:{self.height}:{self.color_size}\n".encode())
        # print(bytes(data))
        assert len(bytes(data[:])) == w * h * self.color_size

        with open(f"{self.test_name}.bin", "ab") as fr:
            pi = 0
            for py in range(0, h):
                for px in range(0, w):
                    try:
                        pixel = data[pi : pi + self.color_size]

                        fr.write(self.reverse_pixel(pixel))
                        # fr.write(bytes(pixel))
                        pi += self.color_size
                    except Exception:
                        print(pi)

    async def screenshot(self, name="screenshot", debug=False):
        _debug = self._debug
        self._debug = False
        self._save_frame = False

        # Reset
        self._rst_scr = lv.obj()
        c_scr = lv.screen_active()
        lv.screen_load(self._rst_scr)
        await asyncio.sleep_ms(500)

        # Load test screen
        self._save_frame = sys.platform in ["darwin", "linux"]
        self._header_set = False
        self._debug = debug
        _test_name = self.test_name
        self.test_name = f"{self.test_name}@{name}"
        print(f"SCREENSHOT @ {self.test_name.rsplit('/')[-1].split('.')[-1]}")
        lv.screen_load(c_scr)
        await asyncio.sleep_ms(500)

        self._debug = _debug
        self._save_frame = False
        self._header_set = True
        self.test_name = _test_name

    def _shasum_frame(self, data):
        _hash = hashlib.sha256()
        _hash.update(data)
        _result = _hash.digest()
        result = hexlify(_result).decode()
        return result

    def blit(self, x1, y1, w, h, buff):
        if self._save_frame:
            self.save_frame(buff, w, h)
        if self.debug:
            print(f"\nFRAME: {self.n} {(x1, y1, w, h, len(buff))}")
            print(self._shasum_frame(bytes(buff)))
            self.n += 1


tdisp = DummyDisplay(color_format=lv.COLOR_FORMAT.RGB888)

display_config = TestDisplayConfig
# alloc_buffer = lambda buffersize: memoryview(bytearray(buffer_size))

# factor = 10  ### Must be 1 if using an RGBBus
# double_buf = True  ### Must be False if using an RGBBus

# buffer_size = tdisp.width * tdisp.height * (tdisp.color_depth // 8) // factor

# fbuf1 = alloc_buffer(buffer_size)
# fbuf2 = alloc_buffer(buffer_size) if double_buf else None


def get_display(
    width=240,
    height=320,
    disp=tdisp,
    color_format=lv.COLOR_FORMAT.RGB888,
    mode="sim",
    pointer="sim",
    show_display_info=False,
    render_mode=lv.DISPLAY_RENDER_MODE.PARTIAL,
    window_pos=(None, None),
):
    print(f"DISPLAY_MODE: {mode.upper()}")
    print(f"INDEV_MODE: {pointer.upper()}")

    if mode == "sim":
        show_display_info = True
        disp = tdisp
        disp.width = width
        disp.height = height
    elif mode == "interactive":
        disp.width = width
        disp.height = height
        try:
            from hwdisplay import HwDisplayDriver

            disp = HwDisplayDriver(
                width=width, height=height, color_format=color_format
            )
        except Exception as e:
            if sys.platform not in ["darwin", "linux"]:
                sys.print_exception(e)
            else:
                disp.window_pos = window_pos
    assert hasattr(disp, "width") is True, "expected width attribute in display driver"
    assert hasattr(disp, "height") is True, (
        "expected height attribute in display driver"
    )

    assert hasattr(disp, "color_depth") is True, (
        "expected color_depth attribute in display driver"
    )

    if show_display_info:
        _cf = {v: k for k, v in lv.COLOR_FORMAT.__dict__.items() if k != "NATIVE"}
        print(f"COLOR_FORMAT: {_cf.get(color_format, 'UNKNOWN')}")
        print(f"DISPLAY_SIZE: {width} x {height}")

    alloc_buffer = lambda buffersize: memoryview(bytearray(buffer_size))

    if render_mode == lv.DISPLAY_RENDER_MODE.PARTIAL:
        factor = 10  ### Must be 1 if using an RGBBus
    else:
        factor = 1

    double_buf = False  ### Must be False if using an RGBBus

    buffer_size = (
        disp.width * disp.height * (lv.color_format_get_size(color_format)) // factor
    )
    if color_format == lv.COLOR_FORMAT.I1:
        buffer_size //= 8
        # see https://docs.lvgl.io/master/details/main-modules/display/color_format.html#monochrome-displays
        buffer_size += 8

    fbuf1 = alloc_buffer(buffer_size)
    fbuf2 = alloc_buffer(buffer_size) if double_buf else None
    return TestDisplayDriver(
        disp, fbuf1, fbuf2, color_format, mode, pointer, render_mode
    )
