// LTDC display driver for STM32H7 with LVGL.
// Provides MicroPython interface for configuring and using the LTDC peripheral.

#include <stdint.h>
#include <string.h>
#include <stddef.h>
#include <stdbool.h>

#include "mpconfigboard.h"
#include "lv_conf.h"
#include "py/mphal.h"
#include "py/gc.h"
#include "py/runtime.h"
#include "py/nlr.h"
#include "boardctrl.h"
#include <stm32h7xx_hal.h>
#include "mpu.h"
#include "led.h"
#include <lvgl.h>
#include <lv_display_private.h>
#include <lv_global.h>
// Required by common.h which uses the STATIC macro
#define STATIC static
#include <common.h>

#define LTDC_POL_HS_MASK  (1 << 0)   // bit 0: HSYNC polarity
#define LTDC_POL_VS_MASK  (1 << 1)   // bit 1: VSYNC polarity
#define LTDC_POL_DE_MASK  (1 << 2)   // bit 2: DE polarity
#define LTDC_POL_PC_MASK  (1 << 3)   // bit 3: Pixel Clock polarity

// Global because the HAL LTDC IRQ handler references it by name
LTDC_HandleTypeDef hltdc   = {0};
DMA2D_HandleTypeDef hdma2d = {0};

// LTDC display object - holds timing parameters, framebuffer pointers
// and LVGL display state for the STM32H7 LTDC peripheral.
typedef struct _ltdc_display_obj_t {
    mp_obj_base_t base;
    uint32_t hsync;       // horizontal sync width
    uint32_t vsync;       // vertical sync height
    uint32_t hbp;         // horizontal back porch
    uint32_t vbp;         // vertical back porch
    uint32_t hfp;         // horizontal front porch
    uint32_t vfp;         // vertical front porch
    uint32_t width;       // active display width
    uint32_t height;      // active display height
    uint32_t polarity;    // sync polarity flags
    uint32_t fb_size;     // framebuffer size in bytes
    uint32_t fb_addr;     // framebuffer base address
    mp_hal_pin_obj_t rst_pin; // LCD reset pin
    mp_hal_pin_obj_t bl_pin;  // LCD backlight pin
    pyb_led_t bl_led;         // LCD backlight LED index
    lv_display_t *disp;  // LVGL display structure
    lv_color_format_t color_format;  // LVGL color format
    lv_color_t *fb[2];   // LTDC framebuffer pointers
} ltdc_display_obj_t;

MP_REGISTER_ROOT_POINTER(void *ltdc_fb[2]);
MP_REGISTER_ROOT_POINTER(mp_obj_t current_ltdc_obj);

void led_set_intensity(pyb_led_t led, mp_int_t intensity);
static void lcd_hw_reset(ltdc_display_obj_t *self);
static void optimize_axi_for_display(void);
static void configure_fb_mpu_wt(ltdc_display_obj_t *ltdc_obj);
static bool config_ltdc(ltdc_display_obj_t *self);
static bool config_dma2d(ltdc_display_obj_t *self);
static mp_obj_t mp_ltdc_init(size_t n_args, const mp_obj_t *pos_args, mp_map_t *kw_args);
static mp_obj_t mp_ltdc_deinit(mp_obj_t self_in);
static mp_obj_t mp_ltdc_framebuffer(mp_obj_t self_in, mp_obj_t n_obj);
static mp_obj_t mp_ltdc_make_new(const mp_obj_type_t *type,
                                 size_t n_args, size_t n_kw,
                                 const mp_obj_t *all_args);
static void mp_ltdc_flush(lv_display_t *disp_drv, const lv_area_t *area, lv_color_t *color_p);

static MP_DEFINE_CONST_FUN_OBJ_KW(mp_ltdc_init_obj, 1, mp_ltdc_init);
static MP_DEFINE_CONST_FUN_OBJ_1(mp_ltdc_deinit_obj, mp_ltdc_deinit);
static MP_DEFINE_CONST_FUN_OBJ_2(mp_ltdc_framebuffer_obj, mp_ltdc_framebuffer);
DEFINE_PTR_OBJ(mp_ltdc_flush);

