# display_driver.py
from st_ltdc_utils import init_display
from display_conf import board, panel
disp, touch = init_display(panel, board)
