// Touch pointer driver for STM32H7 with LVGL.
// Provides MicroPython interface for configuring and using various touch I2C devices.
// Supports both hardware I2C (HAL) and software I2C (bit-bang) modes.

#include <stdint.h>
#include <string.h>
#include <stddef.h>
#include <stdbool.h>

#include "mpconfigboard.h"
#include "py/mphal.h"
#include "boardctrl.h"
#include <stm32h7xx_hal.h>
#include <extmod/modmachine.h>
#include <lvgl.h>
#include <lv_display_private.h>
// Required by common.h which uses the STATIC macro
#define STATIC static
#include <common.h>

// GT9XX I2C addresses (7-bit 0x14)
#define TP_DEF_I2C_ADDR     (0x14)
#define TP_DEF_TOUCH_MAX    (5)

#define GT9XX_CFG_ADDR  0x8047
#define GT9XX_READ_ADDR 0x814E
#define GT9XX_ID_ADDR   0x8140

MP_REGISTER_ROOT_POINTER(mp_obj_t current_tp_obj);

// Multi-touch scan result from the touch controller
typedef struct _touch_data_t {
    uint8_t flag;
    uint8_t num;
    uint16_t x[TP_DEF_TOUCH_MAX];
    uint16_t y[TP_DEF_TOUCH_MAX];
} touch_data_t;

// MicroPython touch-pointer object
typedef struct _tp_obj_t {
    mp_obj_base_t base;
    char device[20];                // touch device
    uint8_t touch_max;              // maximum number of touch points
    uint8_t addr;                   // i2c address
    mp_hal_pin_obj_t rst_pin;       // reset pin
    mp_hal_pin_obj_t int_pin;       // interrupt pin (input after tp reset)
    mp_obj_t i2c_obj;               // mp i2c object
    mp_machine_i2c_p_t *i2c_proto;  // mp i2c protocol
} tp_obj_t;

static void mp_tp_read(lv_indev_t *indev_drv, lv_indev_data_t *data);
static bool config_gt9xx(tp_obj_t *self);
static void gt9xx_hw_reset(tp_obj_t *self);
static touch_data_t gt9xx_touch_scan(tp_obj_t *self);

static mp_obj_t mp_tp_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *all_args);
DEFINE_PTR_OBJ(mp_tp_read);

static const mp_rom_map_elem_t mp_tp_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_mod_tp) },
    { MP_ROM_QSTR(MP_QSTR_tp_read), MP_ROM_PTR(&PTR_OBJ(mp_tp_read))},
};

static MP_DEFINE_CONST_DICT(mp_tp_locals_dict, mp_tp_locals_dict_table);

// Touch type definition using slot-based system
MP_DEFINE_CONST_OBJ_TYPE(
    mp_tp_type,
    MP_QSTR_TP,
    MP_TYPE_FLAG_NONE,
    make_new, mp_tp_make_new,
    locals_dict, &mp_tp_locals_dict
);

// Module globals table
static const mp_rom_map_elem_t mod_tp_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_mod_tp) },
    { MP_ROM_QSTR(MP_QSTR_TP), MP_ROM_PTR(&mp_tp_type) },
    { MP_ROM_QSTR(MP_QSTR_I2C_ADDR), MP_ROM_INT(TP_DEF_I2C_ADDR) },
};
static MP_DEFINE_CONST_DICT(mod_tp_globals, mod_tp_globals_table);

const mp_obj_module_t mp_touch_i2c = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&mod_tp_globals
};

#if MODULE_TOUCH_I2C_ENABLED
MP_REGISTER_MODULE(MP_QSTR_touch_i2c, mp_touch_i2c);
#endif

