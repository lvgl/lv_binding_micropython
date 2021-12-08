'''
MIT License

Copyright (c) 2019 lewis he

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

axp20x.py - MicroPython library for X-Power AXP202 chip.
Created by Lewis he on June 24, 2019.
github:https://github.com/lewisxhe/AXP202X_Libraries

Modified by Russ Hughes on Mar 26, 2021 to use optionally use an initalized I2c
bus object.

'''


import gc
from machine import Pin, SoftI2C
import micropython
from ustruct import unpack


# Chip Address
AXP202_SLAVE_ADDRESS = 0x35
AXP192_SLAVE_ADDRESS = 0x34

# Chip ID
AXP202_CHIP_ID = 0x41
AXP192_CHIP_ID = 0x03

default_pin_scl = 22
default_pin_sda = 21
default_pin_intr = 35
default_chip_type = AXP202_CHIP_ID


# REG MAP
AXP202_STATUS = 0x00
AXP202_MODE_CHGSTATUS = 0x01
AXP202_OTG_STATUS = 0x02
AXP202_IC_TYPE = 0x03
AXP202_DATA_BUFFER1 = 0x04
AXP202_DATA_BUFFER2 = 0x05
AXP202_DATA_BUFFER3 = 0x06
AXP202_DATA_BUFFER4 = 0x07
AXP202_DATA_BUFFER5 = 0x08
AXP202_DATA_BUFFER6 = 0x09
AXP202_DATA_BUFFER7 = 0x0A
AXP202_DATA_BUFFER8 = 0x0B
AXP202_DATA_BUFFER9 = 0x0C
AXP202_DATA_BUFFERA = 0x0D
AXP202_DATA_BUFFERB = 0x0E
AXP202_DATA_BUFFERC = 0x0F
AXP202_LDO234_DC23_CTL = 0x12
AXP202_DC2OUT_VOL = 0x23
AXP202_LDO3_DC2_DVM = 0x25
AXP202_DC3OUT_VOL = 0x27
AXP202_LDO24OUT_VOL = 0x28
AXP202_LDO3OUT_VOL = 0x29
AXP202_IPS_SET = 0x30
AXP202_VOFF_SET = 0x31
AXP202_OFF_CTL = 0x32
AXP202_CHARGE1 = 0x33
AXP202_CHARGE2 = 0x34
AXP202_BACKUP_CHG = 0x35
AXP202_POK_SET = 0x36
AXP202_DCDC_FREQSET = 0x37
AXP202_VLTF_CHGSET = 0x38
AXP202_VHTF_CHGSET = 0x39
AXP202_APS_WARNING1 = 0x3A
AXP202_APS_WARNING2 = 0x3B
AXP202_TLTF_DISCHGSET = 0x3C
AXP202_THTF_DISCHGSET = 0x3D
AXP202_DCDC_MODESET = 0x80
AXP202_ADC_EN1 = 0x82
AXP202_ADC_EN2 = 0x83
AXP202_ADC_SPEED = 0x84
AXP202_ADC_INPUTRANGE = 0x85
AXP202_ADC_IRQ_RETFSET = 0x86
AXP202_ADC_IRQ_FETFSET = 0x87
AXP202_TIMER_CTL = 0x8A
AXP202_VBUS_DET_SRP = 0x8B
AXP202_HOTOVER_CTL = 0x8F
AXP202_GPIO0_CTL = 0x90
AXP202_GPIO0_VOL = 0x91
AXP202_GPIO1_CTL = 0x92
AXP202_GPIO2_CTL = 0x93
AXP202_GPIO012_SIGNAL = 0x94
AXP202_GPIO3_CTL = 0x95
AXP202_INTEN1 = 0x40
AXP202_INTEN2 = 0x41
AXP202_INTEN3 = 0x42
AXP202_INTEN4 = 0x43
AXP202_INTEN5 = 0x44
AXP202_INTSTS1 = 0x48
AXP202_INTSTS2 = 0x49
AXP202_INTSTS3 = 0x4A
AXP202_INTSTS4 = 0x4B
AXP202_INTSTS5 = 0x4C

