"""
MicroPython driver for SD cards using SPI bus.
(based on the original SD driver https://github.com/micropython/micropython/blob/master/drivers/sdcard/sdcard.py)
Espidf SPI support inside for SPI screen driver compatibility

Requires an SPI bus and a CS pin. Provides readblocks and writeblocks
methods so the device can be mounted as a filesystem.

Example usage on pyboard:
    import pyb, sdcard, os
    sd = sdcard.SDCard(pyb.SPI(1), pyb.Pin.board.X5)
    pyb.mount(sd, '/sd2')
    print(os.listdir('/'))

Example usage on ESP8266 / ESP32:
    import machine, sdcard, os
    sd = sdcard.SDCard(machine.SPI(1), machine.Pin(15))
    os.mount(sd, '/sd')
    print(os.listdir('/'))

Example usage on ESP32 with ili93XXX.py screen driver:
    import machine, sdcard, os
    from ili9XXX import ili9341
    lcd = ili9341(mosi=23, miso=38, clk=18, dc=15, cs=5, invert=True, rot=0x10, width=320, height=240,
                 rst=-1, power=-1, backlight=-1, half_duplex=False) # half_duplex do not work with SDCard    
    sd = sdcard.SDCard(sdcard.SPI(), machine.Pin(4))
    os.mount(sd, "/sd")
    print(os.listdir('/sd'))

"""

from micropython import const
import utime

try:
    import espidf as esp
except:
    pass


_CMD_TIMEOUT = const(1000)  # PGH (was 100)

_R1_IDLE_STATE = const(1 << 0)
_R1_ILLEGAL_COMMAND = const(1 << 2)
_TOKEN_CMD25 = const(0xFC)
_TOKEN_STOP_TRAN = const(0xFD)
_TOKEN_DATA = const(0xFE)


