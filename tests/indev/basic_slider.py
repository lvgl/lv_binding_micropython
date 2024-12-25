import lvgl as lv
import sys
import asyncio
import os

sys.path.append("..")
sys.path.append(os.getcwd())
import testrunner  # noqa

# This is a basic test to test buttons, labels,
# RGB colors, layout aligment and events.


class TestSlider(lv.slider):
    def __init__(self, parent):
        super().__init__(parent)
        self.event_completed = asyncio.Event()


async def demo(scr, display=None):
    def get_button(scr, text, align, color):
        scr.set_style_pad_all(10, 0)
        _btn = TestSlider(scr)
        _btn.set_width(lv.pct(75))
        _btn.set_height(lv.pct(10))
        _lab = lv.label(_btn)
        _lab.set_text(text)
        _lab.set_style_text_color(lv.color_white(), 0)
        _lab.center()
        _btn.set_style_align(align, 0)
        _btn.set_style_bg_color(lv.color_make(*color), lv.PART.INDICATOR)
        _btn.set_style_bg_color(lv.color_make(*color), lv.PART.MAIN)
        _btn.set_style_bg_color(lv.color_make(*color), lv.PART.KNOB)
        return _btn, text

    buttons = [
        ("RED", lv.ALIGN.TOP_MID, (255, 0, 0)),
        ("GREEN", lv.ALIGN.BOTTOM_MID, (0, 255, 0)),
        ("BLUE", lv.ALIGN.CENTER, (0, 0, 255)),
    ]

    def button_cb(event, name, slider):
        if slider.get_value() == 100:
            if not slider.event_completed.is_set():
                print(f"{name} VALUE: {slider.get_value()}")
                slider.event_completed.set()

    _all_btns = [get_button(scr, *btn) for btn in buttons]

    for btn, name in _all_btns:
        btn.add_event_cb(
            lambda event, button_name=name, slider=btn: button_cb(
                event, button_name, slider
            ),
            lv.EVENT.VALUE_CHANGED,
            None,
        )

    print("INDEV + SLIDER TEST:")
    display.debug_indev(press=False)
    display.debug_display(False)
    for _btn, name in _all_btns:
        await _btn.event_completed.wait()
    return _all_btns


__file__ = globals().get("__file__", "test")

try:
    import display_config

    display_config.MODE = "interactive"
    display_config.POINTER = "interactive"
except Exception:
    display_config = testrunner.display_config

testrunner.run(demo, __file__, disp_config=display_config)
testrunner.devicereset()
