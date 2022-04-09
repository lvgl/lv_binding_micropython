import time
import machine
import struct

# see e.g.
# https://github.com/MatthewLowden/RPi-XPT2046-Touchscreen-Python/blob/master/XPT2046.py
# and the XPT2046 datasheet

class Xpt2046:
    CHAN_X  = const(0b0101_0000)
    CHAN_Y  = const(0b0001_0000)
    CHAN_Z1 = const(0b0011_0000)
    CHAN_Z2 = const(0b0100_0000)
    CHAN_T0 = const(0b0000_0000)
    CHAN_T1 = const(0b0111_0000)
    CHAN_BAT= const(0b0010_0000)
    CHAN_AUX= const(0b0110_0000)

    CONV_8_BIT =const(0b0000_1000)
    CONV_12_BIT=const(0b0000_0000)
    START_BIT  =const(0b1000_0000)

    def _chanRead(self,chan):
        self.cs.value(0)
        struct.pack_into('BBB',self.buf,0,Xpt2046.START_BIT|self.conv|chan,0,0)
        self.spi.write_readinto(self.buf,self.buf)
        if self.conv==Xpt2046.CONV_8_BIT: ret=self.buf[1]
        else: ret=(self.buf[1]<<4)|(self.buf[2]>>4)
        self.cs.value(1)
        return ret

    def __init__(self,*,
        spi: machine.SPI,cs,bits=12,ranges=((100,1900),(200,1950)),width=240,height=320,rot=0):
        '''
        Construct the Xpt2046 touchscreen controller.
        *spi*: spi bus instance; its baud rate must *not* exceed 2_000_000 (2MHz) for correct functionality
        *cs*: chip select (GPIO number or machine.Pin instance)
        *bits*: ADC precision, can be 12 or 8; note that 8 will require you to provide different *ranges*
        *ranges*: `(x_min,x_max),(y_min,y_max)` for raw coordinate readings; calibrated values might be provided.
        *width*: width of the underyling screen in pixels, in natural (rot=0) orientation (0..*width* is the range for reported horizontal coordinate)
        *height*: height of the underyling screen in pixels
        *rot*: screen rotation (0: portrait, 1: landscape, 2: reverse portrait, 3: reverse landscape)
        '''
        self.buf = bytearray(3)
        self.spi = spi
        self.cs  = (machine.Pin(cs,machine.Pin.OUT) if isinstance(cs,int) else cs)
        self.cs.value(1)
        if bits not in (8,12): raise ValueError('Xpt2046.bits: must be 8 or 12 (not %s)'%str(bits))
        self.conv=(Xpt2046.CONV_8_BIT if bits==8 else Xpt2046.CONV_12_BIT)
        self.xy_range,self.dim,self.rot=ranges,(width,height),(rot%4)
        self.xy_scale=[self.dim[ax]*1./(self.xy_range[ax][1]-self.xy_range[ax][0]) for ax in (0,1)]
        self.xy_origin=[self.xy_range[ax][0] for ax in (0,1)]
    def _raw2px(self,rxy):
        'Convert raw coordinates to pixel coordinates'
        x,y=[int(self.xy_scale[ax]*(rxy[ax]-self.xy_origin[ax])) for ax in (0,1)]
        if   self.rot==0: return self.dim[0]-x,y
        elif self.rot==1: return self.dim[1]-y,x
        elif self.rot==2: return x,self.dim[1]-y
        else:             return y,self.dim[0]-x
    def _raw_pos(self):
        'Read raw position; return value if within valid ranges (`__init__(ranges=...)`) or `None` if outside.'
        ret=[0,0]
        for ax,chan in [(0,Xpt2046.CHAN_X),(1,Xpt2046.CHAN_Y)]:
            r=self._chanRead(chan)
            if not self.xy_range[ax][0]<=r<=self.xy_range[ax][1]: return None
            ret[ax]=r
        return ret

    def pos(self,N=10,attempts=20):
        ''''
        Get N position readings (limited by 20 attempts) and return mean position of valid readings.
        If attempts are exhausted, return None.
        '''
        N,attempts=10,20
        xx,yy,done=0,0,0
        for _ in range(attempts):
            if (r:=self._raw_pos()) is None: continue
            xx+=r[0]; yy+=r[1]; done+=1
            if done==N: break
        else: return None
        mx,my=xx*1./N,yy*1./N
        return self._raw2px((mx,my))

if __name__=='__main__':

    def test_tsc():
        TP_CLK_PIN,TP_MOSI_PIN,TP_MISO_PIN=10,11,12
        TP_CS_PIN=16
        spi=machine.SPI(
            1,
            baudrate=2_000_000, # the chip does not handle more than 2MHz (!)
            polarity=0,
            phase=0,
            sck=machine.Pin(TP_CLK_PIN, machine.Pin.OUT),
            mosi=machine.Pin(TP_MOSI_PIN, machine.Pin.OUT),
            miso=machine.Pin(TP_MISO_PIN, machine.Pin.OUT),
        )

        tsc=Xpt2046(spi=spi,cs=TP_CS_PIN,rot=1)
        for i in range(100000):
            if p:=tsc.pos(): print(p)

    test_tsc()
