import lvgl as lv
import sys
import asyncio
import os

sys.path.append("..")
sys.path.append(os.getcwd())
import testrunner

# This is a basic test to test buttons, labels,
# RGB colors, layout aligment and events.


async def demo(scr, display=None):
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
    print("EVENT TEST:")
    for _btn, name in _all_btns:
        _btn.send_event(lv.EVENT.CLICKED, None)
        await asyncio.sleep_ms(200)

    # simulate touch events
    if display:
        print("INDEV TEST:")
        await display.touch(100, 100)

        await asyncio.sleep_ms(500)

        print("INDEV + BUTTONS TEST:")
        # display.debug_indev(press=False, release=False)
        display.debug_display(False)
        for _btn, name in _all_btns:
            pos = _btn.get_x(), _btn.get_y()
            await display.touch(*pos)
            await asyncio.sleep_ms(1000)

        await asyncio.sleep_ms(500)

    return _all_btns


__file__ = globals().get("__file__", "test")

try:
    import display_config

    display_config.MODE = "sim"
    display_config.POINTER = "sim"
except Exception:
    display_config = testrunner.display_config

testrunner.run(demo, __file__, disp_config=display_config)
testrunner.devicereset()