# Irq control register
AXP192_INTEN1 = 0x40
AXP192_INTEN2 = 0x41
AXP192_INTEN3 = 0x42
AXP192_INTEN4 = 0x43
AXP192_INTEN5 = 0x4A

# Irq status register
AXP192_INTSTS1 = 0x44
AXP192_INTSTS2 = 0x45
AXP192_INTSTS3 = 0x46
AXP192_INTSTS4 = 0x47
AXP192_INTSTS5 = 0x4D

AXP192_LDO23OUT_VOL  = 0x28
AXP192_DC1_VLOTAGE = 0x26

# axp 20 adc data register
AXP202_BAT_AVERVOL_H8 = 0x78
AXP202_BAT_AVERVOL_L4 = 0x79
AXP202_BAT_AVERCHGCUR_H8 = 0x7A
AXP202_BAT_AVERCHGCUR_L4 = 0x7B
AXP202_BAT_VOL_H8 = 0x50
AXP202_BAT_VOL_L4 = 0x51
AXP202_ACIN_VOL_H8 = 0x56
AXP202_ACIN_VOL_L4 = 0x57
AXP202_ACIN_CUR_H8 = 0x58
AXP202_ACIN_CUR_L4 = 0x59
AXP202_VBUS_VOL_H8 = 0x5A
AXP202_VBUS_VOL_L4 = 0x5B
AXP202_VBUS_CUR_H8 = 0x5C
AXP202_VBUS_CUR_L4 = 0x5D
AXP202_INTERNAL_TEMP_H8 = 0x5E
AXP202_INTERNAL_TEMP_L4 = 0x5F
AXP202_TS_IN_H8 = 0x62
AXP202_TS_IN_L4 = 0x63
AXP202_GPIO0_VOL_ADC_H8 = 0x64
AXP202_GPIO0_VOL_ADC_L4 = 0x65
AXP202_GPIO1_VOL_ADC_H8 = 0x66
AXP202_GPIO1_VOL_ADC_L4 = 0x67

AXP202_BAT_AVERDISCHGCUR_H8 = 0x7C
AXP202_BAT_AVERDISCHGCUR_L5 = 0x7D
AXP202_APS_AVERVOL_H8 = 0x7E
AXP202_APS_AVERVOL_L4 = 0x7F
AXP202_INT_BAT_CHGCUR_H8 = 0xA0
AXP202_INT_BAT_CHGCUR_L4 = 0xA1
AXP202_EXT_BAT_CHGCUR_H8 = 0xA2
AXP202_EXT_BAT_CHGCUR_L4 = 0xA3
AXP202_INT_BAT_DISCHGCUR_H8 = 0xA4
AXP202_INT_BAT_DISCHGCUR_L4 = 0xA5
AXP202_EXT_BAT_DISCHGCUR_H8 = 0xA6
AXP202_EXT_BAT_DISCHGCUR_L4 = 0xA7
AXP202_BAT_CHGCOULOMB3 = 0xB0
AXP202_BAT_CHGCOULOMB2 = 0xB1
AXP202_BAT_CHGCOULOMB1 = 0xB2
AXP202_BAT_CHGCOULOMB0 = 0xB3
AXP202_BAT_DISCHGCOULOMB3 = 0xB4
AXP202_BAT_DISCHGCOULOMB2 = 0xB5
AXP202_BAT_DISCHGCOULOMB1 = 0xB6
AXP202_BAT_DISCHGCOULOMB0 = 0xB7
AXP202_COULOMB_CTL = 0xB8
AXP202_BAT_POWERH8 = 0x70
AXP202_BAT_POWERM8 = 0x71
AXP202_BAT_POWERL8 = 0x72

AXP202_VREF_TEM_CTRL = 0xF3
AXP202_BATT_PERCENTAGE = 0xB9


# AXP202   bit definitions for AXP events irq event
AXP202_IRQ_USBLO = 1
AXP202_IRQ_USBRE = 2
AXP202_IRQ_USBIN = 3
AXP202_IRQ_USBOV = 4
AXP202_IRQ_ACRE = 5
AXP202_IRQ_ACIN = 6
AXP202_IRQ_ACOV = 7

