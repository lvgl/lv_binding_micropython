import os
import lvgl as lv

MODE = "interactive"
POINTER = "interactive"
# "sdl" (default) or "wayland" -- set via env var so CI can exercise the
# same tests against both desktop drivers without duplicating test files.
DRIVER = os.getenv("LV_MP_TEST_DRIVER", "sdl")
WIDTH = 240
HEIGHT = 320
COLOR_FORMAT = lv.COLOR_FORMAT.RGB888
