#include "py/runtime.h"
#include "py/mphal.h"
#include "softtimer.h"
#include "../../../lvgl/lvgl.h"
#include "../../include/common.h"
#include <stdint.h>
#include <stdbool.h>
#include "stm32746g_discovery_ts.h"
#include "ports/stm32/i2c.h"

static i2c_t *i2c_ts = NULL;

STATIC bool mp_read_ts(struct _lv_indev_drv_t * indev_drv, lv_indev_data_t * data);

STATIC mp_obj_t mp_init_ts(size_t n_args, const mp_obj_t *pos_args, mp_map_t *kw_args)
{
    enum { ARG_w, ARG_h };
    static const mp_arg_t allowed_args[] = {
        { MP_QSTR_w, MP_ARG_KW_ONLY | MP_ARG_INT, {.u_int = LV_HOR_RES_MAX} },
        { MP_QSTR_h, MP_ARG_KW_ONLY | MP_ARG_INT, {.u_int = LV_VER_RES_MAX} },
    };

    // parse args
    mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all(n_args, pos_args, kw_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);
    uint16_t x = (uint16_t) args[ARG_w].u_int;
	uint16_t y = (uint16_t) args[ARG_h].u_int;

	i2c_ts = I2C3;
	i2c_init(i2c_ts, MICROPY_HW_I2C3_SCL, MICROPY_HW_I2C3_SDA, 400000, 100);

	if(BSP_TS_Init(x, y) != TS_OK)
		printf("Touch screen initialization failed\r\n");

    return mp_const_none;
}

STATIC mp_obj_t mp_deinit_ts()
{
	BSP_TS_DeInit();
    return mp_const_none;
}

STATIC bool mp_read_ts(struct _lv_indev_drv_t * indev_drv, lv_indev_data_t * data)
{
	static TS_StateTypeDef ts_state = {0};
	static lv_coord_t lastX = 0;
	static lv_coord_t lastY = 0;

	BSP_TS_GetState(&ts_state);
	if(ts_state.touchDetected)
	{
		data->point.x = lastX = ts_state.touchX[0];
		data->point.y = lastY = ts_state.touchY[0];
		data->state = LV_INDEV_STATE_PR;
	}
	else
	{
	    data->point.x = lastX;
	    data->point.y = lastY;
	    data->state = LV_INDEV_STATE_REL;
	}

    return false;
}

STATIC MP_DEFINE_CONST_FUN_OBJ_KW(mp_init_ts_obj, 0, mp_init_ts);
STATIC MP_DEFINE_CONST_FUN_OBJ_0(mp_deinit_ts_obj, mp_deinit_ts);

DEFINE_PTR_OBJ(mp_read_ts);


STATIC const mp_rom_map_elem_t ts_globals_table[] = {
        { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_ts) },
        { MP_ROM_QSTR(MP_QSTR_init), MP_ROM_PTR(&mp_init_ts_obj) },
        { MP_ROM_QSTR(MP_QSTR_deinit), MP_ROM_PTR(&mp_deinit_ts_obj) },
        { MP_ROM_QSTR(MP_QSTR_read), MP_ROM_PTR(&PTR_OBJ(mp_read_ts))},
};
         

STATIC MP_DEFINE_CONST_DICT (
    mp_module_ts_globals,
    ts_globals_table
);

const mp_obj_module_t mp_module_ts = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&mp_module_ts_globals
};

MP_REGISTER_MODULE(MP_QSTR_ts, mp_module_ts, 1);


void TS_IO_Init(void)
{}

void TS_IO_Write(uint8_t Addr, uint8_t Reg, uint8_t Value)
{
	static uint8_t buff[2];
	buff[0] = Reg;
	buff[1] = Value;
	uint16_t addr = Addr>>1;
	i2c_writeto(i2c_ts, addr, buff, 2, true);
}

uint8_t TS_IO_Read(uint8_t Addr, uint8_t Reg)
{
	uint8_t Value=0xff;
	uint16_t addr = Addr>>1;
	i2c_writeto(i2c_ts, addr, &Reg, 1, true);
	i2c_readfrom(i2c_ts, addr, &Value, 1, true);
	return Value;
}

void TS_IO_Delay(uint32_t Delay)
{
	HAL_Delay(Delay);
}


