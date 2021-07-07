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

DELAY_MS=25
MAX_CHILDREN=100

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

member_name_cache = {}

def get_member_name(obj, value):
    try:
        return member_name_cache[id(obj)][id(value)]
    except KeyError:
        pass

    for member in dir(obj):
        if getattr(obj, member) == value:
            try:
                member_name_cache[id(obj)][id(value)] = member
            except KeyError:
                member_name_cache[id(obj)] = {id(value): member}
            return member

events = [lv.EVENT.SCROLL, lv.EVENT.CLICKED, lv.EVENT.VALUE_CHANGED, lv.EVENT.READY]

def exec_actions(obj, user_data):
    if obj.get_child_id() <= MAX_CHILDREN:
        obj_info = ''
        if hasattr(obj, 'get_text'):
            obj_info += ' text:"%s"' % obj.get_text()
        if hasattr(obj, 'get_value'):
            obj_info += ' value:"%s"' % obj.get_value()
        print('%s %s' % (obj, obj_info))
        for event in events:
            # print('\t%s' % get_member_name(lv.EVENT, event))
            lv.event_send(obj, event, None)
            time.sleep_ms(DELAY_MS)
            gc.collect()
    return lv.obj.TREE_WALK.NEXT

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
        lv.scr_act().tree_walk(exec_actions, None)

except:
    exc = sys.exc_info()
    print('ERROR! %s: %s\n%s' % (
        exc[0].__name__,
        exc[1],
        exc[2] if exc[2] else ''))

    sys.exit(255) # 255 to exit xargs

