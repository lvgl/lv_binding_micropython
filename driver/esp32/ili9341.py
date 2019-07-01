##############################################################################
# Pure micropython lvgl display driver for ili9341 on ESP32
##############################################################################

import espidf as esp
import lvgl as lv
import lvesp32

class ili9341:

    width = const(240)
    height = const(320)

    ######################################################

    disp_buf1 = lv.disp_buf_t()
    disp_drv = lv.disp_drv_t()

    def __init__(self, miso=5, mosi=18, clk=19, cs=13, dc=12, rst=4, backlight=2, spihost=esp.enum.HSPI_HOST, mhz=40, factor=10):

        # Make sure Micropython was built such that color won't require processing before DMA

        if lv.color_t.SIZE != 2:
            raise RuntimeError('ili9341 micropython driver requires defining LV_COLOR_DEPTH=16')
        if not hasattr(lv.color_t().ch, 'green_l'):
            raise RuntimeError('ili9341 micropython driver requires defining LV_COLOR_16_SWAP=1')

        # Initializations

        self.buf1_1 = bytearray((self.width * self.height * lv.color_t.SIZE) // factor)

        self.miso = miso
        self.mosi = mosi
        self.clk = clk
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.backlight = backlight
        self.spihost = spihost
        self.mhz = mhz

        self.init()

        # Register display driver 

        lv.disp_buf_init(self.disp_buf1, self.buf1_1, None, len(self.buf1_1) // lv.color_t.SIZE)
        lv.disp_drv_init(self.disp_drv)
        self.disp_drv.buffer = self.disp_buf1
        self.disp_drv.flush_cb = self.flush
        self.disp_drv.hor_res = self.width
        self.disp_drv.ver_res = self.height
        lv.disp_drv_register(self.disp_drv)

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
            {'cmd': 0x11, 'data': bytearray([0]), 'delay':100},
            {'cmd': 0x29, 'data': bytearray([0]), 'delay':100}]


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
            "flags": 1<<4, # SPI_DEVICE_HALFDUPLEX
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

        ptr_to_spi = esp.C_Pointer()
	ret = esp.spi_bus_add_device(self.spihost, devcfg, ptr_to_spi)
        if ret != 0: raise RuntimeError("Failed adding SPI device")
        self.spi = ptr_to_spi.ptr_val

    ######################################################

    trans = esp.spi_transaction_t()
    trans_res = esp.spi_transaction_t()

    def disp_spi_send(self, data):
        if len(data) == 0: return      # no need to send anything

        self.trans.length = len(data) * 8 # Length is in bytes, transaction length is in bits. 
        self.trans.tx_buffer = data

	esp.spi_device_queue_trans(self.spi, self.trans, -1)
	esp.spi_device_get_trans_result(self.spi, self.trans_res, -1)


    ######################################################

    cmd_data = bytearray(1)

    def send_cmd(self, cmd):
        self.cmd_data[0] = cmd
	esp.gpio_set_level(self.dc, 0)	 # Command mode
	self.disp_spi_send(self.cmd_data)

    def send_data(self, data):
	esp.gpio_set_level(self.dc, 1)	 # Data mode
	self.disp_spi_send(data)

    ######################################################

    def init(self):
        self.disp_spi_init()
        esp.gpio_pad_select_gpio(self.dc)

	# Initialize non-SPI GPIOs

	esp.gpio_set_direction(self.dc, esp.GPIO_MODE.OUTPUT)
	esp.gpio_set_direction(self.rst, esp.GPIO_MODE.OUTPUT)
        if self.backlight != -1: esp.gpio_set_direction(self.backlight, esp.GPIO_MODE.OUTPUT)

	# Reset the display

	esp.gpio_set_level(self.rst, 0)
        esp.task_delay_ms(100)
	esp.gpio_set_level(self.rst, 1)
        esp.task_delay_ms(100)

	# Send all the commands

        for cmd in self.init_cmds:
            self.send_cmd(cmd['cmd'])
            self.send_data(cmd['data'])
            if hasattr(cmd, 'delay'):
                task_delay_ms(cmd['delay'])

	print("ILI9341 initialization completed")

	# Enable backlight

        if self.backlight != -1:
            print("Enable backlight")
            esp.gpio_set_level(self.backlight, 1)       
    
    ######################################################

    flush_data = bytearray(4)

    def flush(self, disp_drv, area, color_p):

	# Column addresses

	self.send_cmd(0x2A);
        self.flush_data[0] = (area.x1 >> 8) & 0xFF
        self.flush_data[1] = area.x1 & 0xFF
        self.flush_data[2] = (area.x2 >> 8) & 0xFF
        self.flush_data[3] = area.x2 & 0xFF
        self.send_data(self.flush_data)

	# Page addresses

	self.send_cmd(0x2B);
        self.flush_data[0] = (area.y1 >> 8) & 0xFF
        self.flush_data[1] = area.y1 & 0xFF
        self.flush_data[2] = (area.y2 >> 8) & 0xFF
        self.flush_data[3] = area.y2 & 0xFF
        self.send_data(self.flush_data)

	# Memory write
	self.send_cmd(0x2C)

	size = (area.x2 - area.x1 + 1) * (area.y2 - area.y1 + 1)

        data_view = color_p.__dereference__(size * 2)

	self.send_data(data_view)
	lv.disp_flush_ready(disp_drv)

