#!/bin/bash

set -e # Exit on error

SCRIPT_PATH="`dirname \"$0\"`"

NUMCPUS=`grep -c ^processor /proc/cpuinfo`

TEST_PATH="$SCRIPT_PATH/../examples/*.py $SCRIPT_PATH/../lvgl/examples/"
EXCLUDE_PATH="$SCRIPT_PATH/../examples/fb_test.py $SCRIPT_PATH/../examples/uasyncio*.py"

EXCLUDE_FINDEXP=$(echo $EXCLUDE_PATH | sed "s/^\|[[:space:]]/ -and -not -path /g")

find $TEST_PATH -name "*.py" $EXCLUDE_FINDEXP |\
   parallel --max-args=1 --max-procs $NUMCPUS -I {} timeout 5m catchsegv $SCRIPT_PATH/../../../ports/unix/micropython-dev $SCRIPT_PATH/run_test.py {}

