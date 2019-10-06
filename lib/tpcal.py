import lvgl as lv
lv.init()

lv.log_register_print_cb(lambda level,path,line,msg: print('LOG: %s(%d): %s' % (path, line, msg)))

'''
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
'''

# Initialize ILI9341 display

import lvesp32
from ili9341 import ili9341
disp = ili9341()

# Register raw resistive touch driver

import rtch
touch = rtch.touch(xp = 32, yp = 33, xm = 25, ym = 26, touch_rail = 27, touch_sense = 33, cal_x0=0, cal_x1 = 240, cal_y0=0, cal_y1 = 320)
touch.init()
indev_drv = lv.indev_drv_t()
lv.indev_drv_init(indev_drv) 
indev_drv.type = lv.INDEV_TYPE.POINTER;
indev_drv.read_cb = touch.read;
lv.indev_drv_register(indev_drv);


class Tpcal_point():
    def __init__(self, x, y, name):
        self.display_coordinates = lv.point_t({'x': x, 'y': y})
        self.touch_coordinate = None
        self.name = name

    def __repr__(self):
        return "%s: (%d, %d)" % (self.name, 
                self.touch_coordinate.x,
                self.touch_coordinate.y)

class Tpcal():
        
    # Create a screen with a button and a label

    CIRCLE_SIZE = const(20)
    CIRCLE_OFFSET = const(20)
    TP_MAX_VALUE = const(5000)
    TOUCH_NUMBER = const(3)

    LV_COORD_MAX = const((1 << (8 * 2 - 1)) - 1000)
    LV_RADIUS_CIRCLE = const(LV_COORD_MAX)

    def __init__(self, points, output, touch_count = 3):

        self.points = points
        self.output = output
        self.touch_count = touch_count

        self.avr = [lv.point_t() for i in range(0,self.touch_count)] # Storage point to calculate average

        self.hres = lv.disp_get_hor_res(lv.disp_t.cast(None))
        self.vres = lv.disp_get_ver_res(lv.disp_t.cast(None))

        self.cur_point = 0
        self.cur_touch = 0

        self.scr = lv.obj(None, None)
        self.scr.set_size(TP_MAX_VALUE, TP_MAX_VALUE)
        lv.scr_load(self.scr)

        # Create a big transparent button screen to receive clicks

        big_btn = lv.btn(lv.scr_act(), None)
        big_btn.set_size(TP_MAX_VALUE, TP_MAX_VALUE)
        big_btn.set_style(lv.btn.STYLE.REL, lv.style_transp)
        big_btn.set_style(lv.btn.STYLE.PR, lv.style_transp)
        big_btn.set_layout(lv.LAYOUT.OFF)
        big_btn.set_event_cb(lambda obj, event, self=self: self.calibrate() if event == lv.EVENT.CLICKED else None) 

        self.label_main = lv.label(lv.scr_act(), None)

        style_circ = lv.style_t()
        lv.style_copy(style_circ, lv.style_pretty_color)
        style_circ.body.radius = LV_RADIUS_CIRCLE

        self.circ_area = lv.obj(lv.scr_act(), None)
        self.circ_area.set_size(CIRCLE_SIZE, CIRCLE_SIZE)
        self.circ_area.set_style(style_circ)
        self.circ_area.set_click(False)

        self.show_circle()

    def show_circle(self):
        point = self.points[self.cur_point]
        buf = "Click the circle in\n" + \
              point.name + "\n" + \
              "%d left" % (self.touch_count - self.cur_touch)
        self.label_main.set_text(buf)
        self.label_main.set_align(lv.label.ALIGN.CENTER)

        self.label_main.set_pos((self.hres - self.label_main.get_width() ) // 2,
                           (self.vres - self.label_main.get_height()) // 2)

        if point.display_coordinates.x < 0: point.display_coordinates.x += self.hres
        if point.display_coordinates.y < 0: point.display_coordinates.y += self.vres
        self.circ_area.set_pos(point.display_coordinates.x, point.display_coordinates.y)


    def calibrate(self):
        point = self.points[self.cur_point]
        indev = lv.indev_get_act()
        lv.indev_get_point(indev, self.avr[self.cur_touch])

        self.cur_touch += 1

        if self.cur_touch == self.touch_count:
            x_sum = 0
            y_sum = 0
            for i in range(0, self.touch_count):
                x_sum += self.avr[i].x - self.CIRCLE_SIZE // 2
                y_sum += self.avr[i].y - self.CIRCLE_SIZE // 2
            x = x_sum // TOUCH_NUMBER
            y = y_sum // TOUCH_NUMBER
            point.touch_coordinate = lv.point_t({
                'x': x,
                'y': y})

            self.cur_point += 1
            self.cur_touch = 0

        if self.cur_point == len(self.points):
            self.output(self.points)
            self.cur_point = 0

        self.show_circle()


def tpcal_output(points):
    visual_width = points[1].display_coordinates.x - points[0].display_coordinates.x
    visual_height = points[1].display_coordinates.y - points[0].display_coordinates.y
    touch_width = points[1].touch_coordinate.x - points[0].touch_coordinate.x
    touch_height = points[1].touch_coordinate.y - points[0].touch_coordinate.y

    pixel_width = touch_width / visual_width
    pixel_height = touch_height / visual_height

    x0 = points[0].touch_coordinate.x - points[0].display_coordinates.x * pixel_width
    y0 = points[0].touch_coordinate.y - points[0].display_coordinates.y * pixel_height

    screen_width = lv.disp_get_hor_res(lv.disp_t.cast(None))
    screen_height = vres = lv.disp_get_ver_res(lv.disp_t.cast(None))

    x1 = points[1].touch_coordinate.x + (screen_width - points[1].display_coordinates.x) * pixel_width
    y1 = points[1].touch_coordinate.y + (screen_height - points[1].display_coordinates.y) * pixel_height

    print("Calibration result: x0=%d, y0=%d, x1=%d, y1=%d" % (round(x0), round(y0), round(x1), round(y1)))
    


tpcal = Tpcal([
        Tpcal_point(20,  20, "upper left-hand corner"),
        Tpcal_point(-40, -40, "lower right-hand corner"),
    ], tpcal_output)

# while True:
#    pass
