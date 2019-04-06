import lvgl as lv

# lvgl must be initialized before any lvgl function is called or object/struct is constructed!

lv.init()

# Create a style based on style_plain but with a symbol font

symbolstyle = lv.style_t(lv.style_plain)
symbolstyle.text.font = lv.font_symbol_40

# The following two lines do the same thing.
# They show how to initialize struct either directly or through a dict

symbolstyle.text.color = lv.color_hex(0xffffff)
symbolstyle.text.color = {"ch": {"red":0xff, "green":0xff, "blue":0xff}}

def get_member_name(obj, value):
    for member in dir(obj):
        if getattr(obj, member) == value:
            return member

class SymbolButton(lv.btn):
    def __init__(self, parent, symbol, text):
        super().__init__(parent)
        self.symbol = lv.label(self)
        self.symbol.set_text(symbol)
        self.symbol.set_style(symbolstyle)
        
        self.label = lv.label(self)
        self.label.set_text(text)
        
class Page_Buttons:
    def __init__(self, app, page):
        self.app = app
        self.page = page

        self.btn1 = SymbolButton(page, lv.SYMBOL.PLAY, "Play")
        self.btn1.set_size(140,100)
        self.btn1.align(None, lv.ALIGN.IN_TOP_LEFT, 20, 0)
        
        self.btn2 = SymbolButton(page, lv.SYMBOL.PAUSE, "Pause")
        self.btn2.set_size(140,100)
        self.btn2.align(self.btn1, lv.ALIGN.OUT_RIGHT_TOP, 10, 0)
    
        self.label = lv.label(page)
        self.label.align(self.btn1, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)

        # Currently only single callback per object is supported

        for btn, name in [(self.btn1, 'Play'), (self.btn2, 'Pause')]:
            btn.set_event_cb(lambda self, event, name=name: self.label.set_text('%s %s' % (name, get_member_name(lv.EVENT, event))))


class Page_Simple:
    def __init__(self, app, page):
        self.app = app
        self.page = page
        
        # slider 
        self.slider = lv.slider(page)
        self.slider.align(page, lv.ALIGN.IN_TOP_LEFT, 20, 0)
        self.slider_label = lv.label(page)
        self.slider_label.align(self.slider, lv.ALIGN.OUT_RIGHT_MID, 15, 0)
        self.slider.set_event_cb(self.on_slider_changed)
        self.on_slider_changed(None)
        
        # style selector
        self.styles = [('Plain', lv.style_plain), ('Plain color', lv.style_plain_color), ('Pretty', lv.style_pretty), ('Pretty color', lv.style_pretty_color)]
    
        self.style_selector = lv.ddlist(page)
        self.style_selector.align(self.slider, lv.ALIGN.IN_BOTTOM_LEFT, 0, 40)
        self.style_selector.set_options('\n'.join(x[0] for x in self.styles))
        self.style_selector.set_event_cb(self.on_style_selector_changed)
    
    def on_slider_changed(self, event):
        self.slider_label.set_text(str(self.slider.get_value()))

    def on_style_selector_changed(self, event):
        selected = self.style_selector.get_selected()
        self.app.screen_main.tabview.set_style(lv.tabview.STYLE.BG, self.styles[selected][1])   


class Screen_Main(lv.obj):
    def __init__(self, app, *args, **kwds):
        self.app = app
        super().__init__(*args, **kwds)
        
        self.tabview = lv.tabview(self)
        self.page_simple = Page_Simple(self.app, self.tabview.add_tab('Simple'))
        self.page_buttons = Page_Buttons(self.app, self.tabview.add_tab('Buttons'))


class AdvancedDemoApplication():
    def init_gui_SDL(self):

        import SDL
        SDL.init()

        # Register SDL display driver.

        disp_buf1 = lv.disp_buf_t()
        buf1_1 = bytes(480*10)
        lv.disp_buf_init(disp_buf1,buf1_1, None, len(buf1_1))
        disp_drv = lv.disp_drv_t()
        lv.disp_drv_init(disp_drv)
        disp_drv.buffer = disp_buf1
        disp_drv.flush_cb = SDL.monitor_flush
        lv.disp_drv_register(disp_drv)

        # Regsiter SDL mouse driver

        indev_drv = lv.indev_drv_t()
        lv.indev_drv_init(indev_drv) 
        indev_drv.type = lv.INDEV_TYPE.POINTER;
        indev_drv.read_cb = SDL.mouse_read;
        lv.indev_drv_register(indev_drv);
        
    def init_gui_esp32(self):

        import lvesp32
        import ILI9341 as ili

        # Initialize ILI9341 display

        disp = ili.display(miso=5, mosi=18, clk=19, cs=13, dc=12, rst=4, backlight=2)
        disp.init()

        # Register display driver 

        disp_drv = lv.disp_drv_t()
        lv.disp_drv_init(disp_drv)
        disp_drv.flush_cb = disp.flush
        lv.disp_drv_register(disp_drv)

        # Register raw resistive touch driver

        import rtch
        touch = rtch.touch(xp = 32, yp = 33, xm = 25, ym = 26, touch_rail = 27, touch_sense = 33)
        touch.init()
        indev_drv = lv.indev_drv_t()
        lv.indev_drv_init(indev_drv) 
        indev_drv.type = lv.INDEV_TYPE.POINTER;
        indev_drv.read_cb = touch.read;
        lv.indev_drv_register(indev_drv);

    
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

        # Create the main screen and load it.

        self.screen_main = Screen_Main(self)
        lv.scr_load(self.screen_main)

app = AdvancedDemoApplication()
app.init_gui()

import utime

if __name__ == '__main__':
    while True:
        pass

