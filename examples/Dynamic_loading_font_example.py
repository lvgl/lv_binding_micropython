#
# Command line for running this example on the unix port from examples directory:
# MICROPYPATH=./:../lib ../../../ports/unix/micropython -i Dynamic_loading_font_example.py
#

import lvgl as lv
import fs_driver

lv.init()

# display driver init...

import display_driver # Default implementation. Replace by your driver

# FS driver init.
fs_drv = lv.fs_drv_t()
fs_driver.fs_register(fs_drv, 'S')

'''
　load the font file from filesystem(For me is flash )
　How to convert font files refer here: https://github.com/lvgl/lv_font_conv
　font-PHT-en-20.bin:
　　　lv_font_conv --size 20 --format bin --bpp 1 --font Alibaba-PuHuiTi-Medium.subset.ttf --range 0x20-0x7f --no-compress -o font-PHT-en-20.bin
　font-PHT-cn-20.bin:
　　　lv_font_conv --size 20 --format bin --bpp 1 --font Alibaba-PuHuiTi-Medium.subset.ttf --range 0x4e00-0x4e56　--no-compress　-o font-PHT-cn-20.bin
　font-PHT-jp-20.bin:
　　　lv_font_conv --size 20 --format bin --bpp 1 --font Alibaba-PuHuiTi-Medium.subset.ttf --range 0x3042-0x3093　--no-compress　-o font-PHT-jp-20.bin
'''
scr = lv.scr_act()
scr.clean()


myfont_cn = lv.font_load("S:font/font-PHT-cn-20.bin")
style1 = lv.style_t()
style1.init()

label1 = lv.label(scr)
style1.set_text_font(lv.STATE.DEFAULT, myfont_cn)  # set font
label1.add_style(label1.PART.MAIN, style1)

label1.set_text("上中下乎")  
label1.align(None, lv.ALIGN.CENTER, 0, -25)


myfont_en = lv.font_load("S:font/font-PHT-en-20.bin")
style2 = lv.style_t()
style2.init()

label2 = lv.label(scr)
style2.set_text_font(lv.STATE.DEFAULT, myfont_en)  # set font
label2.add_style(label2.PART.MAIN, style2)

label2.set_text("Hello LVGL!")
label2.align(None, lv.ALIGN.CENTER, 0, 25)


myfont_jp = lv.font_load("S:font/font-PHT-jp-20.bin")
style3 = lv.style_t()
style3.init()

label3 = lv.label(scr)
style3.set_text_font(lv.STATE.DEFAULT, myfont_jp)  # set font
label3.add_style(label3.PART.MAIN, style3)

label3.set_text("こんにちはありがとう")
label3.align(None, lv.ALIGN.CENTER, 0, 0)





