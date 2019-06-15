
# init

import ustruct as struct

import lodepng as png
import lvgl as lv
lv.init()

import SDL
SDL.init()

# Register SDL display driver.

disp_buf1 = lv.disp_buf_t()
buf1_1 = bytes(480*10)
lv.disp_buf_init(disp_buf1,buf1_1, None, len(buf1_1)//4)
disp_drv = lv.disp_drv_t()
lv.disp_drv_init(disp_drv)
disp_drv.buffer = disp_buf1
disp_drv.flush_cb = SDL.monitor_flush
disp_drv.hor_res = 480
disp_drv.ver_res = 320
lv.disp_drv_register(disp_drv)

# Regsiter SDL mouse driver

indev_drv = lv.indev_drv_t()
lv.indev_drv_init(indev_drv) 
indev_drv.type = lv.INDEV_TYPE.POINTER
indev_drv.read_cb = SDL.mouse_read
lv.indev_drv_register(indev_drv)

# Read PNG file header
# Taken from https://github.com/shibukawa/imagesize_py/blob/ffef30c1a4715c5acf90e8945ceb77f4a2ed2d45/imagesize.py#L63-L85

with open('lib/lv_bindings/examples/png_decoder_test.png','rb') as f:
    png_header = f.read(24)
if png_header.startswith(b'\211PNG\r\n\032\n') and png_header[12:16] == b'IHDR':
    try:
        width, height = struct.unpack(">LL", png_header[16:24])
    except struct.error:
        raise ValueError("Invalid PNG file")
# Maybe this is for an older PNG version.
elif png_header.startswith(b'\211PNG\r\n\032\n'):
    # Check to see if we have the right content type
    try:
        width, height = struct.unpack(">LL", png_header[8:16])
    except struct.error:
        raise ValueError("Invalid PNG file")
else:
    raise ValueError("Not a PNG file")
print("Header: width=%d, height=%d" % (width, height))

# Read and parse PNG file

with open('lib/lv_bindings/examples/png_decoder_test.png','rb') as f:
  png_data = f.read()

png_decoded = png.C_Pointer()
png_width = png.C_Pointer()
png_height = png.C_Pointer()
error = png.decode32(png_decoded, png_width, png_height, png_data, len(png_data));
if error:
    raise RuntimeError(png.error_text(error))
print('width=%d, height=%d' % (png_width.int_val, png_height.int_val))
img_size = png_width.int_val * png_height.int_val * lv.color_t.SIZE
img_data = png_decoded.ptr_val

# Convert png RGBA-big-endian format to lvgl ARGB-little-endian
# Eventually - this means swapping red and blue.
# More info on https://forumtest.littlevgl.com/t/png-decoding-why-red-and-blue-are-swapped/72

img_view = img_data.__dereference__(img_size)
for i in range(0, img_size, lv.color_t.SIZE):
    ch = lv.color_t.cast(img_view[i:i]).ch
    ch.red, ch.blue = ch.blue, ch.red

# Create a screen with a draggable image

scr = lv.obj()
img = lv.img(scr)
img.align(scr, lv.ALIGN.CENTER, 0, 0)
img_dsc = lv.img_dsc_t({
    'header':{
        'always_zero': 0,
        'w':png_width.int_val,
        'h':png_height.int_val,
        'cf':lv.img.CF.TRUE_COLOR_ALPHA
    },
    'data_size': img_size,
    'data': img_data 
})

img.set_src(img_dsc)
img.set_drag(True)

# Load the screen and display image

lv.scr_load(scr)