static const mp_rom_map_elem_t mp_ltdc_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_st_ltdc) },
    { MP_ROM_QSTR(MP_QSTR_init), MP_ROM_PTR(&mp_ltdc_init_obj) },
    { MP_ROM_QSTR(MP_QSTR_deinit), MP_ROM_PTR(&mp_ltdc_deinit_obj) },
    { MP_ROM_QSTR(MP_QSTR_flush), MP_ROM_PTR(&PTR_OBJ(mp_ltdc_flush))},
    { MP_ROM_QSTR(MP_QSTR_framebuffer), MP_ROM_PTR(&mp_ltdc_framebuffer_obj)},
};

static MP_DEFINE_CONST_DICT(mp_ltdc_locals_dict, mp_ltdc_locals_dict_table);

// Display type definition using slot-based system
MP_DEFINE_CONST_OBJ_TYPE(
    mp_ltdc_type,
    MP_QSTR_LTDCDisplay,
    MP_TYPE_FLAG_NONE,
    make_new, mp_ltdc_make_new,
    locals_dict, &mp_ltdc_locals_dict
);

// Module globals table
static const mp_rom_map_elem_t mod_ltdc_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_st_ltdc) },
    { MP_ROM_QSTR(MP_QSTR_LTDC), MP_ROM_PTR(&mp_ltdc_type) },
    // Polarity constants
    { MP_ROM_QSTR(MP_QSTR_POL_HS), MP_ROM_INT(LTDC_POL_HS_MASK) },
    { MP_ROM_QSTR(MP_QSTR_POL_VS), MP_ROM_INT(LTDC_POL_VS_MASK) },
    { MP_ROM_QSTR(MP_QSTR_POL_DE), MP_ROM_INT(LTDC_POL_DE_MASK) },
    { MP_ROM_QSTR(MP_QSTR_POL_PC), MP_ROM_INT(LTDC_POL_PC_MASK) },
};
static MP_DEFINE_CONST_DICT(mod_ltdc_globals, mod_ltdc_globals_table);

const mp_obj_module_t mp_st_ltdc = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&mod_ltdc_globals
};

#if MODULE_ST_LTDC_ENABLED
MP_REGISTER_MODULE(MP_QSTR_st_ltdc, mp_st_ltdc);
#endif

// Configure SDRAM as Write-Through for the framebuffer region.
// Uses Region 6 (MPU_REGION_DMA_UNCACHED_1) which has HIGHER priority
// than Region 5 (sdram.c configures all SDRAM as Write-Back on Region 5).
// ARM MPU rule: higher region number wins on overlap.
//
// Write-Through (TEX=0, C=1, B=0): CPU writes go to BOTH DCache and SDRAM
// simultaneously, so LTDC/DMA2D always read current data from SDRAM
// without needing manual SCB_CleanDCache_by_Addr() calls.
//
// The region size is computed dynamically from the actual framebuffer
// addresses so that only the minimum power-of-2 area is Write-Through
// (4MB for RGB565, 8MB for RGB888 on a 1024x600 display).
#define MPU_CONFIG_WRITE_THROUGH(size) ( \
    MPU_INSTRUCTION_ACCESS_DISABLE << MPU_RASR_XN_Pos \
        | MPU_REGION_FULL_ACCESS << MPU_RASR_AP_Pos \
        | MPU_TEX_LEVEL0 << MPU_RASR_TEX_Pos \
        | MPU_ACCESS_NOT_SHAREABLE << MPU_RASR_S_Pos \
        | MPU_ACCESS_CACHEABLE << MPU_RASR_C_Pos \
        | MPU_ACCESS_NOT_BUFFERABLE << MPU_RASR_B_Pos \
        | 0x00 << MPU_RASR_SRD_Pos \
        | (size) << MPU_RASR_SIZE_Pos \
        | MPU_REGION_ENABLE << MPU_RASR_ENABLE_Pos \
    )

// Return the smallest MPU region size (log2 encoding) that covers all
// framebuffers.  MPU regions must be power-of-2 sized, minimum 4MB.
static uint32_t fb_mpu_region_size(ltdc_display_obj_t *ltdc_obj) {
    uint32_t fb_end = (uint32_t)ltdc_obj->fb[0] + ltdc_obj->fb_size;
    if (ltdc_obj->fb[1] != NULL) {
        uint32_t end1 = (uint32_t)ltdc_obj->fb[1] + ltdc_obj->fb_size;
        if (end1 > fb_end) {
            fb_end = end1;
        }
    }
    uint32_t needed = fb_end - ltdc_obj->fb_addr;

    // MPU_REGION_SIZE_xMB = log2(bytes) - 1
    // 4MB = 0x15, 8MB = 0x16, 16MB = 0x17, 32MB = 0x18
    if (needed <= 4 * 1024 * 1024) {
        return MPU_REGION_SIZE_4MB;
    }
    if (needed <= 8 * 1024 * 1024) {
        return MPU_REGION_SIZE_8MB;
    }
    if (needed <= 16 * 1024 * 1024) {
        return MPU_REGION_SIZE_16MB;
    }
    return MPU_REGION_SIZE_32MB;
}

