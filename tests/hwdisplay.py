import lvgl as lv
import pyb


class HwDisplayDriver:
    def __init__(self, width=240, height=320, color_format=lv.COLOR_FORMAT.RGB565):
        self.width = width
        self.height = height
        self.color_depth = lv.color_format_get_bpp(color_format)
        self.color_size = lv.color_format_get_size(color_format)
        self._debug = False
        self._press_event = False
        self._x = int(width / 2)
        self.__y = self.gen_y()

    @property
    def debug(self):
        return self._debug

    @debug.setter
    def debug(self, x):
        self._debug = x

    def gen_y(self):
        for i in range(0, self.height * 2, int(self.height / 6)):
            yield i

    def get_y(self):
        self._y = next(self.__y)

    def blit(self, x1, y1, w, h, buff):
        pyb.LED((y1 % 4) + 1).toggle()
        ...

    def read_cb(self, indev, data):
        if pyb.Switch().value() and not self._press_event:
            self._press_event = True
            self.get_y()
            if self._debug:
                print(f"[PRESSED]: ({self._x},{self._y})")
            data.point = lv.point_t({"x": self._x, "y": self._y})
            data.state = lv.INDEV_STATE.PRESSED
        elif not pyb.Switch().value() and self._press_event:
            self._press_event = False
            if self._debug:
                print(f"[RELEASED]: ({self._x},{self._y})")
            data.state = lv.INDEV_STATE.RELEASED


# display = HwDisplayDriver()
