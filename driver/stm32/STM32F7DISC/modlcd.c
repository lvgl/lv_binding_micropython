#include "py/runtime.h"
#include "py/mphal.h"
#include "softtimer.h"
#include <stdint.h>
#include <stdbool.h>
#include "../../../lvgl/lvgl.h"
#include "../../include/common.h"

#define LV_TICK_RATE 30

#define  RK043FN48H_WIDTH		((uint16_t)480)
#define  RK043FN48H_HEIGHT   		((uint16_t)272)
#define  RK043FN48H_HSYNC            	((uint16_t)41)
#define  RK043FN48H_HBP              	((uint16_t)13)
#define  RK043FN48H_HFP              	((uint16_t)32)
#define  RK043FN48H_VSYNC            	((uint16_t)10)
#define  RK043FN48H_VBP              	((uint16_t)2)
#define  RK043FN48H_VFP              	((uint16_t)2)
#define  RK043FN48H_FREQUENCY_DIVIDER   5

#define LCD_DISP_PIN                    GPIO_PIN_12
#define LCD_DISP_GPIO_PORT              GPIOI
#define LCD_DISP_GPIO_CLK_ENABLE()      __HAL_RCC_GPIOI_CLK_ENABLE()
#define LCD_DISP_GPIO_CLK_DISABLE()     __HAL_RCC_GPIOI_CLK_DISABLE()
#define LCD_BL_CTRL_PIN                  GPIO_PIN_3
#define LCD_BL_CTRL_GPIO_PORT            GPIOK
#define LCD_BL_CTRL_GPIO_CLK_ENABLE()    __HAL_RCC_GPIOK_CLK_ENABLE()
#define LCD_BL_CTRL_GPIO_CLK_DISABLE()   __HAL_RCC_GPIOK_CLK_DISABLE()

#define DMA2D_TO	10

static soft_timer_entry_t *modLTC_timer = NULL;
static LTDC_HandleTypeDef *hltdc = NULL;
static DMA2D_HandleTypeDef *hdma2d = NULL;
lv_color_t* fb = NULL;
uint32_t w, h;

static bool config_ltdc(void);
static bool config_dma2d(void);

STATIC mp_obj_t mp_lv_task_handler(mp_obj_t arg)
{  
	lv_tick_inc(LV_TICK_RATE);
    lv_task_handler();
    return mp_const_none;
}

STATIC MP_DEFINE_CONST_FUN_OBJ_1(mp_lv_task_handler_obj, mp_lv_task_handler);