static void configure_fb_mpu_wt(ltdc_display_obj_t *ltdc_obj) {
    uint32_t region_size = fb_mpu_region_size(ltdc_obj);
    uint32_t irq_state = mpu_config_start();
    mpu_config_region(MPU_REGION_DMA_UNCACHED_1,   // Region 6 > Region 5
                      ltdc_obj->fb_addr,
                      MPU_CONFIG_WRITE_THROUGH(region_size));
    mpu_config_end(irq_state);
}

// Optimize AXI bus priorities for tear-free LTDC display.
// Gives LTDC top read/write QoS and limits SDRAM to one outstanding
// transaction so the display controller is never starved.
static void optimize_axi_for_display(void) {
    // Limit SDRAM to 1 outstanding transaction (Target/Slave Port 5)
    GPV->AXI_TARG5_FN_MOD_ISS_BM = 0x01;
    // Top priority for LTDC (Initiator/Master Port 6)
    GPV->AXI_INI6_READ_QOS = 0x0F;
    GPV->AXI_INI6_WRITE_QOS = 0x0F;
    // Top priority for DMA2D (Initiator/Master Port 5)
    GPV->AXI_INI5_READ_QOS = 0x0E;
    GPV->AXI_INI5_WRITE_QOS = 0x0E;
    // Low priority for CPU (Initiator/Master Port 2)
    GPV->AXI_INI2_READ_QOS = 0x0;
    GPV->AXI_INI2_WRITE_QOS = 0x0;
}

// Return a bytearray view of the requested framebuffer.
// On first call the framebuffer is allocated in SDRAM.
static mp_obj_t mp_ltdc_framebuffer(mp_obj_t self_in, mp_obj_t n_obj) {
    int n = mp_obj_get_int(n_obj) - 1;
    ltdc_display_obj_t *ltdc_obj = MP_OBJ_TO_PTR(self_in);

    if (n < 0 || n > 1) {
        mp_raise_msg_varg(&mp_type_ValueError,
            MP_ERROR_TEXT("framebuffer index %d out of range (1-2)"), n + 1);
    }
    uint8_t bpp = lv_color_format_get_size(ltdc_obj->color_format);
    if (bpp < 2 || bpp > 4) {
        mp_raise_msg_varg(&mp_type_ValueError,
            MP_ERROR_TEXT("BPP %d out of range (2-3)"), bpp);
    }
    ltdc_obj->fb_size = ltdc_obj->width * ltdc_obj->height * bpp;

    if (ltdc_obj->fb[n] == NULL) {
        // Allocate on extRAM with 1KB alignment for LTDC burst access on AHB
        ltdc_obj->fb[n] = MP_STATE_PORT(ltdc_fb[n]) = m_malloc(ltdc_obj->fb_size + 1024);
        ltdc_obj->fb[n] = (lv_color_t *)((uint32_t)ltdc_obj->fb[n] + 1024 - (uint32_t)ltdc_obj->fb[n] % 1024);
        memset((void *)ltdc_obj->fb[n], 0, ltdc_obj->fb_size);
    }
    return mp_obj_new_bytearray_by_ref(ltdc_obj->fb_size, (void *)ltdc_obj->fb[n]);
}

