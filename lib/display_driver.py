from display_driver_utils import driver
drv = driver()
if not drv.type:
    print("Not running a supported lvgl enabled version of Micropython. Giving up...")
