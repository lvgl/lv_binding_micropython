##############################################################################
# Pure micropython lvgl display driver for ili9341 on ESP32
#
# Build micropython with LV_CFLAGS="-DLV_COLOR_DEPTH=16 -DLV_COLOR_16_SWAP=1"
# (make parameter) to configure LVGL use the same color format as ili9341
# and prevent the need to loop over all pixels to translate them.
##############################################################################

import espidf as esp
import lvgl as lv
import lvesp32
import micropython
import gc

micropython.alloc_emergency_exception_buf(256)
# gc.threshold(0x10000) # leave enough room for SPI master TX DMA buffers

class ili9341:

    width = const(240)
    height = const(320)

    ######################################################

    disp_buf = lv.disp_buf_t()
    disp_drv = lv.disp_drv_t()

    def __init__(self, miso=5, mosi=18, clk=19, cs=13, dc=12, rst=4, backlight=2, spihost=esp.enum.HSPI_HOST, mhz=40, factor=5):

        # Make sure Micropython was built such that color won't require processing before DMA

        if lv.color_t.SIZE != 2:
            raise RuntimeError('ili9341 micropython driver requires defining LV_COLOR_DEPTH=16')
        if not hasattr(lv.color_t().ch, 'green_l'):
            raise RuntimeError('ili9341 micropython driver requires defining LV_COLOR_16_SWAP=1')

        # Initializations

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

        buf_size = (self.width * self.height * lv.color_t.SIZE) // factor

        lv.disp_buf_init(self.disp_buf, bytearray(buf_size), bytearray(buf_size), buf_size // lv.color_t.SIZE)
        lv.disp_drv_init(self.disp_drv)

        self.disp_drv.buffer = self.disp_buf
        self.disp_drv.flush_cb = self.flush
        self.disp_drv.monitor_cb = self.monitor
        self.disp_drv.hor_res = self.width
        self.disp_drv.ver_res = self.height
        
        lv.disp_drv_register(self.disp_drv)

    ######################################################

    init_cmds = [
            {'cmd': 0xCF, 'data': bytes([0x00, 0x83, 0X30])},
            {'cmd': 0xED, 'data': bytes([0x64, 0x03, 0X12, 0X81])},
            {'cmd': 0xE8, 'data': bytes([0x85, 0x01, 0x79])},
            {'cmd': 0xCB, 'data': bytes([0x39, 0x2C, 0x00, 0x34, 0x02])},
            {'cmd': 0xF7, 'data': bytes([0x20])},
            {'cmd': 0xEA, 'data': bytes([0x00, 0x00])},
            {'cmd': 0xC0, 'data': bytes([0x26])},		# Power control
            {'cmd': 0xC1, 'data': bytes([0x11])},		# Power control
            {'cmd': 0xC5, 'data': bytes([0x35, 0x3E])},	        # VCOM control
            {'cmd': 0xC7, 'data': bytes([0xBE])},		# VCOM control
            {'cmd': 0x36, 'data': bytes([0x48])},		# Memory Access Control
            {'cmd': 0x3A, 'data': bytes([0x55])},		# Pixel Format Set
            {'cmd': 0xB1, 'data': bytes([0x00, 0x1B])},
            {'cmd': 0xF2, 'data': bytes([0x08])},
            {'cmd': 0x26, 'data': bytes([0x01])},
            {'cmd': 0xE0, 'data': bytes([0x1F, 0x1A, 0x18, 0x0A, 0x0F, 0x06, 0x45, 0X87, 0x32, 0x0A, 0x07, 0x02, 0x07, 0x05, 0x00])},
            {'cmd': 0XE1, 'data': bytes([0x00, 0x25, 0x27, 0x05, 0x10, 0x09, 0x3A, 0x78, 0x4D, 0x05, 0x18, 0x0D, 0x38, 0x3A, 0x1F])},
            {'cmd': 0x2A, 'data': bytes([0x00, 0x00, 0x00, 0xEF])},
            {'cmd': 0x2B, 'data': bytes([0x00, 0x00, 0x01, 0x3f])},
            {'cmd': 0x2C, 'data': bytes([0])},
            {'cmd': 0xB7, 'data': bytes([0x07])},
            {'cmd': 0xB6, 'data': bytes([0x0A, 0x82, 0x27, 0x00])},
            {'cmd': 0x11, 'data': bytes([0]), 'delay':100},
            {'cmd': 0x29, 'data': bytes([0]), 'delay':100}]


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
            "clock_speed_hz": self.mhz*1000*1000,   # Clock out at DISP_SPI_MHZ MHz
            "mode": 0,                              # SPI mode 0
            "spics_io_num": self.cs,                # CS pin
            "queue_size": 2,
            "pre_cb": esp.spi_pre_cb_isr,
            "post_cb": esp.spi_post_cb_isr,
            "flags": 1<<4,                          # SPI_DEVICE_HALFDUPLEX
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

        self.bytes_transmitted = 0
        completed_spi_transaction = esp.spi_transaction_t()
        cast_spi_transaction_instance = esp.spi_transaction_t.cast_instance

        def post_isr(arg):
            reported_transmitted = self.bytes_transmitted
            if reported_transmitted > 0:
                print('- Completed DMA of %d bytes (mem_free=0x%X)' % (reported_transmitted , gc.mem_free()))
                self.bytes_transmitted -= reported_transmitted

        # Called in ISR context!
        def flush_isr(spi_transaction_ptr):
            lv.disp_flush_ready(self.disp_drv)
            # cast_spi_transaction_instance(completed_spi_transaction, spi_transaction_ptr)
            # self.bytes_transmitted += completed_spi_transaction.length
            # try:
            #     micropython.schedule(post_isr, None)
            # except RuntimeError:
            #     pass
        
        self.spi_callbacks = esp.spi_transaction_set_cb(None, flush_isr)

    ######################################################

    trans = esp.spi_transaction_t()
    trans_res = esp.spi_transaction_t()

    def disp_spi_send(self, data, dma=False):
        if len(data) == 0: return      # no need to send anything

        self.trans.length = len(data) * 8 # Length is in bytes, transaction length is in bits. 
        self.trans.tx_buffer = data

        if dma:
            self.trans.user = self.spi_callbacks
            esp.spi_device_queue_trans(self.spi, self.trans, -1)
        else:
            self.trans.user = None
            esp.spi_device_polling_transmit(self.spi, self.trans)

    ######################################################

    cmd_data = bytearray(1)

    def send_cmd(self, cmd):
        self.cmd_data[0] = cmd
	esp.gpio_set_level(self.dc, 0)	 # Command mode
	self.disp_spi_send(self.cmd_data)

    def send_data(self, data, dma=False):
	esp.gpio_set_level(self.dc, 1)	 # Data mode
	self.disp_spi_send(data, dma=dma)

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
            if 'delay' in cmd:
                esp.task_delay_ms(cmd['delay'])

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

	# Memory write by DMA, disp_flush_ready when finished

	self.send_cmd(0x2C)

	size = (area.x2 - area.x1 + 1) * (area.y2 - area.y1 + 1)
        data_view = color_p.__dereference__(size * lv.color_t.SIZE)

        self.send_data(data_view, dma=True)
	
    ######################################################

    monitor_acc_time = 0
    monitor_acc_px = 0
    monitor_count = 0

    def monitor(self, disp_drv, time, px):
        self.monitor_acc_time += time
        self.monitor_acc_px += px
        self.monitor_count += 1

    def stat(self):
        if self.monitor_count == 0:
            return None

        time = self.monitor_acc_time // self.monitor_count
        px = self.monitor_acc_px // self.monitor_count
        self.monitor_acc_time = 0
        self.monitor_acc_px = 0
        self.monitor_count = 0

        return time, px


##########################
# TESTING - remove this
##########################

lv.init()
disp = ili9341()


# Animation helper class

class Anim(lv.anim_t):
    def __init__(self, obj, val, size, exec_cb, path_cb, time=500, playback = False, ready_cb=None):
        super().__init__()
        lv.anim_init(self)
        lv.anim_set_time(self, time, 0)
        lv.anim_set_values(self, val, val+size)
        try:
            lv.anim_set_exec_cb(self, obj, exec_cb)
        except TypeError:
            lv.anim_set_custom_exec_cb(self, exec_cb)
        lv.anim_set_path_cb(self, path_cb )
        if playback: lv.anim_set_playback(self, 0)
        if ready_cb: lv.anim_set_ready_cb(self, ready_cb)
        lv.anim_create(self)

# An animated chart

class AnimatedChart(lv.chart):
    def __init__(self, parent, val, size):            
        super().__init__(parent)
        self.val = val
        self.size = size
        self.max = 2000
        self.min = 500
        self.factor = 100
        self.anim_phase1()

    def anim_phase1(self):
        Anim(
            self, 
            self.val, 
            self.size, 
            lambda a, val: self.set_range(0, val), 
            lv.anim_path_ease_in, 
            ready_cb=lambda a:self.anim_phase2(),
            time=(self.max * self.factor) // 100)

    def anim_phase2(self):
        Anim(
            self, 
            self.val+self.size, 
            -self.size, 
            lambda a, val: self.set_range(0, val), 
            lv.anim_path_ease_out, 
            ready_cb=lambda a:self.anim_phase1(),
            time=(self.min * self.factor) // 100)

# Create the chart

scr = lv.obj()
chart = AnimatedChart(scr, 100, 1000)
chart.set_width(scr.get_width() - 100)
chart.align(scr, lv.ALIGN.CENTER, 0, 0)
series1 = chart.add_series(lv.color_hex(0xFF0000))
chart.set_type(chart.TYPE.POINT | chart.TYPE.LINE)
chart.set_series_width(3)
chart.set_range(0,100)
chart.init_points(series1, 10)
chart.set_points(series1, [10,20,30,20,10,40,50,90,95,90])
chart.set_x_tick_texts('a\nb\nc\nd\ne', 2, lv.chart.AXIS.DRAW_LAST_TICK)
chart.set_x_tick_length(10, 5)
chart.set_y_tick_texts('1\n2\n3\n4\n5', 2, lv.chart.AXIS.DRAW_LAST_TICK)
chart.set_y_tick_length(10, 5)
chart.set_div_line_count(3, 3)
chart.set_margin(30)

# Create a slider that controls the chart animation speed

def on_slider_changed(self, obj=None, event=-1):
    chart.factor = slider.get_value()

slider = lv.slider(scr)
slider.align(chart, lv.ALIGN.OUT_RIGHT_TOP, 10, 0)
slider.set_width(30)
slider.set_height(chart.get_height())
slider.set_range(10, 200)
slider.set_value(chart.factor, 0)
slider.set_event_cb(on_slider_changed)

# Load the screen

lv.scr_load(scr)