// Constructor - creates display object with timing parameters.
static mp_obj_t mp_ltdc_make_new(const mp_obj_type_t *type,
                                 size_t n_args, size_t n_kw,
                                 const mp_obj_t *all_args) {
    enum {
        ARG_rst,  ARG_width, ARG_height,
        ARG_hsync, ARG_hbp, ARG_hfp,
        ARG_vsync, ARG_vbp, ARG_vfp,
        ARG_fb_addr, ARG_bl, ARG_polarity,
    };

    static const mp_arg_t allowed_args[] = {
        // Reset pin (optional)
        { MP_QSTR_rst,      MP_ARG_KW_ONLY | MP_ARG_OBJ, {.u_obj = MP_OBJ_NULL} },
        // Panel geometry (required)
        { MP_QSTR_width,    MP_ARG_REQUIRED | MP_ARG_KW_ONLY | MP_ARG_INT, {.u_int = 0} },
        { MP_QSTR_height,   MP_ARG_REQUIRED | MP_ARG_KW_ONLY | MP_ARG_INT, {.u_int = 0} },
        // Timing in pixel clocks / lines (required)
        { MP_QSTR_hsync,    MP_ARG_REQUIRED | MP_ARG_KW_ONLY | MP_ARG_INT, {.u_int = 0} },
        { MP_QSTR_hbp,      MP_ARG_REQUIRED | MP_ARG_KW_ONLY | MP_ARG_INT, {.u_int = 0} },
        { MP_QSTR_hfp,      MP_ARG_REQUIRED | MP_ARG_KW_ONLY | MP_ARG_INT, {.u_int = 0} },
        { MP_QSTR_vsync,    MP_ARG_REQUIRED | MP_ARG_KW_ONLY | MP_ARG_INT, {.u_int = 0} },
        { MP_QSTR_vbp,      MP_ARG_REQUIRED | MP_ARG_KW_ONLY | MP_ARG_INT, {.u_int = 0} },
        { MP_QSTR_vfp,      MP_ARG_REQUIRED | MP_ARG_KW_ONLY | MP_ARG_INT, {.u_int = 0} },
        // Framebuffer base address (optional, default 0xC0000000)
        { MP_QSTR_fb_addr,  MP_ARG_KW_ONLY | MP_ARG_OBJ, {.u_obj = mp_const_none} },
        // Backlight: Pin object or LED index (required)
        { MP_QSTR_bl,       MP_ARG_REQUIRED | MP_ARG_KW_ONLY | MP_ARG_OBJ, {.u_obj = mp_const_none} },
        // LTDC polarity flags (optional, default = all active-low)
        { MP_QSTR_polarity, MP_ARG_KW_ONLY | MP_ARG_INT, {.u_int = 0} },
    };

    mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all_kw_array(n_args, n_kw, all_args,
                               MP_ARRAY_SIZE(allowed_args),
                               allowed_args, args);

    // Invalidate immediately so any LTDC/DMA2D IRQ that fires between the
    // soft-reset heap free and the upcoming mp_ltdc_init() call gets a safe
    // NULL and returns without dereferencing freed memory.
    MP_STATE_PORT(current_ltdc_obj) = MP_OBJ_NULL;

    ltdc_display_obj_t *self = m_new_obj(ltdc_display_obj_t);
    memset(self, 0, sizeof(*self));
    self->base.type = type;

    // Reset pin (optional)
    if (args[ARG_rst].u_obj != MP_OBJ_NULL) {
        self->rst_pin = mp_hal_get_pin_obj(args[ARG_rst].u_obj);
    } else {
        self->rst_pin = MP_OBJ_NULL;
    }

    if (args[ARG_fb_addr].u_obj != mp_const_none) {
        self->fb_addr = (uint32_t)mp_obj_get_int_truncated(args[ARG_fb_addr].u_obj);
    } else {
        self->fb_addr = 0xC0000000;
    }

    // Panel geometry
    self->width  = args[ARG_width].u_int;
    self->height = args[ARG_height].u_int;
    // Timing
    self->hsync = args[ARG_hsync].u_int;
    self->hbp   = args[ARG_hbp].u_int;
    self->hfp   = args[ARG_hfp].u_int;
    self->vsync = args[ARG_vsync].u_int;
    self->vbp   = args[ARG_vbp].u_int;
    self->vfp   = args[ARG_vfp].u_int;
    self->polarity  = args[ARG_polarity].u_int;

    if (mp_obj_is_small_int(args[ARG_bl].u_obj)) {
        self->bl_led = mp_obj_get_int(args[ARG_bl].u_obj);
        if (self->bl_led > 0) {
            led_set_intensity(self->bl_led, 1);
        }
    } else if (mp_obj_is_type(args[ARG_bl].u_obj, &pin_type)) {
        self->bl_pin = mp_hal_get_pin_obj(args[ARG_bl].u_obj);
    } else {
        mp_raise_TypeError(MP_ERROR_TEXT("Pin or LED object expected"));
    }

    self->fb_size = 0;
    self->disp = MP_OBJ_NULL;
    self->color_format = LV_COLOR_FORMAT_UNKNOWN;
    self->fb[0] = NULL;
    self->fb[1] = NULL;
    return MP_OBJ_FROM_PTR(self);
}