class SDCard:
    
    def __init__(self, spi, cs, baudrate=20000000):
        self.spi = spi
        self.cs = cs
        self.baudrate = baudrate
        self.cmdbuf = bytearray(6)
        self.dummybuf = bytearray(512)
        self.tokenbuf = bytearray(1)
        for i in range(512):
            self.dummybuf[i] = 0xFF
        self.dummybuf_memoryview = memoryview(self.dummybuf)

        # initialise the card
        self.init_card()

    
    def init_spi(self, baudrate):
        try:
            master = self.spi.MASTER
        except AttributeError:
            # on ESP8266
            self.spi.init(baudrate=baudrate, phase=0, polarity=0)
        else:
            # on pyboard
            self.spi.init(master, baudrate=baudrate, phase=0, polarity=0)

    
    def init_card(self):
        # init CS pin
        self.cs.init(self.cs.OUT, value=1)

        # init SPI bus; use low data rate for initialization
        self.init_spi(100000)

        # clock card at least 100 cycles with cs high
        for i in range(16):
            self.spi.write(b"\xff")

        # CMD0: init card; should return _R1_IDLE_STATE (allow 5 attempts)
        for _ in range(5):
            if self.cmd(0, 0, 0x95) == _R1_IDLE_STATE:
                break
        else:
            raise OSError("no SD card")

        # CMD8: determine card version
        r = self.cmd(8, 0x01AA, 0x87, 4)
        if r == _R1_IDLE_STATE:
            self.init_card_v2()
        elif r == (_R1_IDLE_STATE | _R1_ILLEGAL_COMMAND):
            self.init_card_v1()
        else:
            raise OSError("couldn't determine SD card version")

        # get the number of sectors
        # CMD9: response R2 (R1 byte + 16-byte block read)
        if self.cmd(9, 0, 0, 0, False) != 0:
            raise OSError("no response from SD card")
        csd = bytearray(16)
        self.readinto(csd)
        if csd[0] & 0xC0 == 0x40:  # CSD version 2.0
            self.sectors = ((csd[8] << 8 | csd[9]) + 1) * 1024
        elif csd[0] & 0xC0 == 0x00:  # CSD version 1.0 (old, <=2GB)
            c_size = csd[6] & 0b11 | csd[7] << 2 | (csd[8] & 0b11000000) << 4
            c_size_mult = ((csd[9] & 0b11) << 1) | csd[10] >> 7
            self.sectors = (c_size + 1) * (2 ** (c_size_mult + 2))
        else:
            raise OSError("SD card CSD format not supported")
        # print('sectors', self.sectors)

        # CMD16: set block length to 512 bytes
        if self.cmd(16, 512, 0) != 0:
            raise OSError("can't set 512 block size")

        # set to high data rate now that it's initialized
        self.init_spi(self.baudrate)

    
    def init_card_v1(self):
        for i in range(_CMD_TIMEOUT):
            self.cmd(55, 0, 0)
            if self.cmd(41, 0, 0) == 0:
                self.cdv = 512
                # print("[SDCard] v1 card")
                return
        raise OSError("timeout waiting for v1 card")

    
    def init_card_v2(self):
        for i in range(_CMD_TIMEOUT):
            utime.sleep_ms(50)
            self.cmd(58, 0, 0, 4)
            self.cmd(55, 0, 0)
            if self.cmd(41, 0x40000000, 0) == 0:
                self.cmd(58, 0, 0, 4)
                self.cdv = 1
                # print("[SDCard] v2 card")
                return
        raise OSError("timeout waiting for v2 card")

    
    def cmd(self, cmd, arg, crc, final=0, release=True, skip1=False):
        self.cs(0)

        # create and send the command
        buf = self.cmdbuf
        buf[0] = 0x40 | cmd
        buf[1] = arg >> 24
        buf[2] = arg >> 16
        buf[3] = arg >> 8
        buf[4] = arg
        buf[5] = crc
        self.spi.write(buf)

        if skip1:
            self.spi.readinto(self.tokenbuf, 0xFF)

        # wait for the response (response[7] == 0)
        for i in range(_CMD_TIMEOUT):
            self.spi.readinto(self.tokenbuf, 0xFF)
            response = self.tokenbuf[0]
            if not (response & 0x80):
                # this could be a big-endian integer that we are getting here
                for j in range(final):
                    self.spi.write(b"\xff")
                if release:
                    self.cs(1)
                    self.spi.write(b"\xff")
                return response

        # timeout
        self.cs(1)
        self.spi.write(b"\xff")
        return -1

    
    def readinto(self, buf):
        self.cs(0)

        # read until start byte (0xff)
        for i in range(_CMD_TIMEOUT):
            self.spi.readinto(self.tokenbuf, 0xFF)
            if self.tokenbuf[0] == _TOKEN_DATA:
                break
        else:
            self.cs(1)
            raise OSError("timeout waiting for response")

        # read data
        mv = self.dummybuf_memoryview
        if len(buf) != len(mv):
            mv = mv[: len(buf)]
        self.spi.write_readinto(mv, buf)

        # read checksum
        self.spi.write(b"\xff")
        self.spi.write(b"\xff")

        self.cs(1)
        self.spi.write(b"\xff")

    
    def write(self, token, buf):
        self.cs(0)

        # send: start of block, data, checksum
        self.spi.read(1, token)
        self.spi.write(buf)
        self.spi.write(b"\xff")
        self.spi.write(b"\xff")

        # check the response
        if (self.spi.read(1, 0xFF)[0] & 0x1F) != 0x05:
            self.cs(1)
            self.spi.write(b"\xff")
            return

        # wait for write to finish
        while self.spi.read(1, 0xFF)[0] == 0:
            pass

        self.cs(1)
        self.spi.write(b"\xff")

    
    def write_token(self, token):
        self.cs(0)
        self.spi.read(1, token)
        self.spi.write(b"\xff")
        # wait for write to finish
        while self.spi.read(1, 0xFF)[0] == 0x00:
            pass

        self.cs(1)
        self.spi.write(b"\xff")

    
    def readblocks(self, block_num, buf):
        self.spi.write(b'\xff')  # PGH
        nblocks = len(buf) // 512
        assert nblocks and not len(buf) % 512, "Buffer length is invalid"
        if nblocks == 1:
            # CMD17: set read address for single block
            if self.cmd(17, block_num * self.cdv, 0, release=False) != 0:
                # release the card
                self.cs(1)
                raise OSError(5)  # EIO
            # receive the data and release card
            self.readinto(buf)
        else:
            # CMD18: set read address for multiple blocks
            if self.cmd(18, block_num * self.cdv, 0, release=False) != 0:
                # release the card
                self.cs(1)
                raise OSError(5)  # EIO
            offset = 0
            mv = memoryview(buf)
            while nblocks:
                # receive the data and release card
                self.readinto(mv[offset : offset + 512])
                offset += 512
                nblocks -= 1
            if self.cmd(12, 0, 0xFF, skip1=True):
                raise OSError(5)  # EIO

    
    def writeblocks(self, block_num, buf):
        # clock card at least 100 cycles with cs high
        self.spi.write(b'\xff')  # PGH
        nblocks, err = divmod(len(buf), 512)
        assert nblocks and not err, "Buffer length is invalid"
        if nblocks == 1:
            # CMD24: set write address for single block
            if self.cmd(24, block_num * self.cdv, 0) != 0:
                raise OSError(5)  # EIO

            # send the data
            self.write(_TOKEN_DATA, buf)
        else:
            # CMD25: set write address for first block
            if self.cmd(25, block_num * self.cdv, 0) != 0:
                raise OSError(5)  # EIO
            # send the data
            offset = 0
            mv = memoryview(buf)
            while nblocks:
                self.write(_TOKEN_CMD25, mv[offset : offset + 512])
                offset += 512
                nblocks -= 1
            self.write_token(_TOKEN_STOP_TRAN)

    
    def ioctl(self, op, arg):
        if op == 4:  # get number of blocks
            return self.sectors





