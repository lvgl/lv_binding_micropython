/**
 * @file sdl_common.h
 *
 */

#ifndef SDL_COMMON_H
#define SDL_COMMON_H

#ifdef __cplusplus
extern "C" {
#endif

/*********************
 *      INCLUDES
 *********************/

#ifdef LV_LVGL_H_INCLUDE_SIMPLE
#include "lvgl.h"
#else
#include "lvgl/lvgl.h"
#endif

#ifndef SDL_INCLUDE_PATH
#define SDL_INCLUDE_PATH <SDL2/SDL.h>
#endif

#include SDL_INCLUDE_PATH

/*********************
 *      DEFINES
 *********************/

#define SDL_HOR_RES     monitor_w
#define SDL_VER_RES     monitor_h
#define SDL_ZOOM        sdl_zoom
#define SDL_FULLSCREEN  sdl_fullscreen


/**********************
 *      TYPEDEFS
 **********************/

/**********************
 * GLOBAL PROTOTYPES
 **********************/

extern float sdl_zoom;
extern bool sdl_fullscreen;

extern volatile bool sdl_quit_qry;

/**
 * Initialize SDL to be used as display, mouse and mouse wheel drivers.
 */
void sdl_init(int w, int h, float zoom, bool fullscreen);

/**
 * Deinit the monitor and close SDL
 */
void sdl_deinit(void);

/**
 * Flush a buffer to the marked area
 * @param drv pointer to driver where this function belongs
 * @param area an area where to copy `color_p`
 * @param color_p an array of pixel to copy to the `area` part of the screen
 */
void sdl_display_flush(lv_disp_drv_t * disp_drv, const lv_area_t * area, lv_color_t * color_p);

/**
 * Get the current position and state of the mouse
 * @param indev_drv pointer to the related input device driver
 * @param data store the mouse data here
 */
void sdl_mouse_read(lv_indev_drv_t * indev_drv, lv_indev_data_t * data);

/**
 * Get encoder (i.e. mouse wheel) ticks difference and pressed state
 * @param indev_drv pointer to the related input device driver
 * @param data store the read data here
 */
void sdl_mousewheel_read(lv_indev_drv_t * indev_drv, lv_indev_data_t * data);

/**
 * Get input from the keyboard.
 * @param indev_drv pointer to the related input device driver
 * @param data store the red data here
 */
void sdl_keyboard_read(lv_indev_drv_t * indev_drv, lv_indev_data_t * data);

int quit_filter(void * userdata, SDL_Event * event);

void mouse_handler(SDL_Event * event);
void mousewheel_handler(SDL_Event * event);
uint32_t keycode_to_ctrl_key(SDL_Keycode sdl_key);
void keyboard_handler(SDL_Event * event);

/**********************
 *      MACROS
 **********************/

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* SDL_COMMON_H */