STATIC mp_obj_t mp_init_lcd(size_t n_args, const mp_obj_t *pos_args, mp_map_t *kw_args)
{
    enum { ARG_w, ARG_h };
    static const mp_arg_t allowed_args[] = {
        { MP_QSTR_w, MP_ARG_KW_ONLY | MP_ARG_INT, {.u_int = LV_HOR_RES_MAX} },
        { MP_QSTR_h, MP_ARG_KW_ONLY | MP_ARG_INT, {.u_int = LV_VER_RES_MAX} },
    };

    // parse args
    mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all(n_args, pos_args, kw_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

    w = args[ARG_w].u_int;
	h = args[ARG_h].u_int;

    if(modLTC_timer) return mp_const_none;
    
    modLTC_timer = m_new_obj(soft_timer_entry_t);
    modLTC_timer->mode = SOFT_TIMER_MODE_PERIODIC;
    modLTC_timer->delta_ms = LV_TICK_RATE;
    modLTC_timer->expiry_ms = mp_hal_ticks_ms() + modLTC_timer->delta_ms;
    modLTC_timer->callback = (mp_obj_t)&mp_lv_task_handler_obj;
    soft_timer_insert(modLTC_timer);

    fb = (lv_color_t*) m_malloc(sizeof(lv_color_t)*w*h);

    if(fb == NULL)
    	printf("ltdc error: frame buffer alloc\r\n");

    if(!config_ltdc())
    	printf("ltdc error: initr\r\n");

    if(!config_dma2d())
    	printf("ltdc error: DMA2D init\r\n");

    return mp_const_none;
}

STATIC mp_obj_t mp_deinit_lcd()
{
    soft_timer_remove(modLTC_timer);
	modLTC_timer = NULL;

	if(hdma2d)
	{
		HAL_DMA2D_DeInit(hdma2d);
		hdma2d = NULL;
	}

	if(hltdc)
	{
		HAL_LTDC_DeInit(hltdc);
		HAL_GPIO_WritePin(LCD_DISP_GPIO_PORT, LCD_DISP_PIN, GPIO_PIN_RESET);
		HAL_GPIO_WritePin(LCD_BL_CTRL_GPIO_PORT, LCD_BL_CTRL_PIN, GPIO_PIN_RESET);
		hltdc = NULL;
		m_free(fb);
		fb = NULL;
	}

    return mp_const_none;
}

STATIC void mp_flush(struct _disp_drv_t * disp_drv, const lv_area_t * area, lv_color_t * color_p)
{
	hdma2d->Init.Mode = DMA2D_M2M;

	if(HAL_DMA2D_Init(hdma2d) == HAL_OK){
		HAL_DMA2D_ConfigLayer(hdma2d, 1);
		lv_color_t* fb_p = fb + area->x1 + area->y1*w;
		lv_coord_t area_w = lv_area_get_width(area);
		SCB_CleanInvalidateDCache();

		uint32_t i;
		for(i = area->y1; i <= area->y2; i++) {
			HAL_DMA2D_Start(hdma2d, (uint32_t) color_p, (uint32_t) fb_p, area_w, 1);
			fb_p += w;
			color_p += area_w;
			if(HAL_DMA2D_PollForTransfer(hdma2d, DMA2D_TO)!= HAL_OK)
				break;
		}
	}
	lv_disp_flush_ready(disp_drv);
}

STATIC void mp_gpu_blend(lv_disp_drv_t * drv, lv_color_t * dest, const lv_color_t * src, uint32_t length, lv_opa_t opa)
{
	hdma2d->Init.Mode = DMA2D_M2M_BLEND;

	if(HAL_DMA2D_Init(hdma2d) == HAL_OK){
		hdma2d->LayerCfg[1].InputAlpha = opa;
		HAL_DMA2D_ConfigLayer(hdma2d, 1);
		SCB_CleanInvalidateDCache();
		HAL_DMA2D_BlendingStart(hdma2d, (uint32_t) src, (uint32_t) dest, (uint32_t) dest, length, 1);
		HAL_DMA2D_PollForTransfer(hdma2d, DMA2D_TO);
	}
}

STATIC void mp_gpu_fill(lv_disp_drv_t * disp_drv, lv_color_t * dest_buf, lv_coord_t dest_width, const lv_area_t * fill_area, lv_color_t color)
{
	hdma2d->Init.Mode = DMA2D_R2M;

	if(HAL_DMA2D_Init(hdma2d) == HAL_OK){
		HAL_DMA2D_ConfigLayer(hdma2d, 1);
		dest_buf +=  fill_area->x1 + dest_width * fill_area->y1;
		lv_coord_t area_w = lv_area_get_width(fill_area);
		SCB_CleanInvalidateDCache();

		uint32_t i;
		for(i = fill_area->y1; i <= fill_area->y2; i++) {
			HAL_DMA2D_Start(hdma2d, lv_color_to32(color), (uint32_t) dest_buf, area_w, 1);
			dest_buf += dest_width;
			if(HAL_DMA2D_PollForTransfer(hdma2d, DMA2D_TO) != HAL_OK)
				break;
		}
	}
}

STATIC MP_DEFINE_CONST_FUN_OBJ_KW(mp_init_lcd_obj, 0, mp_init_lcd);
STATIC MP_DEFINE_CONST_FUN_OBJ_0(mp_deinit_lcd_obj, mp_deinit_lcd);

DEFINE_PTR_OBJ(mp_flush);
DEFINE_PTR_OBJ(mp_gpu_blend);
DEFINE_PTR_OBJ(mp_gpu_fill);

STATIC const mp_rom_map_elem_t lcd_globals_table[] = {
        { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_lcd) },
        { MP_ROM_QSTR(MP_QSTR_init), MP_ROM_PTR(&mp_init_lcd_obj) },
        { MP_ROM_QSTR(MP_QSTR_deinit), MP_ROM_PTR(&mp_deinit_lcd_obj) },
        { MP_ROM_QSTR(MP_QSTR_flush), MP_ROM_PTR(&PTR_OBJ(mp_flush))},
		{ MP_ROM_QSTR(MP_QSTR_gpu_blend), MP_ROM_PTR(&PTR_OBJ(mp_gpu_blend))},
		{ MP_ROM_QSTR(MP_QSTR_gpu_fill), MP_ROM_PTR(&PTR_OBJ(mp_gpu_fill))},
};
         

