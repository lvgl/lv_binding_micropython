##############################################################################
# Run LVGL examples
# An example script should be provided as an argument.
#
# This script would:
# - Initialize LVGL and display
# - Read the example file
# - Chdir to the example file dir
# - Run the example
# - gc collect
# - Try to perform some actions such as sending click/value-changed events
#
# In case of an error, display the error and exit with code 255
# 255 was selected to stop xargs
#
##############################################################################

DELAY_MS=250

import sys
sys.path.append('') # See: https://github.com/micropython/micropython/issues/6419

import gc
import os
import re
import time
import lvgl as lv
import display_driver_utils

lv.init()
driver = display_driver_utils.driver()
scr = lv.scr_act()

##############################################################################

def send_event(*events):
    return ';'.join(['lv.event_send(%%s, lv.EVENT.%s, None)' % e for e in events])

actions = {
            lv.btn:         send_event('CLICKED'),
            lv.obj:         send_event('CLICKED', 'SCROLL'),
            lv.textarea:    send_event('READY'),

            lv.checkbox:    send_event('VALUE_CHANGED'),
            lv.slider:      send_event('VALUE_CHANGED'),
            lv.dropdown:    send_event('VALUE_CHANGED'),
            lv.obj:         send_event('VALUE_CHANGED'),
            lv.switch:      send_event('VALUE_CHANGED'),
            # lv.btnmatrix:   send_event('VALUE_CHANGED'), # need param?
            lv.roller:      send_event('VALUE_CHANGED'),
            lv.table:       send_event('VALUE_CHANGED'),
            # lv.msgbox:      send_event('VALUE_CHANGED'), # mbox.get_active_btn_text may be NULL
            lv.calendar:    send_event('VALUE_CHANGED'),
          }

##############################################################################

try:

    script = sys.argv[1]
    script_path = script[:script.rfind('/')] if script.find('/') >= 0 else '.'
    script_name = script[script.rfind('/')+1:] if script.find('/') >= 0 else script

    print('Running %s ...' % script)

    with open(script, 'r') as file:
        file_string = file.read()
        os.chdir(script_path)
        __file__ = script_name
        exec(file_string)
        time.sleep_ms(DELAY_MS)
        gc.collect()

        for action in actions:
            for g in globals():
                if eval('type(%s)' % g) == action:
                    cmd = actions[action] % g
                    print(cmd)
                    exec(cmd)
                    time.sleep_ms(DELAY_MS)
                    gc.collect()

except:
    exc = sys.exc_info()
    print('ERROR! %s: %s\n%s' % (
        exc[0].__name__,
        exc[1],
        exc[2] if exc[2] else ''))

    sys.exit(255) # 255 to exit xargs

