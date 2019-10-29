from machine import Pin
import espidf as esp
import lvgl as lv

class xpt2046:
    
    CMD_X_READ  = const(0b10010000)
    CMD_Y_READ  = const(0b11010000)
    CMD_Z1_READ = const(0b10110000)
    CMD_Z2_READ = const(0b11000000)

    MAX_RAW_COORD = const((1<<12) - 1)

    def __init__(self, miso=-1, mosi=-1, clk=-1, cs=25, irq=26, spihost=esp.HSPI_HOST, mhz=5, max_cmds=16, cal_x0 = 1892, cal_y0 = 1967, cal_x1 = 121, cal_y1 = 194, transpose = True):

        # Initializations

        self.screen_width = lv.disp_get_hor_res(lv.disp_t.cast(None))
        self.screen_height = lv.disp_get_ver_res(lv.disp_t.cast(None))
        self.miso = miso
        self.mosi = mosi
        self.clk = clk
        self.cs = cs
        self.irq = irq
        self.spihost = spihost
        self.mhz = mhz
        self.max_cmds = max_cmds
        self.cal_x0 = cal_x0
        self.cal_y0 = cal_y0
        self.cal_x1 = cal_x1
        self.cal_y1 = cal_y1
        self.transpose = transpose
        self.touched = False
        
        def handle_irq(p):
            self.touched = (p.value() == 0)
        
        self.irq_pin = Pin(self.irq, Pin.IN)
        self.irq_pin.irq(trigger = Pin.IRQ_FALLING | Pin.IRQ_RISING, handler = handle_irq)

        self.spi_init()
        
    def calibrate(self, x0, y0, x1, y1):
        self.cal_x0 = x0
        self.cal_y0 = y0
        self.cal_x1 = x1
        self.cal_y1 = y1

    def spi_init(self):
	buscfg = esp.spi_bus_config_t({
            "miso_io_num": self.miso,
	    "mosi_io_num": self.mosi,
	    "sclk_io_num": self.clk,
	    "quadwp_io_num": -1,
	    "quadhd_io_num": -1,
	    "max_transfer_sz": 4,
	})

	devcfg = esp.spi_device_interface_config_t({
            "command_bits": 9,                      # Actually 8, but need another cycle before xpt starts transmitting response, see Figure 12 on datasheet.
            "clock_speed_hz": self.mhz*1000*1000,   
            "mode": 0,                              # SPI mode 0
            "spics_io_num": self.cs,                # CS pin
            "queue_size": self.max_cmds,
            "flags": esp.SPI_DEVICE.HALFDUPLEX,
            "duty_cycle_pos": 128,
	})

        esp.gpio_pad_select_gpio(self.cs)

	# Initialize the SPI bus, if needed

        if buscfg.miso_io_num >= 0 and \
           buscfg.mosi_io_num >= 0 and \
           buscfg.sclk_io_num >= 0:

                esp.gpio_pad_select_gpio(self.miso)
                esp.gpio_pad_select_gpio(self.mosi)
                esp.gpio_pad_select_gpio(self.clk)

                esp.gpio_set_direction(self.miso, esp.GPIO_MODE.INPUT)
                esp.gpio_set_pull_mode(self.miso, esp.GPIO.PULLUP_ONLY)
                esp.gpio_set_direction(self.mosi, esp.GPIO_MODE.OUTPUT)
                esp.gpio_set_direction(self.clk, esp.GPIO_MODE.OUTPUT)

                ret = esp.spi_bus_initialize(self.spihost, buscfg, 1)
                if ret != 0: raise RuntimeError("Failed initializing SPI bus")

	# Attach the LCD to the SPI bus

        ptr_to_spi = esp.C_Pointer()
	ret = esp.spi_bus_add_device(self.spihost, devcfg, ptr_to_spi)
        if ret != 0: raise RuntimeError("Failed adding SPI device")
        self.spi = ptr_to_spi.ptr_val
        
        # Prepare transactions

        self.trans = [esp.spi_transaction_t() for i in range(0, self.max_cmds)]
        for trans in self.trans:
            trans.rx_buffer = bytearray(2)
            trans.rxlength = 16

    trans_result_ptr = esp.C_Pointer()

    def xpt_cmds(self, cmds):
        for i, cmd in enumerate(cmds):
            self.trans[i].cmd = cmd
            esp.spi_device_queue_trans(self.spi, self.trans[i], -1)
        result = []
        for i in range(0, len(cmds)):
            esp.spi_device_get_trans_result(self.spi, self.trans_result_ptr , -1)
            buf = self.trans[i].rx_buffer.__dereference__(2)
            value = (buf[0] << 4) + (buf[1] >> 4) # value is in the 12 higher bits, network order
            if value == self.MAX_RAW_COORD:
                value = 0
            result.append(value)
        return tuple(result)
    
    def get_raw_coords(self):
        return self.xpt_cmds([self.CMD_X_READ, self.CMD_Y_READ])

    def get_med_coords(self, count=7):
        mid = count//2
        values = [self.get_raw_coords() for i in range(0, count)]
        # values = self.xpt_cmds([self.CMD_X_READ]*count + [self.CMD_Y_READ]*count)
        # x_values = sorted(values[:count])
        # y_values = sorted(values[count:])
        x_values = sorted([x for x,y in values])
        y_values = sorted([y for x,y in values])
        if 0 in x_values or 0 in y_values: return 0,0
        return x_values[mid], y_values[mid]

    def get_coords(self):
        if self.transpose:
            raw_y, raw_x = self.get_med_coords() 
        else:
            raw_x, raw_y = self.get_med_coords() 

        if raw_x != 0 and raw_y != 0:
            x = ((raw_x - self.cal_x0) * self.screen_width) // (self.cal_x1 - self.cal_x0)
            y = ((raw_y - self.cal_y0) * self.screen_height) // (self.cal_y1 - self.cal_y0)
            # print('(%d, %d) ==> (%d, %d)' % (raw_x, raw_y, x, y))
            return x,y
        else: return -1,-1

    def get_pressure(self, factor):
        z1, z2, x = self.xpt_cmds([self.CMD_Z1_READ, self.CMD_Z2_READ, self.CMD_X_READ])
        if z1 == 0: return -1
        return ( (x*factor)/4096 )*( z2/z1 -1 )

    def read(self, indev_drv, data):
        if self.touched:
            data.point.x ,data.point.y = self.get_coords()
            data.state = lv.INDEV_STATE.PR
        else:
            data.state = lv.INDEV_STATE.REL
        return False

'''
device = xpt2046()

def handle_irq(p):
    x,y = device.get_med_coords()
    if x != 0 and y != 0:
        print('%d, %d' % (x,y))

irq_pin = Pin(26, Pin.IN)
irq_pin.irq(trigger=Pin.IRQ_FALLING, handler=handle_irq)
'''
