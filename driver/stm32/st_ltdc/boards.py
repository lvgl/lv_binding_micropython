# boards.py
class TEMPLATE:
    # LTDC
    RST_PIN  = "XX"   # RGB-Pin 40
    BL_PIN   = "XX"   # RGB-Pin 34
    FB_ADDR  = 0xC0000000
    # Touch (GT911)
    TP_RST_PIN = "XX"       # RGB-Pin 35
    TP_INT_PIN = "XX"       # RGB-Pin 39
    TP_I2C_NUM = 0          # 0 = soft I2C
    TP_SCL_PIN = "XX"       # RGB-Pin 38 - Only if TP_I2C_NUM = 0
    TP_SDA_PIN = "XX"       # RGB-Pin 36 - Only if TP_I2C_NUM = 0

class STM32H743_CORE_V10:
    # LTDC
    RST_PIN  = "E2"
    BL_PIN   = "H6"
    FB_ADDR  = 0xC0000000
    # Touch (GT911)
    TP_RST_PIN = "H7"
    TP_INT_PIN = "E3"
    TP_I2C_NUM = 4

class STM32H743_CORE_V13:
    # LTDC
    RST_PIN  = "D11"
    BL_PIN   = "D12"
    FB_ADDR  = 0xC0000000
    # Touch (GT911)
    TP_RST_PIN = "B14"
    TP_INT_PIN = "H7"
    TP_I2C_NUM = 0
    TP_SCL_PIN = "B12"
    TP_SDA_PIN = "B13"

class FK743M5_XIH6:
    # LTDC
    RST_PIN  = ""
    BL_PIN   = "H6"
    FB_ADDR  = 0xC0000000
    # Touch (GT911)
    TP_RST_PIN = "I10"
    TP_INT_PIN = "I11"
    TP_I2C_NUM = 0
    TP_SCL_PIN = "G3"
    TP_SDA_PIN = "G7"

class DEV190806042:
    # LTDC
    RST_PIN  = ""
    BL_PIN   = "B5"
    FB_ADDR  = 0xC0000000
    # Touch (GT911)
    TP_RST_PIN = "I8"
    TP_INT_PIN = "H7"
    TP_I2C_NUM = 0
    TP_SCL_PIN = "H6"
    TP_SDA_PIN = "G7"
