// LTDC display BSP driver for FK743M5-XIH6 board.

#include <stdint.h>
#include <string.h>
#include <stddef.h>
#include <stdbool.h>
#include "boardctrl.h"
#include <stm32h7xx_hal.h>

// HAL MSP initialization for the LTDC peripheral.
// Configures PLL3 for the pixel clock, enables GPIO clocks and maps
// the LTDC alternate-function pins.
void HAL_LTDC_MspInit(LTDC_HandleTypeDef *ltdc_handle) {
    GPIO_InitTypeDef gpio = {0};

    RCC_PeriphCLKInitTypeDef PeriphClkInitStruct = {0};
    PeriphClkInitStruct.PeriphClockSelection = RCC_PERIPHCLK_LTDC;
    PeriphClkInitStruct.PLL3.PLL3M = 5;
    PeriphClkInitStruct.PLL3.PLL3N = 40;
    PeriphClkInitStruct.PLL3.PLL3P = 2;
    PeriphClkInitStruct.PLL3.PLL3Q = 4;
    PeriphClkInitStruct.PLL3.PLL3R = 4;
    PeriphClkInitStruct.PLL3.PLL3RGE = RCC_PLL3VCIRANGE_2;
    PeriphClkInitStruct.PLL3.PLL3VCOSEL = RCC_PLL3VCOWIDE;
    PeriphClkInitStruct.PLL3.PLL3FRACN = 0;

    if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInitStruct) != HAL_OK) {
        boardctrl_fatal_error("HAL_LTDC_MspInit()");
    }

    if (ltdc_handle->Instance == LTDC) {
        // LTDC and GPIO clock enable
        __HAL_RCC_GPIOG_CLK_ENABLE();
        __HAL_RCC_GPIOH_CLK_ENABLE();
        __HAL_RCC_GPIOI_CLK_ENABLE();
        __HAL_RCC_GPIOJ_CLK_ENABLE();
        __HAL_RCC_GPIOK_CLK_ENABLE();
        __HAL_RCC_LTDC_CLK_ENABLE();
        // Common settings for all LTDC data/sync/clk pins
        gpio.Mode      = GPIO_MODE_AF_PP;
        gpio.Pull      = GPIO_NOPULL;
        gpio.Speed     = GPIO_SPEED_FREQ_HIGH;

        // GPIOG: G3 = LCD_G3
        gpio.Pin = GPIO_PIN_10;           // PG10 = LCD_G3
        gpio.Alternate = GPIO_AF9_LTDC;
        HAL_GPIO_Init(GPIOG, &gpio);

        // GPIOH: PH4=G5
        gpio.Pin = GPIO_PIN_4;
        gpio.Alternate = GPIO_AF9_LTDC;
        HAL_GPIO_Init(GPIOH, &gpio);

        // GPIOH: PH15=G4
        gpio.Pin = GPIO_PIN_15;
        gpio.Alternate = GPIO_AF14_LTDC;
        HAL_GPIO_Init(GPIOH, &gpio);

        // GPIOI: PI12=HSYNC PI13=VSYNC PI14=CLK PI15=R0
        gpio.Pin = GPIO_PIN_12 | GPIO_PIN_13 | GPIO_PIN_14 | GPIO_PIN_15;
        gpio.Alternate = GPIO_AF14_LTDC;
        HAL_GPIO_Init(GPIOI, &gpio);

        // GPIOJ: PJ0..PJ9 and PJ12..PJ15
        //   R1=PJ0  R2=PJ1  R3=PJ2  R4=PJ3  R5=PJ4  R6=PJ5  R7=PJ6
        //   G0=PJ7  G1=PJ8  G2=PJ9
        //   B0=PJ12 B1=PJ13 B2=PJ14 B3=PJ15
        gpio.Pin = GPIO_PIN_0  | GPIO_PIN_1  | GPIO_PIN_2  | GPIO_PIN_3  |
                   GPIO_PIN_4  | GPIO_PIN_5  | GPIO_PIN_6  | GPIO_PIN_7  |
                   GPIO_PIN_8  | GPIO_PIN_9  |
                   GPIO_PIN_12 | GPIO_PIN_13 | GPIO_PIN_14 | GPIO_PIN_15;
        HAL_GPIO_Init(GPIOJ, &gpio);

        // GPIOK: PK1=G6  PK2=G7  PK3=B4  PK4=B5  PK5=B6  PK6=B7  PK7=DE
        gpio.Pin = GPIO_PIN_1 | GPIO_PIN_2 | GPIO_PIN_3 |
                   GPIO_PIN_4 | GPIO_PIN_5 | GPIO_PIN_6 | GPIO_PIN_7;
        HAL_GPIO_Init(GPIOK, &gpio);
        // LTDC interrupt
        HAL_NVIC_SetPriority(LTDC_IRQn, 5, 0);
        HAL_NVIC_EnableIRQ(LTDC_IRQn);
    }
}

// HAL MSP de-initialization for the LTDC peripheral.
// Resets the LTDC block, disables its clock and de-initializes all
// associated GPIO pins.
void HAL_LTDC_MspDeInit(LTDC_HandleTypeDef *ltdc_handle) {
    if (ltdc_handle->Instance == LTDC) {
        __HAL_RCC_LTDC_FORCE_RESET();
        __HAL_RCC_LTDC_RELEASE_RESET();
        HAL_NVIC_DisableIRQ(LTDC_IRQn);
        __HAL_RCC_LTDC_CLK_DISABLE();
        HAL_GPIO_DeInit(GPIOG, GPIO_PIN_10);
        HAL_GPIO_DeInit(GPIOH, GPIO_PIN_4 | GPIO_PIN_15);
        HAL_GPIO_DeInit(GPIOI, GPIO_PIN_12 | GPIO_PIN_13 | GPIO_PIN_14 | GPIO_PIN_15);
        HAL_GPIO_DeInit(GPIOJ, GPIO_PIN_0  | GPIO_PIN_1  | GPIO_PIN_2  | GPIO_PIN_3  |
                              GPIO_PIN_4  | GPIO_PIN_5  | GPIO_PIN_6  | GPIO_PIN_7  |
                              GPIO_PIN_8  | GPIO_PIN_9  |
                              GPIO_PIN_12 | GPIO_PIN_13 | GPIO_PIN_14 | GPIO_PIN_15);
        HAL_GPIO_DeInit(GPIOK, GPIO_PIN_1 | GPIO_PIN_2 | GPIO_PIN_3 |
                              GPIO_PIN_4 | GPIO_PIN_5 | GPIO_PIN_6 | GPIO_PIN_7);
    }
}


