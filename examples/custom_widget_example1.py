import lvgl as lv
import display_driver

lv.init()

##############################################################################

# Helper debug function to print member name

member_name_cache = {}

def get_member_name(obj, value):
    try:
        return member_name_cache[id(obj)][id(value)]
    except KeyError:
        pass

    for member in dir(obj):
        if getattr(obj, member) == value:
            try:
                member_name_cache[id(obj)][id(value)] = member
            except KeyError:
                member_name_cache[id(obj)] = {id(value): member}
            return member


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

    def create(self, parent, wrapper):
        # Create LVGL object from class and associate wrapper (user_data)
        return self.lv_cls.create_obj(parent, wrapper)

    def constructor(self, lv_cls, obj):
        # obj.valid = False
        obj.add_flag(obj.FLAG.CLICKABLE);
        obj.add_flag(obj.FLAG.CHECKABLE);
        obj.add_flag(obj.FLAG.SCROLL_ON_FOCUS);
        print("Contructor called!")

    def destructor(self, lv_cls, obj):
        pass

    def event_cb(self, lv_cls, e):

        # Call the ancestor's event handler
        res = lv_cls.event_base(e)
        if res != lv.RES.OK:
            return

        code = e.get_code()
        obj = e.get_target()

        # TODO remove this when user_data is set correctly.
        if obj.__class__ == lv.obj:
            print("!!! event_cb skipped!")
            return

        print("Event %s" % get_member_name(lv.EVENT, code))

        if code == lv.EVENT.DRAW_MAIN:
            # Handle DRAW event
            clip_area = lv.area_t.cast(e.get_param())
            self.draw(obj, clip_area)
        elif code in [
                lv.EVENT.STYLE_CHANGED,
                lv.EVENT.VALUE_CHANGED,
                lv.EVENT.PRESSING,
                lv.EVENT.RELEASED]:
            # Check if need to recalculate widget parameters
            obj.valid = False

    def calc(self, obj):
        # Calculate object parameters

        area = lv.area_t()
        obj.get_content_coords(area)

        obj.draw_desc = lv.draw_rect_dsc_t()
        obj.draw_desc.init()
        obj.draw_desc.bg_opa = lv.OPA.COVER;
        obj.draw_desc.bg_color = obj.get_style_bg_color(lv.PART.MAIN)
        
        obj.points = [
            {'x':area.x1 + area.get_width()//2,
             'y':area.y2 if obj.get_state() & lv.STATE.CHECKED else area.y1},
            {'x':area.x2,
             'y':area.y1 + area.get_height()//2},
            {'x':area.x1,
             'y':area.y1 + area.get_height()//2},
        ]

        obj.valid = True

    def draw(self, obj, clip_area):

        # If object invalidated, recalculate its parameters

        if not obj.valid:
            self.calc(obj)

        # Draw the custom widget

        lv.draw_polygon(obj.points, len(obj.points), clip_area, obj.draw_desc)

##############################################################################

# A Python class to wrap the LVGL custom class
class CustomWidget():
    cls = CustomWidgetClass()

    def __new__(cls, parent):
        # Return a new lv object instead of CustomWidget, 
        # but first bind the LVGL object with CustomWidgetWrapper
        wrapper = cls.CustomWidgetWrapper(parent)
        return wrapper.lv_obj

    class CustomWidgetWrapper():
        def __init__(self, parent):
            # Create the LVGL object from class
            # It also associates the LVGL object with CustomWidget wrapper
            self.valid = False
            self.lv_obj = CustomWidget.cls.create(parent, None) # self)
            self.lv_obj.set_user_data(self)

        def __getattr__(self, attr):
            # Provide access to LVGL object functions
            # At this point it's possible to override them
            print("__getattr__(%s, %s)" % (repr(self), repr(attr)))
            return getattr(self.lv_obj, attr)

        # def get_class(self):
        #     return self.lv_obj.get_class()

        def __repr__(self):
            return "Custom Widget"

##############################################################################

class CustomTheme(lv.theme_t):

    class Style(lv.style_t):
        def __init__(self):
            super().__init__()
            self.init()
            self.set_bg_color(lv.palette_main(lv.PALETTE.GREY));

            self.set_layout(lv.LAYOUT_FLEX.value);
            self.set_flex_main_place(lv.FLEX_ALIGN.CENTER);
            self.set_flex_cross_place(lv.FLEX_ALIGN.CENTER);
            self.set_flex_track_place(lv.FLEX_ALIGN.CENTER);

    class PressedStyle(lv.style_t):
        def __init__(self):
            super().__init__()
            self.init()
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

# Add a label to the custom widget
l2 = lv.label(customWidget)

l2.set_text("Click me!")

# Add click events to both button and custom widget
def event_cb(e):
    print("%s Clicked!" % repr(e.get_target()))

btn.add_event_cb(event_cb, lv.EVENT.CLICKED, None)
customWidget.add_event_cb(event_cb, lv.EVENT.CLICKED, None)

