/**
 * This file defines the Micorpython API to ESP-IDF
 * It is used as input to gen_mpy.py to create a micropython module
 **/ 

// Disable some macros and includes that make pycparser choke

#ifdef PYCPARSER
#define __attribute__(x)
#define _SOC_IO_MUX_REG_H_
#define _SYS_REENT_H_
#define PORTMACRO_H
#define PORTABLE_H
#define INC_FREERTOS_H
#define QUEUE_H
#define SEMAPHORE_H

// Exclude SOC just because it contains large structs that don't interest the user
#define _SOC_SPI_PERIPH_H_
typedef void *spi_dev_t;

// TODO: Check why lldesc_t causes inifinite recursion on gen_mpy.py 
#define _ROM_LLDESC_H_
typedef void *lldesc_t; 

// FreeRTOS portmaco is excluded, but we still need TickType_t
#include <stdint.h>
typedef uint16_t TickType_t;


#else //PYCPARSER

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

#endif //PYCPARSER

// The following includes are the source of the esp-idf micropython module.
// All included files are API we want to include in the module

#include "driver/gpio.h"
#include "driver/spi_master.h"

// We don't want the whole FreeRTOS, only selected functions

static inline void task_delay_ms(int ms)
{
	vTaskDelay(ms / portTICK_RATE_MS);
}