// LVGL flush callback supporting DIRECT, FULL and PARTIAL render modes.
//
// DIRECT/FULL: LVGL renders the full screen into one of the double buffers.
//   We just swap the LTDC read address at VSYNC — no copy needed.
//   flush_ready is signalled by HAL_LTDC_ReloadEventCallback.
//
//   Python side: disp.set_buffers(fb1, fb2, len(fb1), lv.DISPLAY_RENDER_MODE.DIRECT)
//   where fb1/fb2 come from disp.framebuffer(1) / disp.framebuffer(2).
//
// PARTIAL: LVGL renders only dirty rectangles into small, dedicated render
//   buffers (NOT the LTDC framebuffers). color_p holds the rendered pixels
//   for the rectangle [area], starting at offset 0. DMA2D copies them to the
//   correct position inside fb[0] (the framebuffer LTDC reads from).
//   flush_ready is signalled by DMA2D_TransferComplete.
//
//   IMPORTANT: for PARTIAL mode the render buffers passed to set_buffers()
//   must be SEPARATE from the LTDC framebuffers. If you reuse framebuffer(1)
//   as a render buffer, LVGL will overwrite its beginning with the dirty-rect
//   pixels, corrupting the display content at screen position (0,0).
//
//   Python side: disp.set_buffers(bytearray(W*H//10*BPP), bytearray(W*H//10*BPP),
//                                 W*H//10*BPP, lv.DISPLAY_RENDER_MODE.PARTIAL)
static void mp_ltdc_flush(lv_display_t *disp_drv, const lv_area_t *area, lv_color_t *color_p) {
    if (MP_STATE_PORT(current_ltdc_obj) == MP_OBJ_NULL) {
        lv_display_flush_ready(disp_drv);
        return;
    }
    ltdc_display_obj_t *ltdc_obj = MP_OBJ_TO_PTR(MP_STATE_PORT(current_ltdc_obj));
    ltdc_obj->disp = disp_drv;
    if (disp_drv->render_mode == LV_DISPLAY_RENDER_MODE_DIRECT ||
            disp_drv->render_mode == LV_DISPLAY_RENDER_MODE_FULL) {
        if (lv_display_is_double_buffered(disp_drv) && lv_display_flush_is_last(disp_drv)) {
            HAL_LTDC_SetAddress_NoReload(&hltdc, (uint32_t)color_p, LTDC_LAYER_1);
            __HAL_LTDC_ENABLE_IT(&hltdc, LTDC_IT_RR);
            HAL_LTDC_Reload(&hltdc, LTDC_RELOAD_VERTICAL_BLANKING);
        } else {
            lv_display_flush_ready(ltdc_obj->disp);
        }
    } else {
        int32_t width = lv_area_get_width(area);
        int32_t height = lv_area_get_height(area);
        uint8_t bpp = lv_color_format_get_size(ltdc_obj->color_format);
        // Destination: position (area->x1, area->y1) inside the LTDC framebuffer.
        // color_p contains width*height pixels compacted from index 0 (LVGL PARTIAL layout).
        uint32_t destination_addr = (uint32_t)ltdc_obj->fb[0] +
                                    ((area->y1 * ltdc_obj->width) + area->x1) * bpp;

        // Only the output-offset register needs to change between flush calls
        // (it depends on the dirty-rect width). Avoid full HAL_DMA2D_Init to
        // preserve the layer config written by config_dma2d(); just update OOR.
        hdma2d.Init.OutputOffset = ltdc_obj->width - width;
        WRITE_REG(hdma2d.Instance->OOR, hdma2d.Init.OutputOffset);

        HAL_DMA2D_Start_IT(&hdma2d, (uint32_t)color_p, destination_addr,
                           width, height);
    }
}

// HAL callback after DMA2D transfer completes.
void DMA2D_TransferComplete(DMA2D_HandleTypeDef *hdma2d) {
    if (MP_STATE_PORT(current_ltdc_obj) == MP_OBJ_NULL) {
        return;
    }
    ltdc_display_obj_t *ltdc_obj = MP_OBJ_TO_PTR(MP_STATE_PORT(current_ltdc_obj));
    if (ltdc_obj->disp == NULL) {
        return;  // display freed by lv.deinit()
    }
    lv_display_flush_ready(ltdc_obj->disp);
}

