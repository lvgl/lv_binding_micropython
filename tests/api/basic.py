import lvgl as lv
import sys
import asyncio
import os

sys.path.append("..")
sys.path.append(os.getcwd())
import testrunner

# This is a basic test to test buttons, labels,
# RGB colors, layout aligment and events.


async def buttons(scr, display=None):
    display.debug_display(True)

    def get_button(scr, text, align, color):
        _btn = lv.button(scr)
        _btn.set_size(lv.pct(25), lv.pct(10))
        _lab = lv.label(_btn)
        _lab.set_text(text)
        _lab.center()
        _btn.set_style_align(align, 0)
        _btn.set_style_bg_color(lv.color_make(*color), 0)
        return _btn, text

    buttons = [
        ("RED", lv.ALIGN.TOP_MID, (255, 0, 0)),
        ("GREEN", lv.ALIGN.BOTTOM_MID, (0, 255, 0)),
        ("BLUE", lv.ALIGN.CENTER, (0, 0, 255)),
    ]

    def button_cb(event, name):
        print(f"{name} PRESSED")

    _all_btns = [get_button(scr, *btn) for btn in buttons]

    for btn, name in _all_btns:
        btn.add_event_cb(
            lambda event, button_name=name: button_cb(event, button_name),
            lv.EVENT.CLICKED,
            None,
        )

    await asyncio.sleep_ms(500)  # await so the frame can be rendered
    await display.screenshot()
    print("EVENT TEST:")
    for _btn, name in _all_btns:
        _btn.send_event(lv.EVENT.CLICKED, None)
        await asyncio.sleep_ms(200)

    return _all_btns


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

testrunner.run(buttons, __file__, disp_config=display_config)
testrunner.devicereset()
