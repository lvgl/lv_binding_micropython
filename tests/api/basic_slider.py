import lvgl as lv
import sys
import asyncio
import os

sys.path.append("..")
sys.path.append(os.getcwd())
import testrunner  # noqa

# This is a basic test to test buttons, labels,
# RGB colors, layout aligment and events.


async def sliders(scr, display=None):
    display.debug_display(True)

    def get_slider(scr, text, align, color):
        scr.set_style_pad_all(10, 0)
        slider = lv.slider(scr)
        slider.set_width(lv.pct(75))
        slider.set_height(lv.pct(10))
        _lab = lv.label(slider)
        _lab.set_text(text)
        _lab.set_style_text_color(lv.color_white(), 0)
        _lab.center()
        slider.set_style_align(align, 0)
        slider.set_style_bg_color(lv.color_make(*color), lv.PART.INDICATOR)
        slider.set_style_bg_color(lv.color_make(*color), lv.PART.MAIN)
        slider.set_style_bg_color(lv.color_make(*color), lv.PART.KNOB)
        return slider, text

    sliders = [
        ("RED", lv.ALIGN.TOP_MID, (255, 0, 0)),
        ("GREEN", lv.ALIGN.BOTTOM_MID, (0, 255, 0)),
        ("BLUE", lv.ALIGN.CENTER, (0, 0, 255)),
    ]

    def slider_cb(event, name, slider):
        if slider.get_value() == 100:
            print(f"{name} VALUE: {slider.get_value()}")

    _all_objs = [get_slider(scr, *slider) for slider in sliders]

    for sld, name in _all_objs:
        sld.add_event_cb(
            lambda event, button_name=name, slider=sld: slider_cb(
                event, button_name, slider
            ),
            lv.EVENT.VALUE_CHANGED,
            None,
        )

    await asyncio.sleep_ms(500)  # await so the frame can be rendered
    await display.screenshot(name="start")

    # simulate touch events
    if display:
        print("INDEV + SLIDER TEST:")
        display.debug_indev(press=False)
        display.debug_display(False)
        for _btn, name in _all_objs:
            pos = _btn.get_x(), _btn.get_y()
            pos2 = _btn.get_x2(), _btn.get_y2()
            x1, y1 = pos
            x2, y2 = pos2
            y_mid = y2 - ((y2 - y1) // 2)
            await display.swipe(x1 + 5, y_mid, x2 + (y2 - y1), y_mid, ms=500)
            await asyncio.sleep_ms(100)

    await display.screenshot(name="end")
    return _all_objs


__file__ = globals().get("__file__", "test")

try:
    import display_config

    display_config.MODE = "sim"
    display_config.POINTER = "sim"
    display_config.COLOR_FORMAT = lv.COLOR_FORMAT.RGB888
    display_config.WIDTH = 240
    display_config.HEIGHT = 320
except Exception:
    display_config = testrunner.display_config

testrunner.run(sliders, __file__, disp_config=display_config)
testrunner.devicereset()
