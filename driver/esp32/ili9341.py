# Pure micropython lvgl display driver for ili9341 on ESP32

import espidf as esp

class ili9341:

    ######################################################

    init_cmds = [
            {'cmd': 0xCF, 'data': bytearray([0x00, 0x83, 0X30])},
            {'cmd': 0xED, 'data': bytearray([0x64, 0x03, 0X12, 0X81])},
            {'cmd': 0xE8, 'data': bytearray([0x85, 0x01, 0x79])},
            {'cmd': 0xCB, 'data': bytearray([0x39, 0x2C, 0x00, 0x34, 0x02])},
            {'cmd': 0xF7, 'data': bytearray([0x20])},
            {'cmd': 0xEA, 'data': bytearray([0x00, 0x00])},
            {'cmd': 0xC0, 'data': bytearray([0x26])},			# Power control
            {'cmd': 0xC1, 'data': bytearray([0x11])},			# Power control
            {'cmd': 0xC5, 'data': bytearray([0x35, 0x3E])},	        # VCOM control
            {'cmd': 0xC7, 'data': bytearray([0xBE])},			# VCOM control
            {'cmd': 0x36, 'data': bytearray([0x48])},			# Memory Access Control
            {'cmd': 0x3A, 'data': bytearray([0x55])},			# Pixel Format Set
            {'cmd': 0xB1, 'data': bytearray([0x00, 0x1B])},
            {'cmd': 0xF2, 'data': bytearray([0x08])},
            {'cmd': 0x26, 'data': bytearray([0x01])},
            {'cmd': 0xE0, 'data': bytearray([0x1F, 0x1A, 0x18, 0x0A, 0x0F, 0x06, 0x45, 0X87, 0x32, 0x0A, 0x07, 0x02, 0x07, 0x05, 0x00])},
            {'cmd': 0XE1, 'data': bytearray([0x00, 0x25, 0x27, 0x05, 0x10, 0x09, 0x3A, 0x78, 0x4D, 0x05, 0x18, 0x0D, 0x38, 0x3A, 0x1F])},
            {'cmd': 0x2A, 'data': bytearray([0x00, 0x00, 0x00, 0xEF])},
            {'cmd': 0x2B, 'data': bytearray([0x00, 0x00, 0x01, 0x3f])},
            {'cmd': 0x2C, 'data': bytearray([0])},
            {'cmd': 0xB7, 'data': bytearray([0x07])},
            {'cmd': 0xB6, 'data': bytearray([0x0A, 0x82, 0x27, 0x00])},
            {'cmd': 0x11, 'data': bytearray([0]), 'delay':True},
            {'cmd': 0x29, 'data': bytearray([0]), 'delay':True}]


    ######################################################

    def disp_spi_init(self):
	buscfg = esp.spi_bus_config_t({
            "miso_io_num": self.miso,
	    "mosi_io_num": self.mosi,
	    "sclk_io_num": self.clk,
	    "quadwp_io_num": -1,
	    "quadhd_io_num": -1,
	    "max_transfer_sz": 128*1024,
	})

	devcfg = esp.spi_device_interface_config_t({
            "clock_speed_hz": self.mhz*1000*1000, # Clock out at DISP_SPI_MHZ MHz
            "mode": 0,                            # SPI mode 0
            "spics_io_num": self.cs,              # CS pin
            "queue_size": 1,
            "pre_cb": None,
            "post_cb": None,
            "flags": 1<<4, # SPI_DEVICE_HALFDUPLEX,
            "duty_cycle_pos": 128,
	})

	esp.gpio_pad_select_gpio(self.miso)
        esp.gpio_pad_select_gpio(self.mosi)
        esp.gpio_pad_select_gpio(self.clk)

        esp.gpio_set_direction(self.miso, esp.GPIO_MODE.INPUT)
        esp.gpio_set_pull_mode(self.miso, esp.GPIO.PULLUP_ONLY)
        esp.gpio_set_direction(self.mosi, esp.GPIO_MODE.OUTPUT)
        esp.gpio_set_direction(self.clk, esp.GPIO_MODE.OUTPUT)

        esp.gpio_pad_select_gpio(self.cs)

	# Initialize the SPI bus

	ret = esp.spi_bus_initialize(self.spihost, buscfg, 1)
        if ret != 0: raise RuntimeError("Failed initializing SPI bus")

	# Attach the LCD to the SPI bus
        self.spi = esp.C_Pointer()
	ret = esp.spi_bus_add_device(self.spihost, devcfg, self.spi)
        if ret != 0: raise RuntimeError("Failed adding SPI device")

    ######################################################

    def disp_spi_send(self, data):
        if len(data) == 0: return      # no need to send anything

	t = esp.spi_transaction_t({
            "length": len(data)* 8 # Length is in bytes, transaction length is in bits.
            "tx_buffer":  data
        })

	esp.spi_device_queue_trans(self.spi, t, 0xffffffff)

	rt = esp.spi_transaction_t()
	spi_device_get_trans_result(self.spi, rt, 0xffffffff)


    ######################################################

    def send_cmd(self, cmd):
	esp.gpio_set_level(self.dc, 0)	 # Command mode
	self.disp_spi_send(self, [cmd])

    def send_data(self, data):
	esp.gpio_set_level(self.dc, 1)	 # Data mode
	self.disp_spi_send(self, data)

    ######################################################

    def init(self):
        self.disp_spi_init(self)
        esp.gpio_pad_select_gpio(self.dc)

	# Initialize non-SPI GPIOs
	esp.gpio_set_direction(self.dc, esp.GPIO_MODE.OUTPUT)
	esp.gpio_set_direction(self.rst, esp.GPIO_MODE.OUTPUT)
        if self.backlight != -1: esp.gpio_set_direction(self.backlight, esp.GPIO_MODE.OUTPUT)

	# Reset the display
	esp.gpio_set_level(self.rst, 0)
        task_delay_ms(100)
	esp.gpio_set_level(self.rst, 1)
        task_delay_ms(100)

	print("ILI9341 initialization")

	# Send all the commands
        for cmd in init_cmds:
            self.send_cmd(self, cmd.cmd)
            self.send_data(self, cmd.data)
            if hasattr(cmd, 'delay'):
                task_delay_ms(100)

	# Enable backlight
        if self.backlight != -1:
            print("Enable backlight")
            self.gpio_set_level(self.backlight, 1)       
    
    ######################################################


    def flush(disp_drv, area, color_p):
	uint8_t data[4];

    ILI9341_t *self = g_ILI9341;

	/*Column addresses*/
	ili9441_send_cmd(self, 0x2A);
	data[0] = (area->x1 >> 8) & 0xFF;
	data[1] = area->x1 & 0xFF;
	data[2] = (area->x2 >> 8) & 0xFF;
	data[3] = area->x2 & 0xFF;
	ili9341_send_data(self, data, 4);

	/*Page addresses*/
	ili9441_send_cmd(self, 0x2B);
	data[0] = (area->y1 >> 8) & 0xFF;
	data[1] = area->y1 & 0xFF;
	data[2] = (area->y2 >> 8) & 0xFF;
	data[3] = area->y2 & 0xFF;
	ili9341_send_data(self, data, 4);

	/*Memory write*/
	ili9441_send_cmd(self, 0x2C);

	uint32_t size = (area->x2 - area->x1 + 1) * (area->y2 - area->y1 + 1);

	/*Byte swapping is required*/
	uint32_t i;
	uint8_t * color_u8 = (uint8_t *) color_p;
	uint8_t color_tmp;
	for(i = 0; i < size * 2; i += 2) {
		color_tmp = color_u8[i + 1];
		color_u8[i + 1] = color_u8[i];
		color_u8[i] = color_tmp;
	}

	ili9341_send_data(self, (void*)color_p, size * 2);

	/*
	while(size > LV_HOR_RES) {

		ili9341_send_data((void*)color_p, LV_HOR_RES * 2);
		//vTaskDelay(10 / portTICK_PERIOD_MS);
		size -= LV_HOR_RES;
		color_p += LV_HOR_RES;
	}

	ili9341_send_data((void*)color_p, size * 2);	*/ /*Send the remaining data*/

	lv_disp_flush_ready(disp_drv);
}
