#include "../include/common.h"
#include "py/obj.h"
#include "py/runtime.h"
#include "py/gc.h"
#include "py/stackctrl.h"
#include "mphalport.h"
#include "espidf.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "soc/cpu.h"

// ESP IDF has some functions that are declared but not implemented.
// To avoid linking errors, provide empty implementation

inline void gpio_pin_wakeup_disable(void){}
inline void gpio_pin_wakeup_enable(uint32_t i, GPIO_INT_TYPE intr_state){}
inline void gpio_intr_ack_high(uint32_t ack_mask){}
inline void gpio_intr_ack(uint32_t ack_mask){}
inline uint32_t gpio_intr_pending_high(void){return 0;}
inline uint32_t gpio_intr_pending(void){return 0;}
inline void gpio_intr_handler_register(gpio_intr_handler_fn_t fn, void *arg){}
inline void gpio_init(void){}

void task_delay_ms(int ms)
{
	vTaskDelay(ms / portTICK_RATE_MS);
}

// ISR callbacks handling
// Can't use mp_sched_schedule because lvgl won't yield to give micropython a chance to run
// Must run Micropython in ISR itself.

DEFINE_PTR_OBJ_TYPE(spi_transaction_ptr_type, MP_QSTR_spi_transaction_ptr_t);

typedef struct{
    mp_ptr_t spi_transaction_ptr;
    mp_obj_t pre_cb;
    mp_obj_t post_cb;
} mp_spi_device_callbacks_t;

void *spi_transaction_set_cb(mp_obj_t pre_cb, mp_obj_t post_cb)
{
    mp_spi_device_callbacks_t *callbacks = m_new_obj(mp_spi_device_callbacks_t);
    callbacks->spi_transaction_ptr.base.type = &spi_transaction_ptr_type;
    callbacks->pre_cb = pre_cb != mp_const_none? pre_cb: NULL;
    callbacks->post_cb = post_cb != mp_const_none? post_cb: NULL;
    return callbacks;
}

STATIC void isr_print_strn(void *env, const char *str, size_t len) {
    size_t i;
    (void)env;
    for (i=0; i<len; i++) ets_write_char_uart(str[i]);
}

static const mp_print_t mp_isr_print = {NULL, isr_print_strn};

// Called in ISR context!
//
static inline void cb_isr(mp_obj_t cb, mp_obj_t arg)
{
    if (cb != NULL && cb != mp_const_none) {

        volatile uint32_t sp = (uint32_t)get_sp();

        // Calling micropython from ISR
        // See: https://github.com/micropython/micropython/issues/4895

        void *old_state = mp_thread_get_state();

        mp_state_thread_t ts; // local thread state for the ISR
        mp_thread_set_state(&ts);
        mp_stack_set_top((void*)sp); // need to include in root-pointer scan
        mp_stack_set_limit(configIDLE_TASK_STACK_SIZE - 1024); // tune based on ISR thread stack size
        mp_locals_set(mp_state_ctx.thread.dict_locals); // use main thread's locals
        mp_globals_set(mp_state_ctx.thread.dict_globals); // use main thread's globals

        mp_sched_lock(); // prevent VM from switching to another MicroPython thread
        gc_lock(); // prevent memory allocation

        nlr_buf_t nlr;
        if (nlr_push(&nlr) == 0) {
            mp_call_function_1(cb, arg);
            nlr_pop();
        } else {
            ets_printf("Uncaught exception in IRQ callback handler!\n");
            mp_obj_print_exception(&mp_isr_print, MP_OBJ_FROM_PTR(nlr.ret_val));
        }

        gc_unlock();
        mp_sched_unlock();

        mp_thread_set_state(old_state);

        mp_hal_wake_main_task_from_isr();
    }
}

// Called in ISR context!
void spi_pre_cb_isr(spi_transaction_t *trans)
{
    mp_spi_device_callbacks_t *self = (mp_spi_device_callbacks_t*)trans->user;
    if (self) {
        self->spi_transaction_ptr.ptr = trans;
        cb_isr(self->pre_cb, MP_OBJ_FROM_PTR(self));
    }
}

// Called in ISR context!
void spi_post_cb_isr(spi_transaction_t *trans)
{
    mp_spi_device_callbacks_t *self = (mp_spi_device_callbacks_t*)trans->user;
    if (self) {
        self->spi_transaction_ptr.ptr = trans;
        cb_isr(self->post_cb, MP_OBJ_FROM_PTR(self));
    }
}

/////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Demo code of ili9341 flush in C
// Built to compare with micropython performance

#ifdef ENABLE_ILI9341_DEMO_FLUSH

#include "../../lvgl/lvgl.h"

static int g_dc = -1;
static spi_device_handle_t g_spi = NULL;

void setup_demo(int dc, void* _spi)
{
    spi_device_handle_t spi = _spi;

    g_dc = dc;
    g_spi = spi;
}

static void spi_send_value(const uint8_t *value, uint8_t size)
{
    static spi_transaction_t trans = {0};
    trans.length = size*8;
    trans.tx_buffer = value;
    trans.user = NULL;
    spi_device_polling_transmit(g_spi, &trans);
}

static inline void send_cmd(uint8_t cmd)
{
   DMA_ATTR static uint8_t value[4] = {0};
   value[0] = cmd;
   gpio_set_level(g_dc, 0);
   spi_send_value(value, 1);
}

static inline void send_data(const uint8_t *value)
{
   gpio_set_level(g_dc, 1);
   spi_send_value(value, 4);
}


static void send_data_dma(void *disp_drv, void *data, size_t size)
{
    static spi_transaction_t trans = {0};
    gpio_set_level(g_dc, 1);
    trans.length = size*8;
    trans.tx_buffer = data;
    trans.user = disp_drv;
    spi_device_queue_trans(g_spi, &trans, -1);
}

void demo_post_cb_isr(spi_transaction_t *trans)
{
    if (trans->user)
        lv_disp_flush_ready(trans->user);
}

void flush_demo(void *disp_drv, const void *_area, void *_color_p)
{
    const lv_area_t *area = _area;
    lv_color_t *color_p = _color_p;

    DMA_ATTR static uint8_t buf[4] = {0};
   
    send_cmd(0x2A);

    buf[0] = (area->x1 >> 8) & 0xFF;
    buf[1] = area->x1 & 0xFF;
    buf[2] = (area->x2 >> 8) & 0xFF;
    buf[3] = area->x2 & 0xFF;
    send_data(buf);

	// Page addresses

	send_cmd(0x2B);

    buf[0] = (area->y1 >> 8) & 0xFF;
    buf[1] = area->y1 & 0xFF;
    buf[2] = (area->y2 >> 8) & 0xFF;
    buf[3] = area->y2 & 0xFF;
    send_data(buf);

	// Memory write by DMA, disp_flush_ready when finished

	send_cmd(0x2C);

	size_t size = (area->x2 - area->x1 + 1) * (area->y2 - area->y1 + 1);
    send_data_dma(disp_drv, color_p, size * 2);
}

#endif
