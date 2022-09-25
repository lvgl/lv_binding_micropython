//
// Created by Mariotaku on 2021/10/14.
//

#include "sdl_common.h"

/*********************
 *      DEFINES
 *********************/

#ifndef KEYBOARD_BUFFER_SIZE
#define KEYBOARD_BUFFER_SIZE SDL_TEXTINPUTEVENT_TEXT_SIZE
#endif

/**********************
 *  STATIC PROTOTYPES
 **********************/


/**********************
 *  STATIC VARIABLES
 **********************/

volatile bool sdl_quit_qry = false;

static bool left_button_down = false;
static int16_t last_x = 0;
static int16_t last_y = 0;

static int16_t wheel_diff = 0;
static lv_indev_state_t wheel_state = LV_INDEV_STATE_RELEASED;

struct key_event
{
    char key;
    bool state;
};
static struct key_event key_buffer[KEYBOARD_BUFFER_SIZE];
static int16_t key_buffer_len = 0;

/**********************
 *   GLOBAL FUNCTIONS
 **********************/
/**
 * Get the current position and state of the mouse
 * @param indev_drv pointer to the related input device driver
 * @param data store the mouse data here
 */
void sdl_mouse_read(lv_indev_drv_t * indev_drv, lv_indev_data_t * data)
{
    (void) indev_drv;      /*Unused*/

    /*Store the collected data*/
    data->point.x = last_x;
    data->point.y = last_y;
    data->state = left_button_down ? LV_INDEV_STATE_PRESSED : LV_INDEV_STATE_RELEASED;
}


/**
 * Get encoder (i.e. mouse wheel) ticks difference and pressed state
 * @param indev_drv pointer to the related input device driver
 * @param data store the read data here
 */
void sdl_mousewheel_read(lv_indev_drv_t * indev_drv, lv_indev_data_t * data)
{
    (void) indev_drv;      /*Unused*/

    data->state = wheel_state;
    data->enc_diff = wheel_diff;
    wheel_diff = 0;
}

/**
 * Get input from the keyboard.
 * @param indev_drv pointer to the related input device driver
 * @param data store the red data here
 */
void sdl_keyboard_read(lv_indev_drv_t * indev_drv, lv_indev_data_t * data)
{
    (void) indev_drv;      /*Unused*/

    if(key_buffer_len > 0){
        data->state = key_buffer[0].state;
        data->key = key_buffer[0].key;
        key_buffer_len--;
        data->continue_reading = key_buffer_len > 0;
        memmove(&key_buffer[0], &key_buffer[1], sizeof(struct key_event) * key_buffer_len);
    }
}

/**********************
 *   STATIC FUNCTIONS
 **********************/

int quit_filter(void * userdata, SDL_Event * event)
{
    (void)userdata;

    if(event->type == SDL_QUIT) {
        sdl_quit_qry = true;
    }

    return 1;
}

void mouse_handler(SDL_Event * event)
{
    switch(event->type) {
        case SDL_MOUSEBUTTONUP:
            if(event->button.button == SDL_BUTTON_LEFT)
                left_button_down = false;
            break;
        case SDL_MOUSEBUTTONDOWN:
            if(event->button.button == SDL_BUTTON_LEFT) {
                left_button_down = true;
                last_x = (int16_t)(event->motion.x / SDL_ZOOM);
                last_y = (int16_t)(event->motion.y / SDL_ZOOM);
            }
            break;
        case SDL_MOUSEMOTION:
            last_x = (int16_t)(event->motion.x / SDL_ZOOM);
            last_y = (int16_t)(event->motion.y / SDL_ZOOM);
            break;

        case SDL_FINGERUP:
            left_button_down = false;
            last_x = (int16_t) (LV_HOR_RES * event->tfinger.x / SDL_ZOOM);
            last_y = (int16_t) (LV_VER_RES * event->tfinger.y / SDL_ZOOM);
            break;
        case SDL_FINGERDOWN:
            left_button_down = true;
            last_x = (int16_t) (LV_HOR_RES * event->tfinger.x / SDL_ZOOM);
            last_y = (int16_t) (LV_VER_RES * event->tfinger.y / SDL_ZOOM);
            break;
        case SDL_FINGERMOTION:
            last_x = (int16_t) (LV_HOR_RES * event->tfinger.x / SDL_ZOOM);
            last_y = (int16_t) (LV_VER_RES * event->tfinger.y / SDL_ZOOM);
            break;
    }

}


