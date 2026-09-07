# display_conf.py
try:
    from board_config import BOARD, VERSION
except ImportError:
    BOARD = "STM32H7_CORE"
    VERSION = "V13"

try:
    from panel_config import PANEL
except ImportError:
    PANEL = "IPS1024x600"

if BOARD == "STM32H7_CORE":
    if VERSION == "V10":
        from boards import STM32H743_CORE_V10 as board
    elif VERSION == "V13":
        from boards import STM32H743_CORE_V13 as board
    else:
        raise ValueError("Unsupported VERSION: " + VERSION)
elif BOARD == "FK743M5-XIH6":
    from boards import FK743M5_XIH6 as board
elif BOARD == "DEV190806042":
    from boards import DEV190806042 as board
else:
    raise ValueError("Unsupported BOARD: " + BOARD)

if PANEL == "IPS1024x600":
    from panels import IPS1024x600 as panel
elif PANEL == "RGB043M2":
    from panels import RGB043M2 as panel
else:
    raise ValueError("Unsupported PANEL: " + PANEL)