// HAL callback after LTDC vertical-blanking reload completes.
// Signals LVGL that the flush is done so the next frame can be rendered.
void HAL_LTDC_ReloadEventCallback(LTDC_HandleTypeDef *hltdc) {
    if (MP_STATE_PORT(current_ltdc_obj) == MP_OBJ_NULL) {
        return;
    }
    ltdc_display_obj_t *ltdc_obj = MP_OBJ_TO_PTR(MP_STATE_PORT(current_ltdc_obj));
    if (ltdc_obj->disp == NULL) {
        return;  // display freed by lv.deinit()
    }
    lv_display_flush_ready(ltdc_obj->disp);
}

static void display_delete_cb(lv_event_t *e) {
    (void)e;
    MP_STATE_PORT(current_ltdc_obj) = MP_OBJ_NULL;
}

// Initialize the LTDC peripheral, GPIO and framebuffers.
static mp_obj_t mp_ltdc_init(size_t n_args, const mp_obj_t *pos_args, mp_map_t *kw_args) {
    enum {
        ARG_SELF, ARG_LV_DISP,
    };

    static const mp_arg_t allowed_args[] = {
        { MP_QSTR_self, MP_ARG_REQUIRED | MP_ARG_OBJ, {.u_obj = MP_OBJ_NULL} },
        { MP_QSTR_disp, MP_ARG_REQUIRED | MP_ARG_OBJ, {.u_obj = MP_OBJ_NULL} },
    };

    // parse args
    mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all(n_args, pos_args, kw_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

    ltdc_display_obj_t *self = MP_OBJ_TO_PTR(args[ARG_SELF].u_obj);

    if (args[ARG_LV_DISP].u_obj != MP_OBJ_NULL) {
        // lv.display_create() returns an mp_lv_struct_t whose get_buffer
        // exposes &self->data (a pointer-to-pointer).  Use the standard
        // buffer protocol to read out the underlying lv_display_t *.
        mp_obj_t disp_obj = args[ARG_LV_DISP].u_obj;
        mp_buffer_info_t bufinfo;
        mp_get_buffer_raise(disp_obj, &bufinfo, MP_BUFFER_READ);
        if (bufinfo.len != sizeof(lv_display_t *)) {
            mp_raise_TypeError(MP_ERROR_TEXT("disp: expected lv_display_t pointer"));
        }
        memcpy(&self->disp, bufinfo.buf, sizeof(lv_display_t *));
    } else {
        mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("LVGL Display object is mandatory"));
    }

    // Update MP_STATE_PORT(current_ltdc_obj) immediately so any IRQ that fires between now
    // and the end of init uses the new (valid) Python object, not a dangling
    // pointer left over from a previous soft reset.
    MP_STATE_PORT(current_ltdc_obj) = MP_OBJ_FROM_PTR(self);
    lv_display_add_event_cb(self->disp, display_delete_cb, LV_EVENT_DELETE, self);

    self->color_format = lv_display_get_color_format(self->disp);

    optimize_axi_for_display();

    // Allocate both framebuffers before configuring the MPU so the
    // Write-Through region can be sized to cover them both.
    mp_ltdc_framebuffer(MP_OBJ_FROM_PTR(self), mp_obj_new_int(1));
    mp_ltdc_framebuffer(MP_OBJ_FROM_PTR(self), mp_obj_new_int(2));
    if (self->fb[0] == NULL || self->fb[1] == NULL) {
        mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("Failed allocating frame buffers"));
    }
    configure_fb_mpu_wt(self);
    if (self->bl_pin != MP_OBJ_NULL) {
        mp_hal_pin_high(self->bl_pin);
    } else if (self->bl_led > 0) {
        led_set_intensity(self->bl_led, 50);
    }
    lcd_hw_reset(self);
    if (!config_ltdc(self)) {
        mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("LTDC layer config error"));
    }
    if (!config_dma2d(self)) {
        mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("DMA2D init error"));
    }
    return mp_const_none;
}

