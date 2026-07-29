/**
 * @file lv_mpy_drivers.h
 *
 * gen_mpy.py builds its binding AST from a single preprocessed input file
 * (see the LVGL_MPY rule in micropython.mk). lvgl_private.h alone only
 * pulls in _private.h counterparts for libinput/evdev, so desktop window
 * drivers (sdl/wayland/x11/...) never reach the parser and never get
 * Python bindings, regardless of LV_USE_SDL/LV_USE_WAYLAND/etc. This
 * wrapper adds the public driver headers to gen_mpy's input so any driver
 * enabled in lv_conf.h is bound the same way widgets are.
 */

#include "lvgl_private.h"

#if LV_USE_WAYLAND
/*
 * lv_wayland_window_create()'s close_cb parameter has no accompanying
 * user_data-carrying struct argument (its first parameter is a plain
 * uint32_t, not an lv_obj/lv_display, which is what gen_mpy's
 * callback-binding heuristic requires to know where to stash the
 * Python callable). gen_mpy silently emits invalid C
 * (`hor_res->user_data`) for it instead of erroring, so hide the
 * original declaration from the parser here and expose
 * lv_wayland_window_create_simple() instead (implemented in
 * lv_mpy_drivers.c), which has no callback parameter at all -- window
 * close is already observable via lv_wayland_window_is_open().
 */
#define lv_wayland_window_create(...) lv_wayland_window_create_native_unbound
#endif

#include "src/drivers/lv_drivers.h"

#if LV_USE_WAYLAND
#undef lv_wayland_window_create
lv_display_t * lv_wayland_window_create_simple(uint32_t hor_res, uint32_t ver_res, char * title);
#endif