/**
 * It is called periodically from the SDL thread to check mouse wheel state
 * @param event describes the event
 */
void mousewheel_handler(SDL_Event * event)
{
    switch(event->type) {
        case SDL_MOUSEWHEEL:
            // Scroll down (y = -1) means positive encoder turn,
            // so invert it
#ifdef __EMSCRIPTEN__
            /*Escripten scales it wrong*/
            if(event->wheel.y < 0) wheel_diff++;
            if(event->wheel.y > 0) wheel_diff--;
#else
            wheel_diff = -event->wheel.y;
#endif
            break;
        case SDL_MOUSEBUTTONDOWN:
            if(event->button.button == SDL_BUTTON_MIDDLE) {
                wheel_state = LV_INDEV_STATE_PRESSED;
            }
            break;
        case SDL_MOUSEBUTTONUP:
            if(event->button.button == SDL_BUTTON_MIDDLE) {
                wheel_state = LV_INDEV_STATE_RELEASED;
            }
            break;
        default:
            break;
    }
}


/**
 * Called periodically from the SDL thread, store text input or control characters in the buffer.
 * @param event describes the event
 */
void keyboard_handler(SDL_Event * event)
{
    bool key_state = (event->type == SDL_KEYUP) ? LV_INDEV_STATE_RELEASED : LV_INDEV_STATE_PRESSED;
    /* We only care about SDL_KEYDOWN and SDL_TEXTINPUT events */
    switch(event->type) {
        case SDL_KEYDOWN:                       /*Button press*/
        case SDL_KEYUP:                       /*Button release*/
        {
            const uint32_t ctrl_key = keycode_to_ctrl_key(event->key.keysym.sym);
            
            if(key_buffer_len < KEYBOARD_BUFFER_SIZE){
                key_buffer[key_buffer_len].key = ctrl_key;
                key_buffer[key_buffer_len].state = key_state;
                key_buffer_len++;
            }
            break;
        }
        case SDL_TEXTINPUT:                     /*Text input*/
        {
            const size_t len = key_buffer_len + strlen(event->text.text);
            if (len < KEYBOARD_BUFFER_SIZE - 2) {
                for (uint32_t i = 0; i < strlen(event->text.text); i++) {
                    key_buffer[key_buffer_len].key = event->text.text[i];
                    key_buffer[key_buffer_len].state = LV_INDEV_STATE_PRESSED;
                    key_buffer_len++;
                    key_buffer[key_buffer_len].key = event->text.text[i];
                    key_buffer[key_buffer_len].state = LV_INDEV_STATE_RELEASED;
                    key_buffer_len++;
                }
            }
        }
            break;
        default:
            break;

    }
}


/**
 * Convert a SDL key code to it's LV_KEY_* counterpart or return '\0' if it's not a control character.
 * @param sdl_key the key code
 * @return LV_KEY_* control character or '\0'
 */
uint32_t keycode_to_ctrl_key(SDL_Keycode sdl_key)
{
    /*Remap some key to LV_KEY_... to manage groups*/

    SDL_Keymod mode = SDL_GetModState();

    switch(sdl_key) {
        case SDLK_RIGHT:
        case SDLK_KP_PLUS:
            return LV_KEY_RIGHT;

        case SDLK_LEFT:
        case SDLK_KP_MINUS:
            return LV_KEY_LEFT;

        case SDLK_UP:
            return LV_KEY_UP;

        case SDLK_DOWN:
            return LV_KEY_DOWN;

        case SDLK_ESCAPE:
            return LV_KEY_ESC;

        case SDLK_BACKSPACE:
            return LV_KEY_BACKSPACE;

        case SDLK_DELETE:
            return LV_KEY_DEL;

        case SDLK_KP_ENTER:
        case '\r':
            return LV_KEY_ENTER;

        case SDLK_TAB:
            return (mode & KMOD_SHIFT)? LV_KEY_PREV: LV_KEY_NEXT;

        case SDLK_PAGEDOWN:
            return LV_KEY_NEXT;

        case SDLK_PAGEUP:
            return LV_KEY_PREV;

        default:
            return sdl_key;
    }
}
