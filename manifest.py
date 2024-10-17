import sys

include("$(MPY_DIR)/extmod/asyncio")

freeze("lib", (
    "display_driver.py",
    "display_driver_utils.py",
    "fs_driver.py",
    "lv_colors.py",
    "lv_utils.py",
    "tpcal.py",
    "utils.py",
), opt=0)

require("aiorepl")

if sys.platform in ("linux"):
    freeze("driver/linux", (
        "evdev.py",
        "lv_timer.py",
    ), opt=1)