// Constructor - create a touch-screen object with device and I2C parameters.
static mp_obj_t mp_tp_make_new(const mp_obj_type_t *type,
                               size_t n_args, size_t n_kw,
                               const mp_obj_t *all_args) {
    enum {
        ARG_TP_DEVICE, ARG_I2C_OBJ, ARG_I2C_ADDR, ARG_TOUCH_MAX, ARG_RST_PIN, ARG_INT_PIN,
    };

    static const mp_arg_t allowed_args[] = {
        { MP_QSTR_device, MP_ARG_KW_ONLY | MP_ARG_OBJ, {.u_obj = MP_OBJ_NULL} },
        { MP_QSTR_i2c, MP_ARG_REQUIRED | MP_ARG_OBJ, {.u_obj = MP_OBJ_NULL} },
        { MP_QSTR_addr, MP_ARG_KW_ONLY | MP_ARG_INT, {.u_int = TP_DEF_I2C_ADDR} },
        { MP_QSTR_tp_max, MP_ARG_KW_ONLY | MP_ARG_INT, {.u_int = TP_DEF_TOUCH_MAX} },
        { MP_QSTR_tp_rst, MP_ARG_REQUIRED | MP_ARG_KW_ONLY | MP_ARG_OBJ, {.u_obj = MP_OBJ_NULL} },
        { MP_QSTR_tp_int, MP_ARG_REQUIRED | MP_ARG_KW_ONLY | MP_ARG_OBJ, {.u_obj = MP_OBJ_NULL} },
    };

    mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all_kw_array(n_args, n_kw, all_args,
                               MP_ARRAY_SIZE(allowed_args),
                               allowed_args, args);

    tp_obj_t *self = m_new_obj(tp_obj_t);
    self->base.type = type;

    if (args[ARG_TP_DEVICE].u_obj != MP_OBJ_NULL) {
        const char *s = mp_obj_str_get_str(args[ARG_TP_DEVICE].u_obj);
        strncpy(self->device, s, sizeof(self->device) - 1);
        self->device[sizeof(self->device) - 1] = '\0'; // Safety null-terminator
    } else {
        memset(self->device, 0, sizeof(self->device));
    }
    self->i2c_obj = args[ARG_I2C_OBJ].u_obj;
    self->addr = args[ARG_I2C_ADDR].u_int;
    self->touch_max = args[ARG_TOUCH_MAX].u_int;

    if (self->touch_max > TP_DEF_TOUCH_MAX) {
        self->touch_max = TP_DEF_TOUCH_MAX;
    }
    // Convert the MicroPython Pin object to a HAL pin
    if (args[ARG_RST_PIN].u_obj != MP_OBJ_NULL) {
        self->rst_pin = mp_hal_get_pin_obj(args[ARG_RST_PIN].u_obj);
    }
    if (args[ARG_INT_PIN].u_obj != MP_OBJ_NULL) {
        self->int_pin = mp_hal_get_pin_obj(args[ARG_INT_PIN].u_obj);
    }
    if (self->i2c_obj == MP_OBJ_NULL) {
        mp_raise_TypeError(MP_ERROR_TEXT("I2C object required"));
    }
    // Get the I2C protocol
    self->i2c_proto = (mp_machine_i2c_p_t *)
        MP_OBJ_TYPE_GET_SLOT(mp_obj_get_type(self->i2c_obj), protocol);

    if (self->i2c_proto == NULL) {
        mp_raise_TypeError(MP_ERROR_TEXT("Object does not support I2C protocol"));
    }
    if (strcmp(self->device, "GT911") == 0) {
        if (!config_gt9xx(self)) {
            mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("Touch device init error"));
        }
    } else {
        mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("Device not supported"));
    }
    MP_STATE_PORT(current_tp_obj) = MP_OBJ_FROM_PTR(self);
    return MP_STATE_PORT(current_tp_obj);
}

// LVGL input-device read callback.
// Polls the touch controller and fills data with the current state.
static void mp_tp_read(lv_indev_t *indev_drv, lv_indev_data_t *data) {
    static int32_t last_x = 0;
    static int32_t last_y = 0;

    if (MP_STATE_PORT(current_tp_obj) == MP_OBJ_NULL) {
        data->point.x = last_x;
        data->point.y = last_y;
        data->state = LV_INDEV_STATE_RELEASED;
        return;
    }

    tp_obj_t *self = MP_OBJ_TO_PTR(MP_STATE_PORT(current_tp_obj));
    touch_data_t ts_state = gt9xx_touch_scan(self);

    if (ts_state.flag) {
        data->point.x = last_x = ts_state.x[0];
        data->point.y = last_y = ts_state.y[0];
        data->state = LV_INDEV_STATE_PRESSED;
    } else {
        data->point.x = last_x;
        data->point.y = last_y;
        data->state = LV_INDEV_STATE_RELEASED;
    }
}

