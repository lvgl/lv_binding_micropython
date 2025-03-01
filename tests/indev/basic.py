import lvgl as lv
import sys
import asyncio
import os

sys.path.append("..")
sys.path.append(os.getcwd())
import testrunner

# This is a basic test to test buttons, labels,
# RGB colors, layout aligment and events.


class TestButton(lv.button):
    def __init__(self, parent):
        super().__init__(parent)
        self.event_press = asyncio.Event()


async def demo(scr, display=None):
    def get_button(scr, text, align, color):
        _btn = TestButton(scr)
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

    def button_cb(event, name, button):
        print(f"{name} PRESSED")
        button.event_press.set()

    _all_btns = [get_button(scr, *btn) for btn in buttons]

    for btn, name in _all_btns:
        btn.add_event_cb(
            lambda event, button_name=name, button=btn: button_cb(
                event, button_name, button
            ),
            lv.EVENT.CLICKED,
            None,
        )

    await asyncio.sleep_ms(500)  # await so the frame can be rendered
    print("PRESS EVENT TEST:")
    for _btn, name in _all_btns:
        await _btn.event_press.wait()
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
