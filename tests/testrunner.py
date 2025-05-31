import sys
import os

sys.path.append("..")
sys.path.append(os.getcwd())

from testdisplay import get_display, display_config  # noqa

_int = sys.argv.pop() if sys.platform in ["darwin", "linux"] else ""
_mode = "sim"
if _int in ("-id", "-d"):
    _mode = "interactive"


async def run_test(func, display=None, **kwargs):
    import lvgl as lv  # noqa

    lv.init()

    scr = lv.obj()
    scr.set_style_bg_color(lv.color_black(), 0)
    lv.screen_load(scr)

    resp = await func(scr, display, **kwargs)
    return scr, resp


def run(func, filename, disp_config=display_config, **kwargs):
    import asyncio

    # import micropython  # noqa

    # micropython.mem_info()

    async def _run(func, disp_config=disp_config, **kwargs):
        if hasattr(disp_config, "COLOR_FORMAT"):
            display_config.COLOR_FORMAT = disp_config.COLOR_FORMAT
        display = get_display(
            disp_config.WIDTH,
            disp_config.HEIGHT,
            mode=disp_config.MODE if disp_config.MODE is not None else _mode,
            pointer=disp_config.POINTER,
            color_format=display_config.COLOR_FORMAT,
        )

        if display.mode == "sim":
            display.set_test_name(f"{filename.replace('.py', '')}.{func.__name__}")
            await run_test(func, display)
            await asyncio.sleep_ms(100)
        elif display.mode == "interactive":
            await run_test(func, display, **kwargs)
            if _int == "-id":
                while True:
                    try:
                        await asyncio.sleep_ms(1000)
                    except KeyboardInterrupt:
                        sys.exit()
                    except Exception as e:
                        sys.print_exception(e)

    asyncio.run(_run(func, disp_config, **kwargs))


def devicereset():
    import lvgl as lv

    if lv.is_initialized():
        lv.deinit()
