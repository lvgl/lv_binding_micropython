import lvgl as lv
import lodepng as png
import struct
import micropython

class lodepng_error(RuntimeError):
    def __init__(self, err):
        super().__init__(png.error_text(err))

# Parse PNG file header
# Taken from https://github.com/shibukawa/imagesize_py/blob/ffef30c1a4715c5acf90e8945ceb77f4a2ed2d45/imagesize.py#L63-L85
def get_png_info(decoder, src, header):
    # Only handle variable image types

    if lv.img.src_get_type(src) != lv.img.SRC.VARIABLE:
        return lv.RES.INV

    png_header = bytes(lv.img_dsc_t.cast(src).data.__dereference__(24))

    if png_header.startswith(b'\211PNG\r\n\032\n'):
        if png_header[12:16] == b'IHDR':
            start = 16
        # Maybe this is for an older PNG version.
        else:
            start = 8
        try:
            width, height = struct.unpack(">LL", png_header[start:start+8])
        except struct.error:
            return lv.RES.INV
    else:
        return lv.RES.INV

    header.always_zero = 0
    header.w = width
    header.h = height
    header.cf = lv.img.CF.TRUE_COLOR_ALPHA

    return lv.RES.OK

@micropython.viper
def convert_rgba_to_argb(img_view, img_size):
    """Convert png RGBA-big-endian format to lvgl ARGB-little-endian"""
    # Eventually - this means swapping red and blue.
    # More info on https://forumtest.littlevgl.com/t/png-decoding-why-red-and-blue-are-swapped/72
    for i in range(0, img_size, lv.color_t.SIZE):
        ch = lv.color_t.cast(img_view[i:i]).ch
        ch.red, ch.blue = ch.blue, ch.red

# Read and parse PNG file
def open_png(decoder, dsc):
    img_dsc = lv.img_dsc_t.cast(dsc.src)
    png_data = img_dsc.data
    png_size = img_dsc.data_size
    png_decoded = png.C_Pointer()
    png_width = png.C_Pointer()
    png_height = png.C_Pointer()
    error = png.decode32(png_decoded, png_width, png_height, png_data, png_size);
    if error:
        raise lodepng_error(error)
    img_size = png_width.int_val * png_height.int_val * lv.color_t.SIZE
    img_data = png_decoded.ptr_val

    img_view = img_data.__dereference__(img_size)
    convert_rgba_to_argb(img_view, img_size)

    dsc.img_data = img_data
    return lv.RES.OK
