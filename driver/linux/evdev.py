# LVGL indev driver for evdev mouse device
# (for the unix micropython port)

import ustruct
import select
import lvgl as lv

EV_REL = 0x02
EV_ABS = 0x03
EV_KEY = 0x01
REL_X = 0x00
REL_Y = 0x01
ABS_X = 0x00
ABS_Y = 0x01
ABS_MT_POSITION_X = 0x35
ABS_MT_POSITION_Y = 0x36
ABS_MT_TRACKING_ID = 0x39
BTN_MOUSE = 0x110
BTN_TOUCH = 0x14a

# Default crosshair cursor
class crosshair_cursor:
    def __init__(self, scr=None):
        self.scr = scr if scr else lv.scr_act()
        self.hor_res = self.scr.get_width()
        self.ver_res = self.scr.get_height()
        self.cursor_style = lv.style_t()
        self.cursor_style.set_line_width(1)
        self.cursor_style.set_line_dash_gap(5)
        self.cursor_style.set_line_dash_width(1)
        self.cursor_hor = lv.line(self.scr)
        self.cursor_hor.add_style(self.cursor_style, lv.PART.MAIN)
        self.cursor_ver = lv.line(self.scr)
        self.cursor_ver.add_style(self.cursor_style, lv.PART.MAIN)

    def __call__(self, data):
        # print("%d : %d:%d" % (data.state, data.point.x, data.point.y))
        self.cursor_hor.set_points([{'x':0,'y':data.point.y},{'x':self.hor_res,'y':data.point.y}],2)
        self.cursor_ver.set_points([{'y':0,'x':data.point.x},{'y':self.ver_res,'x':data.point.x}],2)

    def delete(self):
        self.cursor_hor.delete()
        self.cursor_ver.delete()

# evdev driver for mouse
class mouse_indev:
    def __init__(self, scr=None, cursor=None, device='/dev/input/mice'):

        # Open evdev and initialize members
        self.evdev = open(device, 'rb')
        self.poll = select.poll()
        self.poll.register(self.evdev.fileno())
        self.scr = scr if scr else lv.scr_act()
        self.cursor = cursor if cursor else crosshair_cursor(self.scr)
        self.hor_res = self.scr.get_width()
        self.ver_res = self.scr.get_height()

        # Register LVGL indev driver
        self.indev = lv.indev_create()
        self.indev.set_type(lv.INDEV_TYPE.POINTER)
        self.indev.set_read_cb(self.mouse_read)

    def mouse_read(self, indev, data) -> int:
        
        # Check if there is input to be read from evdev
        if not self.poll.poll()[0][1] & select.POLLIN:
            return 0

        # Read and parse evdev mouse data
        mouse_data = ustruct.unpack('bbb',self.evdev.read(3))

        # Data is relative, update coordinates
        data.point.x += mouse_data[1]
        data.point.y -= mouse_data[2]

        # Handle coordinate overflow cases
        data.point.x = min(data.point.x, self.hor_res - 1)
        data.point.y = min(data.point.y, self.ver_res - 1)
        data.point.x = max(data.point.x, 0)
        data.point.y = max(data.point.y, 0)

        # Update "pressed" status
        data.state = lv.INDEV_STATE.PRESSED if ((mouse_data[0] & 1) == 1) else lv.INDEV_STATE.RELEASED

        # Draw cursor, if needed
        if self.cursor: self.cursor(data)
        return 0

    def delete(self):
        self.evdev.close()
        if self.cursor and hasattr(self.cursor, 'delete'):
            self.cursor.delete()
        self.indev.enable(False)

# evdev driver for touchscreen
class touch_indev:
    def __init__(self, scr=None, device='/dev/input/event1', evdev_swap_axes=False):

        # Open evdev and initialize members
        self.evdev = open(device, 'rb')
        self.poll = select.poll()
        self.poll.register(self.evdev.fileno())
        self.scr = scr if scr else lv.scr_act()
        self.hor_res = self.scr.get_width()
        self.ver_res = self.scr.get_height()
        self.evdev_button = lv.INDEV_STATE.RELEASED
        self.evdev_swap_axes = evdev_swap_axes
        self.evdev_calibrate = False
        self.last_evdev_root_x = 0
        self.last_evdev_root_y = 0 

    def read(self, indev_drv, data) -> int:
        
        # Check if there is input to be read from evdev
        if not self.poll.poll()[0][1] & select.POLLIN:
            return 0

        FORMAT = 'llHHI'
        EVENT_SIZE = ustruct.calcsize(FORMAT)
        
        evdev_root_x = self.last_evdev_root_x
        evdev_root_y = self.last_evdev_root_y

        raw_data = self.evdev.read(EVENT_SIZE)

        while(self.poll.poll()[0][1] & select.POLLIN):

            # Read and parse evdev data
            raw_data = self.evdev.read(EVENT_SIZE)
            (_, _, event_type, code, value) = ustruct.unpack(FORMAT, raw_data)
           
            if event_type == EV_ABS:
                if (code == ABS_X) or (code == ABS_MT_POSITION_X):
                    if self.evdev_swap_axes:
                        evdev_root_y = value
                    else:
                        evdev_root_x = value
                elif (code == ABS_Y) or (code == ABS_MT_POSITION_Y):
                    if self.evdev_swap_axes:
                        evdev_root_x = value
                    else:
                        evdev_root_y = value
                elif code == ABS_MT_TRACKING_ID:
                    if value == -1:
                        self.evdev_button = lv.INDEV_STATE.RELEASED
                    else:
                        self.evdev_button = lv.INDEV_STATE.PRESSED
            elif (event_type == EV_KEY) and (code == BTN_TOUCH):
                if value == 0:
                    self.evdev_button = lv.INDEV_STATE.RELEASED
                elif value == 1:
                    self.evdev_button = lv.INDEV_STATE.PRESSED

        self.last_evdev_root_x = evdev_root_x
        self.last_evdev_root_y = evdev_root_y
            
        # Scaling
        if self.evdev_calibrate:
            evdev_root_x = self._map_horizontal(evdev_root_x)
            evdev_root_y = self._map_vertical(evdev_root_y)

        # Handle coordinate overflow cases
        data.point.x = min(evdev_root_x, self.hor_res - 1)
        data.point.y = min(evdev_root_y, self.ver_res - 1)
        data.point.x = max(evdev_root_x, 0)
        data.point.y = max(evdev_root_y, 0)

        # Update "pressed" status
        data.state = self.evdev_button

        return 0

    # Scaling: if range of evdev readouts is different than screen resolution
    # Example for Waveshare 7inch HDMI LCD (C) Rev4.1
    # touch.calibrate(0, 4096, 0, 4096)
    def calibrate(self, evdev_min_hor, evdev_max_hor, evdev_min_ver, evdev_max_ver):
        self.evdev_calibrate = True
        self.evdev_min_hor = evdev_min_hor
        self.evdev_max_hor = evdev_max_hor
        self.evdev_min_ver = evdev_min_ver
        self.evdev_max_ver = evdev_max_ver

    def _map_vertical(self, val):
        return int((val - self.evdev_min_ver) * (self.ver_res) / (self.evdev_max_ver - self.evdev_min_ver))

    def _map_horizontal(self, val):
        return int((val - self.evdev_min_hor) * (self.hor_res) / (self.evdev_max_hor - self.evdev_min_hor))

    def delete(self):
        self.evdev.close()