// Reset the GT9XX touch controller and select I2C address 0x14.
// The GT911 latches its I2C slave address from the INT pin level on the
// rising edge of RST. INT HIGH selects 0x14 (8-bit 0x28/0x29).
static void gt9xx_hw_reset(tp_obj_t *self) {
    // Configure INT pin as output and set HIGH for address 0x14
    mp_hal_pin_output(self->rst_pin);
    mp_hal_pin_output(self->int_pin);
    mp_hal_delay_ms(1);
    mp_hal_pin_low(self->rst_pin);
    mp_hal_delay_ms(1);
    mp_hal_pin_high(self->int_pin);
    // Assert reset
    mp_hal_delay_ms(10);
    // Release reset - GT911 samples INT here for address selection
    // INT HIGH on rising RST edge selects address 0x14 (0x28/0x29)
    mp_hal_pin_high(self->rst_pin);
    mp_hal_delay_ms(60);
    // Release INT so the controller can use it for interrupt signaling
    mp_hal_pin_input(self->int_pin);
    mp_hal_delay_ms(50);
}

static uint8_t gt9xx_write_data(tp_obj_t *self, uint16_t addr, uint8_t value) {
    uint8_t buf[] = {
        (uint8_t)(addr >> 8),   // Register high byte
        (uint8_t)(addr & 0xFF), // Register low byte
        value                   // Data byte to write
    };

    // Prepare the I2C buffer structure
    mp_machine_i2c_buf_t i2c_buf = {.len = 3, .buf = buf};
    int ret = self->i2c_proto->transfer((mp_obj_base_t *)self->i2c_obj, self->addr, 1, &i2c_buf, MP_MACHINE_I2C_FLAG_STOP);

    return (ret >= 0) ? 0 : 1;
}

static uint8_t gt9xx_read_reg(tp_obj_t *self, uint16_t addr, uint8_t cnt, uint8_t *value) {
    uint8_t reg_addr_buf[] = {
        (uint8_t)(addr >> 8),
        (uint8_t)(addr & 0xFF)
    };

    // Write register address (no STOP, uses repeated start)
    mp_machine_i2c_buf_t wbuf = {.len = 2, .buf = reg_addr_buf};
    int ret = self->i2c_proto->transfer(
        (mp_obj_base_t *)self->i2c_obj, self->addr, 1, &wbuf, 0);
    if (ret < 0) {
        return 1;
    }

    // Read data (with STOP)
    mp_machine_i2c_buf_t rbuf = {.len = cnt, .buf = value};
    ret = self->i2c_proto->transfer(
        (mp_obj_base_t *)self->i2c_obj, self->addr, 1, &rbuf,
        MP_MACHINE_I2C_FLAG_READ | MP_MACHINE_I2C_FLAG_STOP);

    return (ret >= 0) ? 0 : 1;
}

// Initialize the GT9XX touchscreen controller.
// Reads the product ID (e.g. "911\0" for GT911) and verifies
// that the first character is '9' (GT9xx family).
static bool config_gt9xx(tp_obj_t *self) {
    uint8_t gt9xx_info[11] = {0};

    gt9xx_hw_reset(self);

    if (gt9xx_read_reg(self, GT9XX_ID_ADDR, 11, gt9xx_info) != 0) {
        return false;
    }
    // Verify product ID starts with '9' (GT9xx family: GT911, GT928, etc.)
    if (gt9xx_info[0] != '9') {
        return false;
    }
    return true;
}

// Scan for touch events on the GT9XX controller.
// Register 0x814E bit 7 = buffer ready, bits 3:0 = number of touch points.
// Data is only valid when the buffer-ready flag is set.
static touch_data_t gt9xx_touch_scan(tp_obj_t *self) {
    touch_data_t result = {0};
    uint8_t touch_data[2 + 8 * TP_DEF_TOUCH_MAX];

    if (gt9xx_read_reg(self, GT9XX_READ_ADDR, 2 + 8 * self->touch_max, touch_data) != 0) {
        return result;
    }
    // Always clear the buffer-ready flag so the controller prepares new data
    gt9xx_write_data(self, GT9XX_READ_ADDR, 0);

    // Bit 7 must be set for the data to be valid
    if (!(touch_data[0] & 0x80)) {
        return result;
    }

    uint8_t num = touch_data[0] & 0x0f;
    if (num >= 1 && num <= self->touch_max) {
        result.num = num;
        for (uint8_t i = 0; i < num; i++) {
            result.x[i] = (touch_data[3 + 8 * i] << 8) | touch_data[2 + 8 * i];
            result.y[i] = (touch_data[5 + 8 * i] << 8) | touch_data[4 + 8 * i];
        }
        result.flag = 1;
    }
    return result;
}