AXP202_IRQ_TEMLO = 8
AXP202_IRQ_TEMOV = 9
AXP202_IRQ_CHAOV = 10
AXP202_IRQ_CHAST = 11
AXP202_IRQ_BATATOU = 12
AXP202_IRQ_BATATIN = 13
AXP202_IRQ_BATRE = 14
AXP202_IRQ_BATIN = 15

AXP202_IRQ_POKLO = 16
AXP202_IRQ_POKSH = 17
AXP202_IRQ_LDO3LO = 18
AXP202_IRQ_DCDC3LO = 19
AXP202_IRQ_DCDC2LO = 20
AXP202_IRQ_CHACURLO = 22
AXP202_IRQ_ICTEMOV = 23

AXP202_IRQ_EXTLOWARN2 = 24
AXP202_IRQ_EXTLOWARN1 = 25
AXP202_IRQ_SESSION_END = 26
AXP202_IRQ_SESS_AB_VALID = 27
AXP202_IRQ_VBUS_UN_VALID = 28
AXP202_IRQ_VBUS_VALID = 29
AXP202_IRQ_PDOWN_BY_NOE = 30
AXP202_IRQ_PUP_BY_NOE = 31

AXP202_IRQ_GPIO0TG = 32
AXP202_IRQ_GPIO1TG = 33
AXP202_IRQ_GPIO2TG = 34
AXP202_IRQ_GPIO3TG = 35
AXP202_IRQ_PEKFE = 37
AXP202_IRQ_PEKRE = 38
AXP202_IRQ_TIMER = 39


# Signal Capture
AXP202_BATT_VOLTAGE_STEP = 1.1
AXP202_BATT_DISCHARGE_CUR_STEP = 0.5
AXP202_BATT_CHARGE_CUR_STEP = 0.5
AXP202_ACIN_VOLTAGE_STEP = 1.7
AXP202_ACIN_CUR_STEP = 0.625
AXP202_VBUS_VOLTAGE_STEP = 1.7
AXP202_VBUS_CUR_STEP = 0.375
AXP202_INTENAL_TEMP_STEP = 0.1
AXP202_APS_VOLTAGE_STEP = 1.4
AXP202_TS_PIN_OUT_STEP = 0.8
AXP202_GPIO0_STEP = 0.5
AXP202_GPIO1_STEP = 0.5

# axp202 power channel
AXP202_EXTEN = 0
AXP202_DCDC3 = 1
AXP202_LDO2 = 2
AXP202_LDO4 = 3
AXP202_DCDC2 = 4
AXP202_LDO3 = 6

# axp192 power channel
AXP192_DCDC1 = 0
AXP192_DCDC3 = 1
AXP192_LDO2 = 2
AXP192_LDO3 = 3
AXP192_DCDC2 = 4
AXP192_EXTEN = 6

# AXP202 ADC channel
AXP202_ADC1 = 1
AXP202_ADC2 = 2


# axp202 adc1 args
AXP202_BATT_VOL_ADC1 = 7
AXP202_BATT_CUR_ADC1 = 6
AXP202_ACIN_VOL_ADC1 = 5
AXP202_ACIN_CUR_ADC1 = 4
AXP202_VBUS_VOL_ADC1 = 3
AXP202_VBUS_CUR_ADC1 = 2
AXP202_APS_VOL_ADC1 = 1
AXP202_TS_PIN_ADC1 = 0

# axp202 adc2 args
AXP202_TEMP_MONITORING_ADC2 = 7
AXP202_GPIO1_FUNC_ADC2 = 3
AXP202_GPIO0_FUNC_ADC2 = 2


# AXP202 IRQ1
AXP202_VBUS_VHOLD_LOW_IRQ = 1 << 1
AXP202_VBUS_REMOVED_IRQ = 1 << 2
AXP202_VBUS_CONNECT_IRQ = 1 << 3
AXP202_VBUS_OVER_VOL_IRQ = 1 << 4
AXP202_ACIN_REMOVED_IRQ = 1 << 5
AXP202_ACIN_CONNECT_IRQ = 1 << 6
AXP202_ACIN_OVER_VOL_IRQ = 1 << 7