// Detach from the display: turn off the backlight, blank the layer and
// unregister the current object so IRQ callbacks become no-ops.
static mp_obj_t mp_ltdc_deinit(mp_obj_t self_in) {
    ltdc_display_obj_t *self = MP_OBJ_TO_PTR(self_in);
    // Nothing to do if init() was never called or deinit() already ran.
    if (MP_STATE_PORT(current_ltdc_obj) == MP_OBJ_NULL) {
        return mp_const_none;
    }
    // Clear self->disp BEFORE clearing current_ltdc_obj so the IRQ callbacks
    // see disp==NULL and bail safely even if an interrupt fires between the
    // two stores (the disp==NULL guard is checked under current_ltdc_obj!=NULL).
    self->disp = NULL;
    // Now invalidate MP_STATE_PORT(current_ltdc_obj) so IRQ callbacks that fire after this
    // point are no-ops.
    MP_STATE_PORT(current_ltdc_obj) = MP_OBJ_NULL;
    if (self->bl_pin != MP_OBJ_NULL) {
        mp_hal_pin_low(self->bl_pin);
    } else if (self->bl_led > 0) {
        led_set_intensity(self->bl_led, 0);
    }
    // Blank the layer (alpha=0) so the panel goes dark without stopping clocks.
    // Use NoReload + VBL reload to avoid tearing on the final frame.
    HAL_LTDC_SetAlpha_NoReload(&hltdc, 0, LTDC_LAYER_1);
    HAL_LTDC_Reload(&hltdc, LTDC_RELOAD_VERTICAL_BLANKING);
    if (HAL_LTDC_DeInit(&hltdc) != HAL_OK) {
        mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("LTDC DeInit error"));
    }
    return mp_const_none;
}

// Toggle the LCD reset pin to perform a hardware reset.
static void lcd_hw_reset(ltdc_display_obj_t *self) {
    if (self->rst_pin == MP_OBJ_NULL) {
        return;
    }
    mp_hal_pin_low(self->rst_pin);
    mp_hal_delay_ms(100);
    mp_hal_pin_high(self->rst_pin);
    mp_hal_delay_ms(1);
}

// Configure the LTDC peripheral and Layer 1 with the stored timing parameters.
// This calls HAL_LTDC_Init() which triggers HAL_LTDC_MspInit() (clocks/GPIO/PLL3).
static bool config_ltdc(ltdc_display_obj_t *self) {
    LTDC_LayerCfgTypeDef layer_cfg = {0};

    if (self->width == 0 || self->height == 0 ||
        self->hsync == 0 || self->vsync == 0) {
        return false;
    }

    hltdc.Instance = LTDC;
    hltdc.Init.HSPolarity = (self->polarity & LTDC_POL_HS_MASK)
                                ? LTDC_HSPOLARITY_AH    // active high
                                : LTDC_HSPOLARITY_AL;   // active low
    hltdc.Init.VSPolarity = (self->polarity & LTDC_POL_VS_MASK)
                                ? LTDC_VSPOLARITY_AH
                                : LTDC_VSPOLARITY_AL;
    hltdc.Init.DEPolarity = (self->polarity & LTDC_POL_DE_MASK)
                                ? LTDC_DEPOLARITY_AH
                                : LTDC_DEPOLARITY_AL;
    hltdc.Init.PCPolarity = (self->polarity & LTDC_POL_PC_MASK)
                                ? LTDC_PCPOLARITY_IPC   // inverted
                                : LTDC_PCPOLARITY_IIPC; // not inverted
    // Horizontal timing
    hltdc.Init.HorizontalSync     = self->hsync - 1;
    hltdc.Init.AccumulatedHBP     = self->hsync + self->hbp - 1;
    hltdc.Init.AccumulatedActiveW = self->hsync + self->hbp + self->width - 1;
    hltdc.Init.TotalWidth         = self->hsync + self->hbp + self->width + self->hfp - 1;

    // Vertical timing
    hltdc.Init.VerticalSync       = self->vsync - 1;
    hltdc.Init.AccumulatedVBP     = self->vsync + self->vbp - 1;
    hltdc.Init.AccumulatedActiveH = self->vsync + self->vbp + self->height - 1;
    hltdc.Init.TotalHeigh         = self->vsync + self->vbp + self->height + self->vfp - 1;
    hltdc.Init.Backcolor.Blue = 0;
    hltdc.Init.Backcolor.Green = 0;
    hltdc.Init.Backcolor.Red = 0;
    if (HAL_LTDC_Init(&hltdc) != HAL_OK) {
        return false;
    }

    if (self->color_format == LV_COLOR_FORMAT_RGB565) {
        layer_cfg.PixelFormat = LTDC_PIXEL_FORMAT_RGB565;
    } else if (self->color_format == LV_COLOR_FORMAT_RGB888) {
        layer_cfg.PixelFormat = LTDC_PIXEL_FORMAT_RGB888;
    } else if (self->color_format == LV_COLOR_FORMAT_ARGB8888) {
        layer_cfg.PixelFormat = LTDC_PIXEL_FORMAT_ARGB8888;
    } else {
        return false;
    }

    layer_cfg.WindowX0 = 0;
    layer_cfg.WindowX1 = self->width;
    layer_cfg.WindowY0 = 0;
    layer_cfg.WindowY1 = self->height;
    layer_cfg.FBStartAdress = (uint32_t)self->fb[0];
    layer_cfg.Alpha = 255;
    layer_cfg.Alpha0 = 0;
    layer_cfg.Backcolor.Blue = 0;
    layer_cfg.Backcolor.Green = 0;
    layer_cfg.Backcolor.Red = 0;
    layer_cfg.BlendingFactor1 = LTDC_BLENDING_FACTOR1_CA;
    layer_cfg.BlendingFactor2 = LTDC_BLENDING_FACTOR2_CA;
    layer_cfg.ImageWidth = self->width;
    layer_cfg.ImageHeight = self->height;

    if (HAL_LTDC_ConfigLayer(&hltdc, &layer_cfg, LTDC_LAYER_1) != HAL_OK) {
        mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("LTDC layer config failed"));
        return false;
    }

    return true;
}

