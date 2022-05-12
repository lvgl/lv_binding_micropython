/**
 * @file keyboard.c
 *
 */

/*********************
 *      INCLUDES
 *********************/
#include "SDL_keyboard.h"
#if USE_KEYBOARD != 0

/*********************
 *      DEFINES
 *********************/
#ifndef MONITOR_ZOOM
#define MONITOR_ZOOM    1
#endif

/**********************
 *      TYPEDEFS
 **********************/

/**********************
 *  STATIC PROTOTYPES
 **********************/

/**********************
 *  STATIC VARIABLES
 **********************/
static bool keyup = false;
static bool keydown = false;
static bool repeat = false;
static bool keyboard_was_read = true;
static int last_key = -1;


/**********************
 *      MACROS
 **********************/

/**********************
 *   GLOBAL FUNCTIONS
 **********************/

/**
 * Get the current key and state of the keyboard
 * @param data store the keyboard data here
 * @return false
 */
void keyboard_read(struct _lv_indev_drv_t * indev_drv, lv_indev_data_t * data)
{
    if(!keyboard_was_read)
    {
        /* Store the collected data */
        if(keyup)
        {
            data->state = LV_INDEV_STATE_PR;
            data->key = last_key;
        }
        else if(keydown)
        {
            data->state = LV_INDEV_STATE_REL;
            data->key = last_key;
        }
    }
    if(keydown && repeat){
        data->state = LV_INDEV_STATE_PR;
        data->key = last_key;
    }
    
    data->continue_reading = false;
    keyboard_was_read = true;
    return;
}

/**
 * It will be called from the main SDL thread
 */
void keyboard_handler(SDL_Event * event)
{
    keydown = false;
    keyup = false;
    last_key = -1;

    if(keyboard_was_read)
    {
        switch(event->type) {
            case SDL_KEYUP:
                    keyup = true;
                    repeat = event->key.repeat;
                    keyboard_was_read = false;
                break;
            case SDL_KEYDOWN:
                    keydown = true;
                    repeat = event->key.repeat;
                    keyboard_was_read = false;
                break;
        }

        if(keyup || keydown)
        {
            switch(event->key.keysym.sym)
            {
                case SDLK_TAB:
                    last_key = LV_KEY_NEXT;
                    break;
                case SDLK_END:
                    last_key = LV_KEY_PREV;
                    break;
                case SDLK_RETURN:
                    last_key = LV_KEY_ENTER;
                    break;
                case SDLK_LEFT:
                    last_key = LV_KEY_LEFT;
                    break;
                case SDLK_RIGHT:
                    last_key = LV_KEY_RIGHT;
                    break;
                case SDLK_UP:
                    last_key = LV_KEY_UP;
                    break;
                case SDLK_DOWN:
                    last_key = LV_KEY_DOWN;
                    break;
                case SDLK_ESCAPE:
                    last_key = LV_KEY_ESC;
                    break;
                case SDLK_DELETE:
                    last_key = LV_KEY_DEL;
                    break;
                case SDLK_BACKSPACE:
                    last_key = LV_KEY_BACKSPACE;
                    break;
                case SDLK_HOME:
                    last_key = LV_KEY_HOME;
                    break;
                default:
                    last_key = event->key.keysym.sym;
                    break;
            }
        }
    }
    return;
}

/**********************
 *   STATIC FUNCTIONS
 **********************/

#endif
