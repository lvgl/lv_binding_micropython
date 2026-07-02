// LTDC display BSP driver for DEV190806042 board.

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
        __HAL_RCC_GPIOI_CLK_ENABLE();
        __HAL_RCC_GPIOJ_CLK_ENABLE();
        __HAL_RCC_GPIOK_CLK_ENABLE();
        __HAL_RCC_LTDC_CLK_ENABLE();
        // Common settings for all LTDC data/sync/clk pins
        gpio.Mode      = GPIO_MODE_AF_PP;
        gpio.Pull      = GPIO_NOPULL;
        gpio.Speed     = GPIO_SPEED_FREQ_VERY_HIGH;
        gpio.Alternate = GPIO_AF14_LTDC;

        // Port I: CLK, HSYNC, VSYNC, R0
        //   PI12 = LTDC_HSYNC
        //   PI13 = LTDC_VSYNC
        //   PI14 = LTDC_CLK
        //   PI15 = LTDC_R0
        gpio.Pin = GPIO_PIN_12 | GPIO_PIN_13 | GPIO_PIN_14 | GPIO_PIN_15;
        HAL_GPIO_Init(GPIOI, &gpio);

        // Port J: R1-R7, G0-G4, B0-B3 (PJ0-PJ15, all 16 pins)
        //   PJ0  = LTDC_R1    PJ1  = LTDC_R2    PJ2  = LTDC_R3
        //   PJ3  = LTDC_R4    PJ4  = LTDC_R5    PJ5  = LTDC_R6
        //   PJ6  = LTDC_R7
        //   PJ7  = LTDC_G0    PJ8  = LTDC_G1    PJ9  = LTDC_G2
        //   PJ10 = LTDC_G3    PJ11 = LTDC_G4
        //   PJ12 = LTDC_B0    PJ13 = LTDC_B1    PJ14 = LTDC_B2
        //   PJ15 = LTDC_B3
        gpio.Pin = GPIO_PIN_0  | GPIO_PIN_1  | GPIO_PIN_2  | GPIO_PIN_3  |
                   GPIO_PIN_4  | GPIO_PIN_5  | GPIO_PIN_6  | GPIO_PIN_7  |
                   GPIO_PIN_8  | GPIO_PIN_9  | GPIO_PIN_10 | GPIO_PIN_11 |
                   GPIO_PIN_12 | GPIO_PIN_13 | GPIO_PIN_14 | GPIO_PIN_15;
        HAL_GPIO_Init(GPIOJ, &gpio);

        // Port K: G5-G7, B4-B7, DE (PK0-PK7)
        //   PK0 = LTDC_G5    PK1 = LTDC_G6    PK2 = LTDC_G7
        //   PK3 = LTDC_B4    PK4 = LTDC_B5    PK5 = LTDC_B6
        //   PK6 = LTDC_B7    PK7 = LTDC_DE
        gpio.Pin = GPIO_PIN_0 | GPIO_PIN_1 | GPIO_PIN_2 | GPIO_PIN_3 |
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
        // De-init Port I LTDC pins
        HAL_GPIO_DeInit(GPIOI, GPIO_PIN_12 | GPIO_PIN_13 |
                               GPIO_PIN_14 | GPIO_PIN_15);

        // De-init Port J - all 16 LTDC pins
        HAL_GPIO_DeInit(GPIOJ, GPIO_PIN_0  | GPIO_PIN_1  | GPIO_PIN_2  | GPIO_PIN_3  |
                               GPIO_PIN_4  | GPIO_PIN_5  | GPIO_PIN_6  | GPIO_PIN_7  |
                               GPIO_PIN_8  | GPIO_PIN_9  | GPIO_PIN_10 | GPIO_PIN_11 |
                               GPIO_PIN_12 | GPIO_PIN_13 | GPIO_PIN_14 | GPIO_PIN_15);

        // De-init Port K LTDC pins
        HAL_GPIO_DeInit(GPIOK, GPIO_PIN_0 | GPIO_PIN_1 | GPIO_PIN_2 | GPIO_PIN_3 |
                               GPIO_PIN_4 | GPIO_PIN_5 | GPIO_PIN_6 | GPIO_PIN_7);
    }
}


