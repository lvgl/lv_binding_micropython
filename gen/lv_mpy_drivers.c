/**
 * @file lv_mpy_drivers.c
 *
 * Implementation of the binding-friendly driver wrappers declared for
 * gen_mpy.py in lv_mpy_drivers.h. See that file for why this is needed.
 */

#include "lvgl.h"

#if LV_USE_WAYLAND

lv_display_t * lv_wayland_window_create_simple(uint32_t hor_res, uint32_t ver_res, char * title)
{
    return lv_wayland_window_create(hor_res, ver_res, title, NULL);
}

#endif