# Pure Espidf SPI driver to share SPI bus (like ili93xxx screen)
class SPI:

    def __init__(self, spihost=esp.HSPI_HOST, baudrate=200000, miso=-1, mosi=-1, clk=-1, cs=4, half_duplex=False):
         
        self.miso = miso
        self.mosi = mosi
        self.clk = clk
        self.cs = cs
        self.half_duplex = half_duplex
        self.baudrate = baudrate
        self.spihost = spihost
        self.spi = None

        buscfg = esp.spi_bus_config_t(
            {
                "miso_io_num": self.miso,
                "mosi_io_num": self.mosi,
                "sclk_io_num": self.clk,
                "quadwp_io_num": -1,
                "quadhd_io_num": -1,
            }
        )

        # Initialize the SPI bus, if needed.
        if buscfg.miso_io_num >= 0 and buscfg.mosi_io_num >= 0 and buscfg.sclk_io_num >= 0:

            esp.gpio_pad_select_gpio(self.miso)
            esp.gpio_pad_select_gpio(self.mosi)
            esp.gpio_pad_select_gpio(self.clk)

            esp.gpio_set_direction(self.miso, esp.GPIO_MODE.INPUT)
            esp.gpio_set_pull_mode(self.miso, esp.GPIO.PULLUP_ONLY)
            esp.gpio_set_direction(self.mosi, esp.GPIO_MODE.OUTPUT)
            esp.gpio_set_direction(self.clk, esp.GPIO_MODE.OUTPUT)

            ret = esp.spi_bus_initialize(self.spihost, buscfg, 1)
            if ret != 0:
                raise RuntimeError("Failed initializing SPI bus")
  
    
    def init(self, baudrate=None, phase=0, polarity=0 ):
        
        if baudrate:
            #print('new baudrate:',baudrate)
            self.baudrate=baudrate

        if self.spi:
            # Remove device (to change bus speed)
            esp.spi_bus_remove_device(self.spi)
            self.spi = None
            
            
        devcfg_flags = esp.SPI_DEVICE.NO_DUMMY
        if self.half_duplex : devcfg_flags |= esp.SPI_DEVICE.HALFDUPLEX

        devcfgSD = esp.spi_device_interface_config_t({
            "clock_speed_hz": self.baudrate,
            "mode": 0, # SPI mode 0
            "spics_io_num": self.cs, # CS pin
            "queue_size": 2,
            "flags": devcfg_flags,
            "duty_cycle_pos": 128,
        })

        esp.gpio_pad_select_gpio(self.cs)

        # Attach device to the SPI bus
        ptr_to_spi = esp.C_Pointer()
        ret = esp.spi_bus_add_device(self.spihost, devcfgSD, ptr_to_spi)
        if ret != 0:
            raise RuntimeError("Failed adding SPI device")
            
        self.spi = ptr_to_spi.ptr_val
        self.trans_result_ptr = esp.C_Pointer()
    
    
    def write(self, data):
        if not isinstance(data,bytearray) : data = bytearray(data)
        trans = esp.spi_transaction_t({
            "length": len(data) * 8, 
            "tx_buffer": data,
            "rx_buffer": None,
            "user": None,
        })
        esp.spi_device_queue_trans(self.spi, trans, -1)
        esp.spi_device_get_trans_result(self.spi, self.trans_result_ptr , -1)

    def read(self, length:int, write=None):
        if write: write = bytearray([write])
        buf=bytearray(length)
        trans = esp.spi_transaction_t({
            "length": length * 8,
            "tx_buffer": write,
            "rx_buffer": buf,
            "user": None,
        })
        esp.spi_device_queue_trans(self.spi, trans, -1)
        esp.spi_device_get_trans_result(self.spi, self.trans_result_ptr , -1)
        return bytes(buf)

    def readinto(self, buf:bytearray, write=None):
        if write: write = bytearray([write])
        trans = esp.spi_transaction_t({
            "length": len(buf) * 8,
            "tx_buffer": write,
            "rx_buffer": buf,
            "user": None,
        })
        esp.spi_device_queue_trans(self.spi, trans, -1)
        esp.spi_device_get_trans_result(self.spi, self.trans_result_ptr , -1)


    def write_readinto(self, data, buf:bytearray):
        if not isinstance(data,bytearray) : data = bytearray(data)
        trans = esp.spi_transaction_t({
            "length": len(data) * 8,
            "tx_buffer": data,
            "rx_buffer": buf,
            "user": None,
        })
        esp.spi_device_queue_trans(self.spi, trans, -1)
        esp.spi_device_get_trans_result(self.spi, self.trans_result_ptr , -1)    

              
    def deinit(self):

        if self.spi:
            # Remove device
            esp.spi_bus_remove_device(self.spi)
            self.spi = None

            # Free SPI bus
            esp.spi_bus_free(self.spihost)
            self.spihost = None