STATIC MP_DEFINE_CONST_DICT (
    mp_module_lcd_globals,
    lcd_globals_table
);

const mp_obj_module_t mp_module_lcd = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&mp_module_lcd_globals
};

MP_REGISTER_MODULE(MP_QSTR_lcd, mp_module_lcd, 1);

static bool config_ltdc(void)
{
	RCC_PeriphCLKInitTypeDef  PeriphClkInitStruct;
	static LTDC_HandleTypeDef hltdc_F={0};
	LTDC_LayerCfgTypeDef      pLayerCfg={0};

	PeriphClkInitStruct.PeriphClockSelection = RCC_PERIPHCLK_LTDC;
	PeriphClkInitStruct.PLLSAI.PLLSAIN = 192;
	PeriphClkInitStruct.PLLSAI.PLLSAIR = RK043FN48H_FREQUENCY_DIVIDER;
	PeriphClkInitStruct.PLLSAIDivR = RCC_PLLSAIDIVR_4;
	if(HAL_RCCEx_PeriphCLKConfig(&PeriphClkInitStruct)!=HAL_OK)
		return false;

	hltdc_F.Init.HSPolarity = LTDC_HSPOLARITY_AL;
	hltdc_F.Init.VSPolarity = LTDC_VSPOLARITY_AL;
	hltdc_F.Init.DEPolarity = LTDC_DEPOLARITY_AL;
	hltdc_F.Init.PCPolarity = LTDC_PCPOLARITY_IPC;
	hltdc_F.Init.HorizontalSync = (RK043FN48H_HSYNC - 1);
	hltdc_F.Init.VerticalSync = (RK043FN48H_VSYNC - 1);
	hltdc_F.Init.AccumulatedHBP = (RK043FN48H_HSYNC + RK043FN48H_HBP - 1);
	hltdc_F.Init.AccumulatedVBP = (RK043FN48H_VSYNC + RK043FN48H_VBP - 1);
	hltdc_F.Init.AccumulatedActiveH = (RK043FN48H_HEIGHT + RK043FN48H_VSYNC + RK043FN48H_VBP - 1);
	hltdc_F.Init.AccumulatedActiveW = (RK043FN48H_WIDTH + RK043FN48H_HSYNC + RK043FN48H_HBP - 1);
	hltdc_F.Init.TotalHeigh = (RK043FN48H_HEIGHT + RK043FN48H_VSYNC + RK043FN48H_VBP + RK043FN48H_VFP - 1);
	hltdc_F.Init.TotalWidth = (RK043FN48H_WIDTH + RK043FN48H_HSYNC + RK043FN48H_HBP + RK043FN48H_HFP - 1);
	hltdc_F.Init.Backcolor.Blue = 0;
	hltdc_F.Init.Backcolor.Green = 0;
	hltdc_F.Init.Backcolor.Red = 0;
	hltdc_F.Instance = LTDC;

	pLayerCfg.WindowX0 = 0;
	pLayerCfg.WindowX1 = w;
	pLayerCfg.WindowY0 = 0;
	pLayerCfg.WindowY1 = h;
	pLayerCfg.PixelFormat = (sizeof(lv_color_t)==4)?LTDC_PIXEL_FORMAT_ARGB8888:LTDC_PIXEL_FORMAT_RGB565;
	pLayerCfg.FBStartAdress = (uint32_t) fb;
	pLayerCfg.Alpha = 255;
	pLayerCfg.Alpha0 = 0;
	pLayerCfg.Backcolor.Blue = 0;
	pLayerCfg.Backcolor.Green = 0;
	pLayerCfg.Backcolor.Red = 0;
	pLayerCfg.BlendingFactor1 = LTDC_BLENDING_FACTOR1_CA;
	pLayerCfg.BlendingFactor2 = LTDC_BLENDING_FACTOR2_CA;
	pLayerCfg.ImageWidth  = w;
	pLayerCfg.ImageHeight = h;

	hltdc = &hltdc_F;

	if(HAL_LTDC_Init(hltdc) != HAL_OK)
		return false;

	if(HAL_LTDC_ConfigLayer(hltdc, &pLayerCfg, 1) != HAL_OK)
		return false;

	return true;
}

