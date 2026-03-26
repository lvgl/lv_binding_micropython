// LTDC display BSP driver for STM32H7_CORE boards.

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
    GPIO_InitTypeDef GPIO_InitStruct = {0};

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
        __HAL_RCC_LTDC_CLK_ENABLE();
        __HAL_RCC_GPIOD_CLK_ENABLE();
        __HAL_RCC_GPIOI_CLK_ENABLE();
        __HAL_RCC_GPIOE_CLK_ENABLE();
        __HAL_RCC_GPIOF_CLK_ENABLE();
        __HAL_RCC_GPIOH_CLK_ENABLE();
        __HAL_RCC_GPIOG_CLK_ENABLE();
        __HAL_RCC_GPIOA_CLK_ENABLE();

        GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
        GPIO_InitStruct.Pull = GPIO_NOPULL;
        GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;

        GPIO_InitStruct.Pin = GPIO_PIN_9 | GPIO_PIN_10 | GPIO_PIN_0 | GPIO_PIN_1
                              | GPIO_PIN_2 | GPIO_PIN_5 | GPIO_PIN_6 | GPIO_PIN_7;
        GPIO_InitStruct.Alternate = GPIO_AF14_LTDC;
        HAL_GPIO_Init(GPIOI, &GPIO_InitStruct);

        GPIO_InitStruct.Pin = GPIO_PIN_10;
        GPIO_InitStruct.Alternate = GPIO_AF14_LTDC;
        HAL_GPIO_Init(GPIOF, &GPIO_InitStruct);

        GPIO_InitStruct.Pin = GPIO_PIN_9 | GPIO_PIN_10 | GPIO_PIN_11 | GPIO_PIN_12
                              | GPIO_PIN_13 | GPIO_PIN_15;
        GPIO_InitStruct.Alternate = GPIO_AF14_LTDC;
        HAL_GPIO_Init(GPIOH, &GPIO_InitStruct);

        GPIO_InitStruct.Pin = GPIO_PIN_6 | GPIO_PIN_7;
        GPIO_InitStruct.Alternate = GPIO_AF14_LTDC;
        HAL_GPIO_Init(GPIOG, &GPIO_InitStruct);

        GPIO_InitStruct.Pin = GPIO_PIN_8;
        GPIO_InitStruct.Alternate = GPIO_AF13_LTDC;
        HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

#if defined(BOARD_V10)
        GPIO_InitStruct.Pin = GPIO_PIN_10 | GPIO_PIN_12;
        GPIO_InitStruct.Alternate = GPIO_AF9_LTDC;
        HAL_GPIO_Init(GPIOG, &GPIO_InitStruct);
#else
        GPIO_InitStruct.Pin = GPIO_PIN_2;
        GPIO_InitStruct.Alternate = GPIO_AF14_LTDC;
        HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

        GPIO_InitStruct.Pin = GPIO_PIN_5 | GPIO_PIN_6;
        GPIO_InitStruct.Alternate = GPIO_AF14_LTDC;
        HAL_GPIO_Init(GPIOE, &GPIO_InitStruct);

        GPIO_InitStruct.Pin = GPIO_PIN_6;
        GPIO_InitStruct.Alternate = GPIO_AF14_LTDC;
        HAL_GPIO_Init(GPIOD, &GPIO_InitStruct);

        GPIO_InitStruct.Pin = GPIO_PIN_4 | GPIO_PIN_14;
        GPIO_InitStruct.Alternate = GPIO_AF14_LTDC;
        HAL_GPIO_Init(GPIOH, &GPIO_InitStruct);

        GPIO_InitStruct.Pin = GPIO_PIN_12 | GPIO_PIN_13 | GPIO_PIN_14;
        GPIO_InitStruct.Alternate = GPIO_AF14_LTDC;
        HAL_GPIO_Init(GPIOG, &GPIO_InitStruct);

        GPIO_InitStruct.Pin = GPIO_PIN_4;
        GPIO_InitStruct.Alternate = GPIO_AF14_LTDC;
        HAL_GPIO_Init(GPIOI, &GPIO_InitStruct);
#endif
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

        HAL_GPIO_DeInit(GPIOI, GPIO_PIN_9 | GPIO_PIN_10 | GPIO_PIN_0 | GPIO_PIN_1
                              | GPIO_PIN_2 | GPIO_PIN_5 | GPIO_PIN_6 | GPIO_PIN_7);
        HAL_GPIO_DeInit(GPIOF, GPIO_PIN_10);
        HAL_GPIO_DeInit(GPIOH, GPIO_PIN_9 | GPIO_PIN_10 | GPIO_PIN_11 | GPIO_PIN_12
                              | GPIO_PIN_13 | GPIO_PIN_15);
        HAL_GPIO_DeInit(GPIOA, GPIO_PIN_8);
        HAL_GPIO_DeInit(GPIOG, GPIO_PIN_6 | GPIO_PIN_7);

#if defined(BOARD_V10)
        HAL_GPIO_DeInit(GPIOG, GPIO_PIN_10 | GPIO_PIN_12);
#else
        HAL_GPIO_DeInit(GPIOA, GPIO_PIN_2);
        HAL_GPIO_DeInit(GPIOE, GPIO_PIN_5 | GPIO_PIN_6);
        HAL_GPIO_DeInit(GPIOD, GPIO_PIN_6);
        HAL_GPIO_DeInit(GPIOH, GPIO_PIN_4 | GPIO_PIN_14);
        HAL_GPIO_DeInit(GPIOG, GPIO_PIN_12 | GPIO_PIN_13 | GPIO_PIN_14);
        HAL_GPIO_DeInit(GPIOI, GPIO_PIN_4);
#endif
    }
}
