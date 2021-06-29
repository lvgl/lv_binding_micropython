#!/bin/bash

set -e # Exit on error

SCRIPT_PATH="`dirname \"$0\"`"
find $SCRIPT_PATH/../lvgl/examples/ -name "*.py" |\
   xargs -I {} $SCRIPT_PATH/../../../ports/unix/micropython-dev $SCRIPT_PATH/run_test.py {}