static bool config_dma2d(void)
{
	static DMA2D_HandleTypeDef Dma2dHandle={0};

	Dma2dHandle.Init.Mode = DMA2D_M2M_BLEND;
	Dma2dHandle.Init.ColorMode = (sizeof(lv_color_t)==4)?DMA2D_INPUT_ARGB8888:DMA2D_INPUT_RGB565;
	Dma2dHandle.Init.OutputOffset = 0x0;
	Dma2dHandle.LayerCfg[1].AlphaMode = DMA2D_REPLACE_ALPHA;
	Dma2dHandle.LayerCfg[1].InputAlpha = 0xFF;
	Dma2dHandle.LayerCfg[1].InputColorMode = (sizeof(lv_color_t)==4)?DMA2D_INPUT_ARGB8888:DMA2D_INPUT_RGB565;
	Dma2dHandle.LayerCfg[1].InputOffset = 0x0;
	Dma2dHandle.LayerCfg[0].AlphaMode = DMA2D_REPLACE_ALPHA;
	Dma2dHandle.LayerCfg[0].InputAlpha = 0xFF;
	Dma2dHandle.LayerCfg[0].InputColorMode = (sizeof(lv_color_t)==4)?DMA2D_INPUT_ARGB8888:DMA2D_INPUT_RGB565;
	Dma2dHandle.LayerCfg[0].InputOffset = 0x0;
	Dma2dHandle.Instance   = DMA2D;

	if(HAL_DMA2D_Init(&Dma2dHandle) != HAL_OK)
		return false;

	hdma2d = &Dma2dHandle;

	HAL_DMA2D_ConfigLayer(&Dma2dHandle, 0);
	HAL_DMA2D_ConfigLayer(&Dma2dHandle, 1);

	return true;
}

