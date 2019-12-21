//
// This module will take care of advancing tick count and scheduling async event for lvgl on ESP32.
// It should be imported after lvgl module is imported.
//

#include "py/obj.h"
#include "py/runtime.h"
#include "py/binary.h"
#include "../../lvgl/lvgl.h"
#include "freertos/FreeRTOS.h"
#include "freertos/timers.h"
#include "esp_log.h"

static const char TAG[] = "[LVGL]";
static TimerHandle_t xTimer = NULL;

void lvesp_deinit()
{
    if (xTimer) xTimerDelete(xTimer, portMAX_DELAY);
    xTimer = NULL;
}

STATIC mp_obj_t mp_deinit_lvesp32()
{
    lvesp_deinit();
    return mp_const_none;
}

STATIC MP_DEFINE_CONST_FUN_OBJ_0(mp_deinit_lvesp32_obj, mp_deinit_lvesp32);

STATIC mp_obj_t mp_lv_task_handler(mp_obj_t arg)
{
    lv_task_handler();
    return mp_const_none;
}

STATIC MP_DEFINE_CONST_FUN_OBJ_1(mp_lv_task_handler_obj, mp_lv_task_handler);

static void vTimerCallback(TimerHandle_t pxTimer)
{
    lv_tick_inc(portTICK_RATE_MS);
    mp_sched_schedule((mp_obj_t)&mp_lv_task_handler_obj, mp_const_none);
}

STATIC mp_obj_t mp_init_lvesp32()
{
    if (xTimer) return mp_const_none;

    lv_init();

    xTimer = xTimerCreate(
                "lvgl_timer",
                1,              // The timer period in ticks.
                pdTRUE,         // The timers will auto-reload themselves when they expire.
                NULL,           // User data passed to callback
                vTimerCallback  // Callback function
            );

    if (xTimer == NULL || xTimerStart( xTimer, 0 ) != pdPASS){
        ESP_LOGE(TAG, "Failed creating or starting LVGL timer!");
    } 

   return mp_const_none;
}

STATIC MP_DEFINE_CONST_FUN_OBJ_0(mp_init_lvesp32_obj, mp_init_lvesp32);

// Finalizer can be used to detect soft reset.
// Taken from: https://github.com/micropython/micropython/issues/1878#issuecomment-534911108

typedef struct _cb_finalizer_t {
    mp_obj_base_t base;
    mp_obj_t fun;
} cb_finalizer_t;

STATIC const mp_obj_type_t mp_type_cb_finalizer;

STATIC mp_obj_t new_cb_finalizer(const mp_obj_type_t *type_in, size_t n_args, size_t n_kw, const mp_obj_t *args) {
    mp_arg_check_num(n_args, n_kw, 1, 1, false);
    cb_finalizer_t *o = m_new_obj_with_finaliser(cb_finalizer_t);
    o->base.type = &mp_type_cb_finalizer;
    o->fun = args[0];
    return o;
}

STATIC mp_obj_t cb_finalizer_del(mp_obj_t self_in) {
    return mp_call_function_0(((cb_finalizer_t *)self_in)->fun);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(cb_finalizer_del_obj, cb_finalizer_del);

STATIC void cb_finalizer_attr(mp_obj_t self_in, qstr attr, mp_obj_t *dest) {
    if (dest[0] == MP_OBJ_NULL && attr == MP_QSTR___del__) {
        dest[0] = MP_OBJ_FROM_PTR(&cb_finalizer_del_obj);
        dest[1] = self_in;
    }
}

STATIC const mp_obj_type_t mp_type_cb_finalizer = {
    {&mp_type_type},
    .name = MP_QSTR_cb_finalizer,
    .make_new = new_cb_finalizer,
    .attr = cb_finalizer_attr,
};

STATIC const mp_rom_map_elem_t lvesp32_globals_table[] = {
        { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_lvesp32) },
        { MP_ROM_QSTR(MP_QSTR___init__), MP_ROM_PTR(&mp_init_lvesp32_obj) },
        { MP_ROM_QSTR(MP_QSTR_init), MP_ROM_PTR(&mp_init_lvesp32_obj) },
        { MP_ROM_QSTR(MP_QSTR_deinit), MP_ROM_PTR(&mp_deinit_lvesp32_obj) },
        { MP_ROM_QSTR(MP_QSTR_cb_finalizer), MP_ROM_PTR(&mp_type_cb_finalizer) },
};

STATIC MP_DEFINE_CONST_DICT (
    mp_module_lvesp32_globals,
    lvesp32_globals_table
);

const mp_obj_module_t mp_module_lvesp32 = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&mp_module_lvesp32_globals
};

