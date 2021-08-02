##############################################################################
#
# Example of the PNG image decoder Usage.
# For dragging to work reasonable, make sure LV_IMG_CACHE_DEF_SIZE is not 0!
#
##############################################################################

import usys as sys
sys.path.append('') # See: https://github.com/micropython/micropython/issues/6419

import lvgl as lv
from imagetools import get_png_info, open_png
import display_driver_utils

# Init

lv.init()
driver = display_driver_utils.driver()
scr = lv.scr_act()
lv.img.cache_set_size(2)
try:
    script_path = __file__[:__file__.rfind('/')] if __file__.find('/') >= 0 else '.'
except NameError: 
    script_path = ''

# Register an image decoder

decoder = lv.img.decoder_create()
decoder.info_cb = get_png_info
decoder.open_cb = open_png

# Load the image

with open('%s/png_decoder_test.png' % script_path, 'rb') as f:
  png_data = f.read()

png_img_dsc = lv.img_dsc_t({
    'data_size': len(png_data),
    'data': png_data 
})

# Create an image using the decoder

img1 = lv.img(scr)
img1.set_src(png_img_dsc)
img1.set_pos(100,50)

# Create an image from a symbol

img2 = lv.img(scr)
img2.set_src(lv.SYMBOL.OK + " Accept")
img2.set_pos(100,200)

# Drag handler

def drag_event_handler(e):
    self = e.get_target()
    indev = lv.indev_get_act()
    vect = lv.point_t()
    indev.get_vect(vect)
    x = self.get_x() + vect.x
    y = self.get_y() + vect.y
    self.set_pos(x, y)

# Register drag handler for images

for img in [img1, img2]:
    img.add_flag(img.FLAG.CLICKABLE)
    img.add_event_cb(drag_event_handler, lv.EVENT.PRESSING, None)


