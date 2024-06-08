import sys
import os

sys.path.append("..")
sys.path.append(os.getcwd())

from testdisplay import get_display  # noqa

_int = sys.argv.pop() if sys.platform in ["darwin", "linux"] else ""
_mode = "test"
if _int in ("-id", "-d"):
    _mode = "interactive"


async def run_test(func, display=None):
    import lvgl as lv  # noqa

    lv.init()

    scr = lv.obj()
    scr.set_style_bg_color(lv.color_black(), 0)
    lv.screen_load(scr)

    resp = await func(scr, display)
    return scr, resp


def run(func, filename, w=240, h=320, mode=None, **kwargs):
    import asyncio

    # import micropython  # noqa

    # micropython.mem_info()

    async def _run(func, w, h, mode=None, **kwargs):
        display = get_display(
            w,
            h,
            mode=mode if mode is not None else _mode,
            pointer=kwargs.get("pointer", "sim"),
        )

        if display.mode == "test":
            display.set_test_name(f"{filename.replace('.py', '')}.{func.__name__}")
            await run_test(func, display)
            await asyncio.sleep_ms(100)
        elif display.mode == "interactive":
            await run_test(func, display)
            if _int == "-id":
                while True:
                    try:
                        await asyncio.sleep_ms(1000)
                    except KeyboardInterrupt:
                        sys.exit()
                    except Exception as e:
                        sys.print_exception(e)

    asyncio.run(_run(func, w, h, mode, **kwargs))


def devicereset():
    try:
        import display_mode
    except Exception:
        return
    if hasattr(display_mode, "RESET"):
        if not display_mode.RESET:
            return
    if sys.platform not in ["darwin", "linux"]:
        import machine

        sys.stdout.write(b"\x04\x04")  # end raw repl listen
        machine.reset()
