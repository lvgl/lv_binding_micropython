/**
 * @file keyboard.h
 *
 */

#ifndef KEYBOARD_H
#define KEYBOARD_H

#ifdef __cplusplus
extern "C" {
#endif

/*********************
 *      INCLUDES
 *********************/
#ifdef LV_CONF_INCLUDE_SIMPLE
#include "lv_drv_conf.h"
#else
#include "lv_drv_conf.h"
#endif

#if USE_KEYBOARD
#include <stdint.h>
#include <stdbool.h>
#include <SDL2/SDL.h>
#include "lvgl/src/hal/lv_hal_indev.h"


#ifndef MONITOR_SDL_INCLUDE_PATH
#define MONITOR_SDL_INCLUDE_PATH <SDL2/SDL.h>
#endif

#include MONITOR_SDL_INCLUDE_PATH

/*********************
 *      DEFINES
 *********************/

/**********************
 *      TYPEDEFS
 **********************/

/**********************
 * GLOBAL PROTOTYPES
 **********************/

/**
 * Initialize the keyboard
 */
void keyboard_init(void);
/**
 * Get the current position and state of the keyboard
 * @param data store the keyboard data here
 * @return false: because the points are not buffered, so no more data to be read
 */
void keyboard_read(struct _lv_indev_drv_t * indev_drv, lv_indev_data_t * data);

/**
 * It will be called from the main SDL thread
 */
void keyboard_handler(SDL_Event *event);

/**********************
 *      MACROS
 **********************/

#endif /* USE_KEYBOARD */

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* KEYBOARD_H */
