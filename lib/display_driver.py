import lvgl as lv
lv.init()

class driver:
    def init_gui_SDL(self):

        import SDL
        SDL.init()

        # Register SDL display driver.

        disp_buf1 = lv.disp_buf_t()
        buf1_1 = bytearray(480*10)
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
        
    def init_gui_esp32(self):

        import lvesp32
        import ili9341 as ili

        # Initialize ILI9341 display

        from ili9341 import ili9341
        self.disp = ili9341()

        # Register raw resistive touch driver
        '''
        import rtch
        touch = rtch.touch(xp = 32, yp = 33, xm = 25, ym = 26, touch_rail = 27, touch_sense = 33)
        touch.init()
        indev_drv = lv.indev_drv_t()
        lv.indev_drv_init(indev_drv) 
        indev_drv.type = lv.INDEV_TYPE.POINTER;
        indev_drv.read_cb = touch.read;
        lv.indev_drv_register(indev_drv);
        '''

        from xpt2046 import xpt2046
        self.touch = xpt2046()
    
    def init_gui(self):
        
        # Identify platform and initialize it

        try:
            self.init_gui_esp32()
        except ImportError:
            pass
    
        try:
            self.init_gui_SDL()
        except ImportError:
            pass

drv = driver()
drv.init_gui()
