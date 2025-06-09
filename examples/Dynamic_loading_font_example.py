"""
LVGL Dynamic Font Loading Example

This example demonstrates how to load binary fonts dynamically from filesystem:
- Loading different font files for different languages (Chinese, English, Japanese)
- Using filesystem driver to access font files
- Creating labels with custom fonts

Font Conversion:
To create binary font files, use lv_font_conv tool:

English font:
  lv_font_conv --size 20 --format bin --bpp 1 --font Alibaba-PuHuiTi-Medium.subset.ttf 
               --range 0x20-0x7f --no-compress -o font-PHT-en-20.bin

Chinese font:
  lv_font_conv --size 20 --format bin --bpp 1 --font Alibaba-PuHuiTi-Medium.subset.ttf 
               --range 0x4e00-0x4e56 --no-compress -o font-PHT-cn-20.bin

Japanese font:
  lv_font_conv --size 20 --format bin --bpp 1 --font Alibaba-PuHuiTi-Medium.subset.ttf 
               --range 0x3042-0x3093 --no-compress -o font-PHT-jp-20.bin

Command line for running on unix port:
  MICROPYPATH=./:../lib ../../../ports/unix/micropython -i Dynamic_loading_font_example.py
"""

import usys as sys
sys.path.append('') # See: https://github.com/micropython/micropython/issues/6419

import lvgl as lv

# Initialize LVGL
lv.init()

# Determine script path for font files
try:
    script_path = __file__[:__file__.rfind('/')] if __file__.find('/') >= 0 else '.'
except NameError:
    script_path = '.'
    print("Warning: __file__ not available, using current directory")

# Initialize display driver
try:
    import display_driver_utils
    driver = display_driver_utils.driver()
except ImportError:
    print("Warning: display_driver_utils not available, using default display")

# Initialize filesystem driver for font loading
try:
    import fs_driver
    fs_drv = lv.fs_drv_t()
    fs_driver.fs_register(fs_drv, 'S')
    print("Filesystem driver registered successfully")
except ImportError:
    print("Warning: fs_driver not available, fonts may not load correctly")

# Clear the screen and create labels with different fonts
scr = lv.screen_active()
scr.clean()

# Load and display Chinese font
try:
    myfont_cn = lv.binfont_create("S:%s/font/font-PHT-cn-20.bin" % script_path)
    label1 = lv.label(scr)
    label1.set_style_text_font(myfont_cn, 0)
    label1.set_text("上中下乎")  # Chinese text
    label1.align(lv.ALIGN.CENTER)
    label1.set_y(label1.get_y() - 25)
    print("Chinese font loaded successfully")
except Exception as e:
    print(f"Failed to load Chinese font: {e}")
    label1 = lv.label(scr)
    label1.set_text("Chinese font failed")
    label1.align(lv.ALIGN.CENTER)
    label1.set_y(label1.get_y() - 25)

# Load and display English font
try:
    myfont_en = lv.binfont_create("S:%s/font/font-PHT-en-20.bin" % script_path)
    label2 = lv.label(scr)
    label2.set_style_text_font(myfont_en, 0)
    label2.set_text("Hello LVGL!")
    label2.align(lv.ALIGN.CENTER)
    label2.set_y(label2.get_y() + 25)
    print("English font loaded successfully")
except Exception as e:
    print(f"Failed to load English font: {e}")
    label2 = lv.label(scr)
    label2.set_text("Hello LVGL!")  # Use default font
    label2.align(lv.ALIGN.CENTER)
    label2.set_y(label2.get_y() + 25)

# Load and display Japanese font
try:
    myfont_jp = lv.binfont_create("S:%s/font/font-PHT-jp-20.bin" % script_path)
    label3 = lv.label(scr)
    label3.set_style_text_font(myfont_jp, 0)
    label3.set_text("こんにちはありがとう")  # Japanese text
    label3.align(lv.ALIGN.CENTER)
    print("Japanese font loaded successfully")
except Exception as e:
    print(f"Failed to load Japanese font: {e}")
    label3 = lv.label(scr)
    label3.set_text("Japanese font failed")
    label3.align(lv.ALIGN.CENTER)





