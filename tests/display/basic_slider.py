import lvgl as lv
import sys
import asyncio
import os

sys.path.append("..")
sys.path.append(os.getcwd())
import testrunner  # noqa

# This is a basic test to test buttons, labels,
# RGB colors, layout aligment and events.


async def demo(scr, display=None):
    def get_button(scr, text, align, color):
        scr.set_style_pad_all(10, 0)
        _btn = lv.slider(scr)
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
            print(f"{name} VALUE: {slider.get_value()}")

    _all_btns = [get_button(scr, *btn) for btn in buttons]

    for btn, name in _all_btns:
        btn.add_event_cb(
            lambda event, button_name=name, slider=btn: button_cb(
                event, button_name, slider
            ),
            lv.EVENT.VALUE_CHANGED,
            None,
        )

    await asyncio.sleep_ms(500)  # await so the frame can be rendered
    # simulate touch events
    if display:
        print("INDEV + SLIDER TEST:")
        display.debug_indev(press=False)
        display.debug_display(False)
        for _btn, name in _all_btns:
            pos = _btn.get_x(), _btn.get_y()
            pos2 = _btn.get_x2(), _btn.get_y2()
            x1, y1 = pos
            x2, y2 = pos2
            y_mid = y2 - ((y2 - y1) // 2)
            await display.swipe(x1 + 5, y_mid, x2 + (y2 - y1), y_mid, ms=500)
            await asyncio.sleep_ms(100)

    return _all_btns


__file__ = globals().get("__file__", "test")

try:
    import display_config

    display_config.MODE = "interactive"
    display_config.POINTER = "sim"
except Exception:
    display_config = testrunner.display_config

testrunner.run(demo, __file__, disp_config=display_config)
testrunner.devicereset()
