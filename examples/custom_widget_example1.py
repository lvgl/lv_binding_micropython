import lvgl as lv
import display_driver

lv.init()

##############################################################################

class CustomWidgetClass():

    def __init__(self):
        # Define LVGL widget class
        self.lv_cls = lv.obj_class_t()
        self.lv_cls.constructor_cb = self.constructor
        self.lv_cls.destructor_cb = self.destructor
        self.lv_cls.event_cb = self.event_cb
        self.lv_cls.width_def = int(lv.DPI.DEF)
        self.lv_cls.height_def = int(lv.DPI.DEF)
        self.lv_cls.group_def = lv.obj.CLASS_GROUP_DEF.TRUE
        self.lv_cls.base_class = lv.obj_class

    def create(self, parent):
        # Create LVGL object from class
        return self.lv_cls.create_from_class(parent)

    def constructor(self, lv_cls, obj):
        obj.add_flag(obj.FLAG.CLICKABLE);
        obj.add_flag(obj.FLAG.CHECKABLE);
        obj.add_flag(obj.FLAG.SCROLL_ON_FOCUS);

    def destructor(self, lv_cls, obj):
        pass

    def event_cb(self, lv_cls, e):

        # Call the ancestor's event handler
        res = lv_cls.event_base(e)
        if res != lv.RES.OK:
            return

        # Handle DRAW event
        code = e.get_code()
        obj = e.get_target()
        if code == lv.EVENT.DRAW_MAIN:
            clip_area = lv.area_t.cast(e.get_param())
            self.draw(obj, clip_area)

    def draw(self, obj, clip_area):
        # Draw the custom widget

        area = lv.area_t()
        obj.get_content_coords(area)

        draw_desc = lv.draw_rect_dsc_t()
        draw_desc.init()
        draw_desc.bg_opa = lv.OPA.COVER;
        draw_desc.bg_color = obj.get_style_bg_color(lv.PART.MAIN)
        
        points = [
            {'x':area.x1 + area.get_width()//2,
             'y':area.y2 if obj.get_state() & lv.STATE.CHECKED else area.y1},
            {'x':area.x2,
             'y':area.y1 + area.get_height()//2},
            {'x':area.x1,
             'y':area.y1 + area.get_height()//2},
        ]

        lv.draw_polygon(points, len(points), clip_area, draw_desc)

##############################################################################

# A Python class to wrap the LVGL custom class
class CustomWidget():
    cls = CustomWidgetClass()

    def __init__(self, parent):
        # Create the LVGL object from class
        self.lv_obj = type(self).cls.create(parent)

        # Associate the LVGL object with CustomWidget
        self.lv_obj.set_user_data(self)

    def __getattr__(self, attr):
        # Provide access to LVGL object functions
        return getattr(self.lv_obj, attr)

    def __repr__(self):
        return "Custom Widget"

##############################################################################

class CustomTheme(lv.theme_t):

    class Style(lv.style_t):
        def __init__(self):
            super().__init__()
            self.set_bg_color(lv.palette_main(lv.PALETTE.GREY));

    class PressedStyle(lv.style_t):
        def __init__(self):
            super().__init__()
            self.set_bg_color(lv.palette_main(lv.PALETTE.BLUE));

    # A theme to apply styles to the custom widget

    def __init__(self):
        super().__init__()
        self.custom_style = CustomTheme.Style()
        self.custom_pressed_style = CustomTheme.PressedStyle()

        # This theme is based on active theme (material)
        base_theme = lv.theme_get_from_obj(lv.scr_act())

        # This theme will be applied only after base theme is applied
        self.set_parent(base_theme)

        # Set the "apply" callback of this theme to our custom callback
        self.set_apply_cb(self.apply)

        # Activate this theme on default display
        lv.disp_get_default().set_theme(self)
    
    def apply(self, theme, obj):
        # Apply the theme to CustomWidget LVGL class
        if obj.get_class() == CustomWidget.cls.lv_cls:
            obj.add_style(self.custom_style, lv.PART.MAIN)
            obj.add_style(self.custom_pressed_style, lv.PART.MAIN | lv.STATE.PRESSED)


##############################################################################

# Create the theme for the custom widget
theme = CustomTheme()

# Add a button to the screen
scr = lv.scr_act()
scr.set_flex_flow(lv.FLEX_FLOW.COLUMN)
scr.set_flex_align(lv.FLEX_ALIGN.SPACE_EVENLY, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
btn = lv.btn(scr)
l1 = lv.label(btn)
l1.set_text("Hello!")

# Create the custom widget
customWidget = CustomWidget(scr)

# A child object must be added to the LVGL undelying object of the custom widget
l2 = lv.label(customWidget.lv_obj)

l2.align(lv.ALIGN.CENTER, 0, -10)
l2.set_text("Click me!")

# Add click events to both button and custom widget
def event_cb(e):
    print("%s Clicked!" % repr(e.get_target()))

btn.add_event_cb(event_cb, lv.EVENT.CLICKED, None)
customWidget.add_event_cb(event_cb, lv.EVENT.CLICKED, None)

