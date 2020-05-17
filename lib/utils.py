
import lvgl as lv

def aligned_buf(buf, alignment):

    """Return an aligned buffer

    Given a buffer, return a memory view within that buffer, which starts
    at an aligned address in RAM.
    The returned memory view is possibly smaller.

    !! You must keep a reference to the original buffer to prevent the
       garbage collector from collecting the aligned view!

    Arguments:

    buf         -- An object that implements buffer protocol
    alignment   -- Integer value

    """

    p = lv.C_Pointer()
    p.ptr_val = buf
    mod = p.uint_val % alignment
    offset = alignment - mod if mod != 0 else 0
    if len(buf) <= offset: return None
    p.uint_val += offset
    return p.ptr_val.__dereference__(len(buf) - offset)