# AXP202 IRQ2
AXP202_BATT_LOW_TEMP_IRQ = 1 << 8
AXP202_BATT_OVER_TEMP_IRQ = 1 << 9
AXP202_CHARGING_FINISHED_IRQ = 1 << 10
AXP202_CHARGING_IRQ = 1 << 11
AXP202_BATT_EXIT_ACTIVATE_IRQ = 1 << 12
AXP202_BATT_ACTIVATE_IRQ = 1 << 13
AXP202_BATT_REMOVED_IRQ = 1 << 14
AXP202_BATT_CONNECT_IRQ = 1 << 15

# AXP202 IRQ3
AXP202_PEK_LONGPRESS_IRQ = 1 << 16
AXP202_PEK_SHORTPRESS_IRQ = 1 << 17
AXP202_LDO3_LOW_VOL_IRQ = 1 << 18
AXP202_DC3_LOW_VOL_IRQ = 1 << 19
AXP202_DC2_LOW_VOL_IRQ = 1 << 20
AXP202_CHARGE_LOW_CUR_IRQ = 1 << 21
AXP202_CHIP_TEMP_HIGH_IRQ = 1 << 22

# AXP202 IRQ4
AXP202_APS_LOW_VOL_LEVEL2_IRQ = 1 << 24
APX202_APS_LOW_VOL_LEVEL1_IRQ = 1 << 25
AXP202_VBUS_SESSION_END_IRQ = 1 << 26
AXP202_VBUS_SESSION_AB_IRQ = 1 << 27
AXP202_VBUS_INVALID_IRQ = 1 << 28
AXP202_VBUS_VAILD_IRQ = 1 << 29
AXP202_NOE_OFF_IRQ = 1 << 30
AXP202_NOE_ON_IRQ = 1 << 31
AXP202_ALL_IRQ = 0xFFFF

# AXP202 LDO3 Mode
AXP202_LDO3_LDO_MODE = 0
AXP202_LDO3_DCIN_MODE = 1

# AXP202 LDO4 voltage setting args
AXP202_LDO4_1250MV = 0
AXP202_LDO4_1300MV = 1
AXP202_LDO4_1400MV = 2
AXP202_LDO4_1500MV = 3
AXP202_LDO4_1600MV = 4
AXP202_LDO4_1700MV = 5
AXP202_LDO4_1800MV = 6
AXP202_LDO4_1900MV = 7
AXP202_LDO4_2000MV = 8
AXP202_LDO4_2500MV = 9
AXP202_LDO4_2700MV = 10
AXP202_LDO4_2800MV = 11
AXP202_LDO4_3000MV = 12
AXP202_LDO4_3100MV = 13
AXP202_LDO4_3200MV = 14
AXP202_LDO4_3300MV = 15


# Boot time setting
AXP202_STARTUP_TIME_128MS = 0
AXP202_STARTUP_TIME_3S = 1
AXP202_STARTUP_TIME_1S = 2
AXP202_STARTUP_TIME_2S = 3


# Long button time setting
AXP202_LONGPRESS_TIME_1S = 0
AXP202_LONGPRESS_TIME_1S5 = 1
AXP202_LONGPRESS_TIME_2S = 2
AXP202_LONGPRESS_TIME_2S5 = 3


# Shutdown duration setting
AXP202_SHUTDOWN_TIME_4S = 0
AXP202_SHUTDOWN_TIME_6S = 1
AXP202_SHUTDOWN_TIME_8S = 2
AXP202_SHUTDOWN_TIME_10S = 3


# REG 33H: Charging control 1 Charging target-voltage setting
AXP202_TARGET_VOL_4_1V = 0
AXP202_TARGET_VOL_4_15V = 1
AXP202_TARGET_VOL_4_2V = 2
AXP202_TARGET_VOL_4_36V = 3

# AXP202 LED CONTROL
AXP20X_LED_OFF = 0
AXP20X_LED_BLINK_1HZ = 1
AXP20X_LED_BLINK_4HZ = 2
AXP20X_LED_LOW_LEVEL = 3


