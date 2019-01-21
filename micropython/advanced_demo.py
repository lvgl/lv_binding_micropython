import lvgl as lv

symbolstyle = lv.style_t(lv.style_plain)
symbolstyle.text.font = lv.font_symbol_40

# The following two lines do the same thing.
# They show how to initialize struct either directly or through a dict
symbolstyle.text.color = lv.COLOR_HEX(0xffffff)
symbolstyle.text.color = {"red":0xff, "green":0xff, "blue":0xff}

class SymbolButton(lv.btn):
    def __init__(self, parent, symbol, text):
        super().__init__(parent)
        self.symbol = lv.label(self)
        self.symbol.set_text(symbol)
        self.symbol.set_style(symbolstyle)
        self.symbol.align(self, lv.ALIGN.CENTER,0,0)
        
        self.label = lv.label(self)
        self.label.set_text(text)
        self.label.align(self, lv.ALIGN.CENTER,20,0)
        
class Page_Buttons:
    def __init__(self, app, page):
        self.app = app
        self.page = page
        self.btn1 = SymbolButton(page, lv.SYMBOL.PLAY, "Play")
        self.btn1.set_size(140,100)
        self.btn2 = SymbolButton(page, lv.SYMBOL.PAUSE, "Pause")
        self.btn2.set_size(140,100)
        self.btn2.align(self.btn1, lv.ALIGN.OUT_RIGHT_TOP, 10, 0)
    
        self.label = lv.label(page)
        self.label.align(self.btn1, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)

        for btn, name in [(self.btn1, 'Play'), (self.btn2, 'Pause')]:
            btn.set_action(lv.btn.ACTION.CLICK, lambda action,name=name: self.label.set_text('%s click' % name))
            # btn.set_action(lv.BTN.ACTION.PR, lambda name=name: self.label.set_text(name + ' press'))
            # btn.set_action(lv.BTN.ACTION.LONG_PR, lambda name=name: self.label.set_text(name + ' long press'))
            # btn.set_action(lv.BTN.ACTION.LONG_PR_REPEAT, lambda name=name: self.label.set_text(name + ' long press repeat'))


class Page_Simple:
    def __init__(self, app, page):
        self.app = app
        self.page = page
        
        # slider 
        self.slider = lv.slider(page)
        self.slider.align(page, lv.ALIGN.IN_TOP_LEFT, 20, 0)
        self.slider_label = lv.label(page)
        self.slider_label.align(self.slider, lv.ALIGN.OUT_RIGHT_MID, 15, 0)
        self.slider.set_action(self.on_slider_changed)
        self.on_slider_changed(0)
        
        # style selector
        self.styles = [('Plain', lv.style_plain), ('Plain color', lv.style_plain_color), ('Pretty', lv.style_pretty), ('Pretty color', lv.style_pretty_color)]
    
        self.style_selector = lv.ddlist(page)
        self.style_selector.align(self.slider, lv.ALIGN.IN_BOTTOM_LEFT, 0, 40)
        self.style_selector.set_options('\n'.join(x[0] for x in self.styles))
        self.style_selector.set_action(self.on_style_selector_changed)
    
    def on_slider_changed(self, action):
        self.slider_label.set_text(str(self.slider.get_value()))

    def on_style_selector_changed(self, action):
        selected = self.style_selector.get_selected()
        self.app.screen_main.tabview.set_style(lv.tabview.STYLE.BG, self.styles[selected][1])   





class Screen_Main():
    def __init__(self, app, *args, **kwds):
        self.app = app
        super().__init__(*args, **kwds)
        
        self.tabview = lv.tabview(lv.scr_act())
        self.page_simple = Page_Simple(self.app, self.tabview.add_tab('Simple'))
        self.page_buttons = Page_Buttons(self.app, self.tabview.add_tab('Buttons'))


class AdvancedDemoApplication():
    def init_gui(self):
        self.screen_main = Screen_Main(self)
        # lv.scr_load(self.screen_main)


app = AdvancedDemoApplication()
app.init_gui()