void HAL_LTDC_MspInit(LTDC_HandleTypeDef *hltdc)
{
	GPIO_InitTypeDef GPIO_Init_Structure;

	__HAL_RCC_LTDC_CLK_ENABLE();
	__HAL_RCC_GPIOE_CLK_ENABLE();
	__HAL_RCC_GPIOG_CLK_ENABLE();
	__HAL_RCC_GPIOI_CLK_ENABLE();
	__HAL_RCC_GPIOJ_CLK_ENABLE();
	__HAL_RCC_GPIOK_CLK_ENABLE();

	GPIO_Init_Structure.Pin       = GPIO_PIN_4;
	GPIO_Init_Structure.Mode      = GPIO_MODE_AF_PP;
	GPIO_Init_Structure.Pull      = GPIO_NOPULL;
	GPIO_Init_Structure.Speed     = GPIO_SPEED_FAST;
	GPIO_Init_Structure.Alternate = GPIO_AF14_LTDC;
	HAL_GPIO_Init(GPIOE, &GPIO_Init_Structure);

	GPIO_Init_Structure.Pin       = GPIO_PIN_12;
	GPIO_Init_Structure.Mode      = GPIO_MODE_AF_PP;
	GPIO_Init_Structure.Alternate = GPIO_AF9_LTDC;
	HAL_GPIO_Init(GPIOG, &GPIO_Init_Structure);

	GPIO_Init_Structure.Pin       = GPIO_PIN_9 | GPIO_PIN_10 | \
			GPIO_PIN_14 | GPIO_PIN_15;
	GPIO_Init_Structure.Mode      = GPIO_MODE_AF_PP;
	GPIO_Init_Structure.Alternate = GPIO_AF14_LTDC;
	HAL_GPIO_Init(GPIOI, &GPIO_Init_Structure);

	GPIO_Init_Structure.Pin       = GPIO_PIN_0 | GPIO_PIN_1 | GPIO_PIN_2 | GPIO_PIN_3 | \
			GPIO_PIN_4 | GPIO_PIN_5 | GPIO_PIN_6 | GPIO_PIN_7 | \
			GPIO_PIN_8 | GPIO_PIN_9 | GPIO_PIN_10 | GPIO_PIN_11 | \
			GPIO_PIN_13 | GPIO_PIN_14 | GPIO_PIN_15;
	GPIO_Init_Structure.Mode      = GPIO_MODE_AF_PP;
	GPIO_Init_Structure.Alternate = GPIO_AF14_LTDC;
	HAL_GPIO_Init(GPIOJ, &GPIO_Init_Structure);

	GPIO_Init_Structure.Pin       = GPIO_PIN_0 | GPIO_PIN_1 | GPIO_PIN_2 | GPIO_PIN_4 | \
			GPIO_PIN_5 | GPIO_PIN_6 | GPIO_PIN_7;
	GPIO_Init_Structure.Mode      = GPIO_MODE_AF_PP;
	GPIO_Init_Structure.Alternate = GPIO_AF14_LTDC;
	HAL_GPIO_Init(GPIOK, &GPIO_Init_Structure);

	GPIO_Init_Structure.Pin       = GPIO_PIN_12;
	GPIO_Init_Structure.Mode      = GPIO_MODE_OUTPUT_PP;
	HAL_GPIO_Init(GPIOI, &GPIO_Init_Structure);

	GPIO_Init_Structure.Pin       = GPIO_PIN_3;
	GPIO_Init_Structure.Mode      = GPIO_MODE_OUTPUT_PP;
	HAL_GPIO_Init(GPIOK, &GPIO_Init_Structure);

	HAL_GPIO_WritePin(LCD_DISP_GPIO_PORT, LCD_DISP_PIN, GPIO_PIN_SET);
	HAL_GPIO_WritePin(LCD_BL_CTRL_GPIO_PORT, LCD_BL_CTRL_PIN, GPIO_PIN_SET);
}


void HAL_LTDC_MspDeInit(LTDC_HandleTypeDef *hltdc)
{
	__HAL_RCC_LTDC_FORCE_RESET();
	__HAL_RCC_LTDC_RELEASE_RESET();
}


void HAL_DMA2D_MspInit(DMA2D_HandleTypeDef *hdma2d)
{
	__HAL_RCC_DMA2D_CLK_ENABLE();

	//HAL_NVIC_SetPriority(DMA2D_IRQn, 0, 0);
	//HAL_NVIC_EnableIRQ(DMA2D_IRQn);
}