class PMU(object):
    def __init__(self, i2c=None, scl=None, sda=None,
                 intr=None, address=None):
        self.device = None
        self.bus = i2c
        if self.bus is None:
            self.scl = scl if scl is not None else default_pin_scl
            self.sda = sda if sda is not None else default_pin_sda

        self.intr = intr if intr is not None else default_pin_intr
        self.chip = default_chip_type
        self.address = address if address else AXP202_SLAVE_ADDRESS

        self.buffer = bytearray(16)
        self.bytebuf = memoryview(self.buffer[0:1])
        self.wordbuf = memoryview(self.buffer[0:2])
        self.irqbuf = memoryview(self.buffer[0:5])

        self.init_pins()
        if self.bus is None:
            self.init_i2c()

        self.init_device()

    def init_i2c(self):
        if self.bus is None:
            print('* initializing i2c')
            self.bus = SoftI2C(scl=self.pin_scl, sda=self.pin_sda)

    def init_pins(self):
        print('* initializing pins')
        if self.bus is None:
            self.pin_sda = Pin(self.sda)
            self.pin_scl = Pin(self.scl)
        self.pin_intr = Pin(self.intr, mode=Pin.IN)

    def write_byte(self, reg, val):
        self.bytebuf[0] = val
        self.bus.writeto_mem(self.address, reg, self.bytebuf)

    def read_byte(self, reg):
        self.bus.readfrom_mem_into(self.address, reg, self.bytebuf)
        return self.bytebuf[0]

    def read_word(self, reg):
        self.bus.readfrom_mem_into(self.address, reg, self.wordbuf)
        return unpack('>H', self.wordbuf)[0]

    def read_word2(self, reg):
        self.bus.readfrom_mem_into(self.address, reg, self.wordbuf)
        return unpack('>h', self.wordbuf)[0]

    def init_device(self):
        print('* initializing mpu')
        self.chip = self.read_byte(AXP202_IC_TYPE)
        if(self.chip == AXP202_CHIP_ID):
            self.chip = AXP202_CHIP_ID
            print("* Detect PMU Type is AXP202")
        elif(self.chip == AXP192_CHIP_ID):
            print("* Detect PMU Type is AXP192")
            self.chip = AXP192_CHIP_ID
        else:
            raise Exception("Invalid Chip ID!")

    def enablePower(self, ch):
        data = self.read_byte(AXP202_LDO234_DC23_CTL)
        data = data | (1 << ch)
        self.write_byte(AXP202_LDO234_DC23_CTL, data)

    def disablePower(self, ch):
        data = self.read_byte(AXP202_LDO234_DC23_CTL)
        data = data & (~(1 << ch))
        self.write_byte(AXP202_LDO234_DC23_CTL, data)

    def __BIT_MASK(self, mask):
        return 1 << mask

    def __get_h8_l5(self, regh8, regl5):
        hv = self.read_byte(regh8)
        lv = self.read_byte(regl5)
        return (hv << 5) | (lv & 0x1F)

    def __get_h8_l4(self, regh8, regl5):
        hv = self.read_byte(regh8)
        lv = self.read_byte(regl5)
        return (hv << 4) | (lv & 0xF)

    def isChargeing(self):
        data = self.read_byte(AXP202_MODE_CHGSTATUS)
        return data & self.__BIT_MASK(6)

    def isBatteryConnect(self):
        data = self.read_byte(AXP202_MODE_CHGSTATUS)
        return data & self.__BIT_MASK(5)

    def getAcinCurrent(self):
        data = self.__get_h8_l4(AXP202_ACIN_CUR_H8, AXP202_ACIN_CUR_L4)
        return data * AXP202_ACIN_CUR_STEP

    def getAcinVoltage(self):
        data = self.__get_h8_l4(AXP202_ACIN_VOL_H8, AXP202_ACIN_VOL_L4)
        return data * AXP202_ACIN_VOLTAGE_STEP

    def getVbusVoltage(self):
        data = self.__get_h8_l4(AXP202_VBUS_VOL_H8, AXP202_VBUS_VOL_L4)
        return data * AXP202_VBUS_VOLTAGE_STEP

    def getVbusCurrent(self):
        data = self.__get_h8_l4(AXP202_VBUS_CUR_H8, AXP202_VBUS_CUR_L4)
        return data * AXP202_VBUS_CUR_STEP

    def getTemp(self):
        hv = self.read_byte(AXP202_INTERNAL_TEMP_H8)
        lv = self.read_byte(AXP202_INTERNAL_TEMP_L4)
        data = (hv << 8) | (lv & 0xF)
        return data / 1000

    def getTSTemp(self):
        data = self.__get_h8_l4(AXP202_TS_IN_H8, AXP202_TS_IN_L4)
        return data * AXP202_TS_PIN_OUT_STEP

    def getGPIO0Voltage(self):
        data = self.__get_h8_l4(AXP202_GPIO0_VOL_ADC_H8,
                                AXP202_GPIO0_VOL_ADC_L4)
        return data * AXP202_GPIO0_STEP

    def getGPIO1Voltage(self):
        data = self.__get_h8_l4(AXP202_GPIO1_VOL_ADC_H8,
                                AXP202_GPIO1_VOL_ADC_L4)
        return data * AXP202_GPIO1_STEP

    def getBattInpower(self):
        h8 = self.read_byte(AXP202_BAT_POWERH8)
        m8 = self.read_byte(AXP202_BAT_POWERM8)
        l8 = self.read_byte(AXP202_BAT_POWERL8)
        data = (h8 << 16) | (m8 << 8) | l8
        return 2 * data * 1.1 * 0.5 / 1000

    def getBattVoltage(self):
        data = self.__get_h8_l4(AXP202_BAT_AVERVOL_H8, AXP202_BAT_AVERVOL_L4)
        return data * AXP202_BATT_VOLTAGE_STEP

    def getBattChargeCurrent(self):
        data = 0
        if(self.chip == AXP202_CHIP_ID):
            data = self.__get_h8_l4(
                AXP202_BAT_AVERCHGCUR_H8, AXP202_BAT_AVERCHGCUR_L4) * AXP202_BATT_CHARGE_CUR_STEP
        elif (self.chip == AXP192_CHIP_ID):
            data = self.__get_h8_l5(
                AXP202_BAT_AVERCHGCUR_H8, AXP202_BAT_AVERCHGCUR_L4) * AXP202_BATT_CHARGE_CUR_STEP
        return data

    def getBattDischargeCurrent(self):
        data = self.__get_h8_l4(
            AXP202_BAT_AVERDISCHGCUR_H8, AXP202_BAT_AVERDISCHGCUR_L5) * AXP202_BATT_DISCHARGE_CUR_STEP
        return data

    def getSysIPSOUTVoltage(self):
        hv = self.read_byte(AXP202_APS_AVERVOL_H8)
        lv = self.read_byte(AXP202_APS_AVERVOL_L4)
        data = (hv << 4) | (lv & 0xF)
        return data

    def enableADC(self, ch, val):
        if(ch == 1):
            data = self.read_byte(AXP202_ADC_EN1)
            data = data | (1 << val)
            self.write_byte(AXP202_ADC_EN1, data)
        elif(ch == 2):
            data = self.read_byte(AXP202_ADC_EN2)
            data = data | (1 << val)
            self.write_byte(AXP202_ADC_EN1, data)
        else:
            return

    def disableADC(self, ch, val):
        if(ch == 1):
            data = self.read_byte(AXP202_ADC_EN1)
            data = data & (~(1 << val))
            self.write_byte(AXP202_ADC_EN1, data)
        elif(ch == 2):
            data = self.read_byte(AXP202_ADC_EN2)
            data = data & (~(1 << val))
            self.write_byte(AXP202_ADC_EN1, data)
        else:
            return

    def enableIRQ(self, val):
        if(val & 0xFF):
            data = self.read_byte(AXP202_INTEN1)
            data = data | (val & 0xFF)
            self.write_byte(AXP202_INTEN1, data)

        if(val & 0xFF00):
            data = self.read_byte(AXP202_INTEN2)
            data = data | (val >> 8)
            self.write_byte(AXP202_INTEN2, data)

        if(val & 0xFF0000):
            data = self.read_byte(AXP202_INTEN3)
            data = data | (val >> 16)
            self.write_byte(AXP202_INTEN3, data)

        if(val & 0xFF000000):
            data = self.read_byte(AXP202_INTEN4)
            data = data | (val >> 24)
            self.write_byte(AXP202_INTEN4, data)

    def disableIRQ(self, val):
        if(val & 0xFF):
            data = self.read_byte(AXP202_INTEN1)
            data = data & (~(val & 0xFF))
            self.write_byte(AXP202_INTEN1, data)

        if(val & 0xFF00):
            data = self.read_byte(AXP202_INTEN2)
            data = data & (~(val >> 8))
            self.write_byte(AXP202_INTEN2, data)

        if(val & 0xFF0000):
            data = self.read_byte(AXP202_INTEN3)
            data = data & (~(val >> 16))
            self.write_byte(AXP202_INTEN3, data)

        if(val & 0xFF000000):
            data = self.read_byte(AXP202_INTEN4)
            data = data & (~(val >> 24))
            self.write_byte(AXP202_INTEN4, data)
        pass

    def readIRQ(self):
        if(self.chip == AXP202_CHIP_ID):
            for i in range(5):
                self.irqbuf[i] = self.read_byte(AXP202_INTSTS1 + i)
        elif(self.chip == AXP192_CHIP_ID):
            for i in range(4):
                self.irqbuf[i] = self.read_byte(AXP192_INTSTS1 + i)

            self.irqbuf[4] = self.read_byte(AXP192_INTSTS5)

    def clearIRQ(self):
        if(self.chip == AXP202_CHIP_ID):
            for i in range(5):
                self.write_byte(AXP202_INTSTS1 + i, 0xFF)
                self.irqbuf[i] = 0
        elif(self.chip == AXP192_CHIP_ID):
            for i in range(4):
                self.write_byte(AXP192_INTSTS1 + i, 0xFF)
            self.write_byte(AXP192_INTSTS5, 0xFF)

    def isVBUSPlug(self):
        data = self.read_byte(AXP202_STATUS)
        return data & self.__BIT_MASK(5)

    # Only can set axp192
    def setDC1Voltage(self, mv):
        if(self.chip != AXP192_CHIP_ID):
            return
        if(mv < 700):
            mv = 700
        elif(mv > 3500):
            mv = 3500
        val = (mv - 700) / 25
        self.write_byte(AXP192_DC1_VLOTAGE, int(val))

    def setDC2Voltage(self, mv):
        if(mv < 700):
            mv = 700
        elif(mv > 3500):
            mv = 3500
        val = (mv - 700) / 25
        self.write_byte(AXP202_DC2OUT_VOL, int(val))

    def setDC3Voltage(self, mv):
        if(mv < 700):
            mv = 700
        elif(mv > 3500):
            mv = 3500
        val = (mv - 700) / 25
        self.write_byte(AXP202_DC3OUT_VOL, int(val))

    def setLDO2Voltage(self, mv):
        if(mv < 1800):
            mv = 1800
        elif(mv > 3300):
            mv = 3300
        val = (mv - 1800) / 100
        prev = self.read_byte(AXP202_LDO24OUT_VOL)
        prev &= 0x0F
        prev = prev | (int(val) << 4)
        self.write_byte(AXP202_LDO24OUT_VOL, int(prev))

    def setLDO3Voltage(self, mv):
        if self.chip == AXP202_CHIP_ID and mv < 700:
            mv = 700
        elif self.chip == AXP192_CHIP_ID and mv < 1800:
            mv = 1800

        if self.chip == AXP202_CHIP_ID and mv > 3500:
            mv = 3500
        elif self.chip == AXP192_CHIP_ID and mv > 3300:
            mv = 3300

        if self.chip == AXP202_CHIP_ID:
            val = (mv - 700) / 25
            prev = self.read_byte(AXP202_LDO3OUT_VOL)
            prev &= 0x80
            prev = prev | int(val)
            self.write_byte(AXP202_LDO3OUT_VOL, int(prev))
            # self.write_byte(AXP202_LDO3OUT_VOL, int(val))
        elif self.chip == AXP192_CHIP_ID:
            val = (mv - 1800) / 100
            prev = self.read_byte(AXP192_LDO23OUT_VOL)
            prev &= 0xF0
            prev = prev | int(val)
            self.write_byte(AXP192_LDO23OUT_VOL, int(prev))

    def setLDO4Voltage(self, arg):
        data = self.read_byte(AXP202_LDO24OUT_VOL)
        data = data & 0xF0
        data = data | arg
        self.write_byte(AXP202_LDO24OUT_VOL, data)

    def setLDO3Mode(self, mode):
        if(mode > AXP202_LDO3_DCIN_MODE):
            return
        data = self.read_byte(AXP202_LDO3OUT_VOL)
        if(mode):
            data = data | self.__BIT_MASK(7)
        else:
            data = data & (~self.__BIT_MASK(7))
        self.write_byte(AXP202_LDO3OUT_VOL, data)

    def setStartupTime(self, val):
        startupParams = (
            0b00000000,
            0b01000000,
            0b10000000,
            0b11000000)
        if(val > AXP202_STARTUP_TIME_2S):
            return
        data = self.read_byte(AXP202_POK_SET)
        data = data & (~startupParams[3])
        data = data | startupParams[val]
        self.write_byte(AXP202_POK_SET, data)

    def setlongPressTime(self, val):
        longPressParams = (
            0b00000000,
            0b00010000,
            0b00100000,
            0b00110000)
        if(val > AXP202_LONGPRESS_TIME_2S5):
            return
        data = self.read_byte(AXP202_POK_SET)
        data = data & (~longPressParams[3])
        data = data | longPressParams[val]
        self.write_byte(AXP202_POK_SET, data)

    def setShutdownTime(self, val):
        shutdownParams = (
            0b00000000,
            0b00000001,
            0b00000010,
            0b00000011)
        if(val > AXP202_SHUTDOWN_TIME_10S):
            return
        data = self.read_byte(AXP202_POK_SET)
        data = data & (~shutdownParams[3])
        data = data | shutdownParams[val]
        self.write_byte(AXP202_POK_SET, data)

    def setTimeOutShutdown(self, en):
        data = self.read_byte(AXP202_POK_SET)
        if(en):
            data = data | self.__BIT_MASK(3)
        else:
            data = data | (~self.__BIT_MASK(3))
        self.write_byte(AXP202_POK_SET, data)

    def shutdown(self):
        data = self.read_byte(AXP202_OFF_CTL)
        data = data | self.__BIT_MASK(7)
        self.write_byte(AXP202_OFF_CTL, data)

    def getSettingChargeCurrent(self):
        data = self.read_byte(AXP202_CHARGE1)
        data = data & 0b00000111
        curr = 300 + data * 100
        return curr

    def isChargeingEnable(self):
        data = self.read_byte(AXP202_CHARGE1)
        if(data & self.__BIT_MASK(7)):
            return True
        return False

    def enableChargeing(self):
        data = self.read_byte(AXP202_CHARGE1)
        data = data | self.__BIT_MASK(7)
        self.write_byte(AXP202_CHARGE1, data)

    def setChargingTargetVoltage(self, val):
        targetVolParams = (
            0b00000000,
            0b00100000,
            0b01000000,
            0b01100000)
        if(val > AXP202_TARGET_VOL_4_36V):
            return
        data = self.read_byte(AXP202_CHARGE1)
        data = data & (~targetVolParams[3])
        data = data | targetVolParams[val]
        self.write_byte(AXP202_CHARGE1, data)

    def getBattPercentage(self):
        data = self.read_byte(AXP202_BATT_PERCENTAGE)
        mask = data & self.__BIT_MASK(7)
        if(mask):
            return 0
        return data & (~self.__BIT_MASK(7))

    def setChgLEDChgControl(self):
        data = self.read_byte(AXP202_OFF_CTL)
        data = data & 0b111110111
        self.write_byte(AXP202_OFF_CTL, data)

    def setChgLEDMode(self, mode):
        data = self.read_byte(AXP202_OFF_CTL)
        data |= self.__BIT_MASK(3)
        if(mode == AXP20X_LED_OFF):
            data = data & 0b11001111
        elif(mode == AXP20X_LED_BLINK_1HZ):
            data = data & 0b11001111
            data = data | 0b00010000
        elif(mode == AXP20X_LED_BLINK_4HZ):
            data = data & 0b11001111
            data = data | 0b00100000
        elif(mode == AXP20X_LED_LOW_LEVEL):
            data = data & 0b11001111
            data = data | 0b00110000
        self.write_byte(AXP202_OFF_CTL, data)
