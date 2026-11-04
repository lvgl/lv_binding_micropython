"""
LVGL PNG Image Decoder Example

This example demonstrates:
- Loading PNG images from filesystem using image decoder
- Creating draggable image widgets
- Using symbols as image sources
- Event handling for drag operations

Requirements:
- PNG decoder enabled in LVGL configuration
- LV_CACHE_DEF_SIZE > 0 for smooth dragging performance
- png_decoder_test.png file in the same directory as this script

Usage:
- Click and drag either image to move them around the screen
- The first image is loaded from a PNG file
- The second image uses a built-in symbol
"""

##############################################################################
# Initialization
##############################################################################

import usys as sys
sys.path.append('') # See: https://github.com/micropython/micropython/issues/6419

import lvgl as lv

# Initialize LVGL
lv.init()

# Initialize display driver
try:
    import display_driver_utils
    driver = display_driver_utils.driver()
except ImportError:
    print("Warning: display_driver_utils not available, using default display")

scr = lv.screen_active()

# Determine script path for loading assets
try:
    script_path = __file__[:__file__.rfind('/')] if __file__.find('/') >= 0 else '.'
except NameError: 
    script_path = '.'
    print("Warning: __file__ not available, using current directory for assets")

# Load the PNG image from file

png_file_path = '%s/png_decoder_test.png' % script_path
try:
    with open(png_file_path, 'rb') as f:
        png_data = f.read()
    
    png_image_dsc = lv.image_dsc_t({
        'data_size': len(png_data),
        'data': png_data 
    })
    print(f"Successfully loaded PNG image from {png_file_path}")
except OSError as e:
    print(f"Error loading PNG file {png_file_path}: {e}")
    print("Using a placeholder instead")
    # Create a simple fallback
    png_image_dsc = None

# Create an image using the decoder

image1 = lv.image(scr)
if png_image_dsc:
    image1.set_src(png_image_dsc)
else:
    # Fallback to a symbol if PNG loading failed
    image1.set_src(lv.SYMBOL.IMAGE + " PNG")
image1.set_pos(100, 50)

# Create an image from a symbol

image2 = lv.image(scr)
image2.set_src(lv.SYMBOL.OK + " Accept")
image2.set_pos(100,200)

# Drag handler

def drag_event_handler(e):
    self = e.get_target_obj()
    indev = lv.indev_active()
    vect = lv.point_t()
    indev.get_vect(vect)
    x = self.get_x() + vect.x
    y = self.get_y() + vect.y
    self.set_pos(x, y)

# Register drag handler for images

for image in [image1, image2]:
    image.add_flag(image.FLAG.CLICKABLE)
    image.add_event_cb(drag_event_handler, lv.EVENT.PRESSING, None)