// Configure the DMA2D peripheral.
static bool config_dma2d(ltdc_display_obj_t *self) {
    uint32_t out_color_mode;
    uint32_t in_color_mode;

    if (self->color_format == LV_COLOR_FORMAT_RGB565) {
        out_color_mode = DMA2D_OUTPUT_RGB565;
        in_color_mode = DMA2D_INPUT_RGB565;
    } else if (self->color_format == LV_COLOR_FORMAT_RGB888) {
        out_color_mode = DMA2D_OUTPUT_RGB888;
        in_color_mode = DMA2D_INPUT_RGB888;
    } else if (self->color_format == LV_COLOR_FORMAT_ARGB8888) {
        out_color_mode = DMA2D_OUTPUT_ARGB8888;
        in_color_mode = DMA2D_INPUT_ARGB8888;
    } else {
        return false;
    }

    hdma2d.Instance = DMA2D;
    hdma2d.Init.Mode = DMA2D_M2M;
    hdma2d.Init.ColorMode = out_color_mode;
    hdma2d.Init.OutputOffset = 0x0;
    hdma2d.Init.BytesSwap = DMA2D_BYTES_REGULAR;
    hdma2d.Init.LineOffsetMode = DMA2D_LOM_PIXELS;
    hdma2d.LayerCfg[1].AlphaMode = DMA2D_NO_MODIF_ALPHA;
    hdma2d.LayerCfg[1].InputAlpha = 0x0;
    hdma2d.LayerCfg[1].InputColorMode = in_color_mode;
    hdma2d.LayerCfg[1].InputOffset = 0x0;
    hdma2d.LayerCfg[1].AlphaInverted = DMA2D_REGULAR_ALPHA;
    hdma2d.LayerCfg[1].RedBlueSwap = DMA2D_RB_REGULAR;
    hdma2d.LayerCfg[1].ChromaSubSampling = DMA2D_NO_CSS;

    hdma2d.XferCpltCallback = DMA2D_TransferComplete;
    if (HAL_DMA2D_Init(&hdma2d) != HAL_OK) {
        return false;
    }
    HAL_DMA2D_ConfigLayer(&hdma2d, 1);
    return true;
}

void HAL_DMA2D_MspInit(DMA2D_HandleTypeDef *hdma2d) {
    __HAL_RCC_DMA2D_CLK_ENABLE();
    HAL_NVIC_SetPriority(DMA2D_IRQn, 1, 1);
    HAL_NVIC_EnableIRQ(DMA2D_IRQn);
}

void HAL_DMA2D_MspDeInit(DMA2D_HandleTypeDef *hdma2d) {
    HAL_NVIC_DisableIRQ(DMA2D_IRQn);
    __HAL_RCC_DMA2D_CLK_DISABLE();
}

// LTDC interrupt handler, forwarded to the HAL.
void LTDC_IRQHandler(void) {
    HAL_LTDC_IRQHandler(&hltdc);
}

// DMA2D interrupt handler, forwarded to the HAL.
void DMA2D_IRQHandler(void) {
    HAL_DMA2D_IRQHandler(&hdma2d);
}
