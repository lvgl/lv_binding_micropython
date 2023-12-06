The testing system is designed to make things easy to do. It keeps all of the
boiler plate code hidden from the person writing the test. The testing framework
used is the builting unittests for CPython. MicroPython does not have any
ability to run tests so we needed to add that ability to it. How this is done
is by leveraging std_in and std_out of a subprocess that is running MicroPython.

There are some rules to follow.

All tests MUST be placed into the sub folder "micropy_tests". The tests are done
as a grouping so you have the ability to run multiple tests as a group if there
are tests that are reliant upon each other. Each test runs in ascending sorted
order. So if you have tests that need to be in a specific alignment I suggest
using numbers for the tests to keep them in line with each other. The same thing
goes for the test groups. Each individual test in a group has a few rules.
file naming is what we will go over. File names for tests MUST start with "test_"
There is one file that is needed and 2 that are optional. The required file MUST
end with "_micropy.py" This file contains the code that you want to run in
MicroPython. The other 2 files are a settings file and a results file. They MUST
have "_settings.py" and "_results.py" at the ends of the file names. see below
for an example

micropy_tests
    group_1_{name of test group}
        test_1_{name of test}_settings.py
        test_1_{name of test}_results.py
        test_1_{name of test}_micropy.py

        test_2_{name of test}_results.py
        test_2_{name of test}_micropy.py

        test_3_{name of test}_settings.py
        test_3_{name of test}_micropy.py

        test_4_{name of test}_micropy.py

    group_2_{name of test group}
        test_1_{name of test}_settings.py
        test_1_{name of test}_results.py
        test_1_{name of test}_micropy.py

        test_2_{name of test}_results.py
        test_2_{name of test}_micropy.py

        test_3_{name of test}_settings.py
        test_3_{name of test}_micropy.py

        test_4_{name of test}_micropy.py


My suggestion is to set up the tests so the first test is the micropython setup
code. Things that only run a single time and are not dependant on any other test.
Things like creating the flush function and the display, initilizing LVGL.. etc...

If you need to have the code loop calling the task handler I strongly recommend using
code similiar to what you see below.

```
import time

start_time = time.time_ns()

left_over = 0
while True:
    # user_code here
    curr_time = time.time_ns()
    new_amount = time.ticks_diff(curr_time, start_time) + left_over
    left_over = new_amount & 0x3E8
    new_amount >>= 12
    if new_amount:
        lv.tick_inc(new_amount)
        lv.task_handler()
        start_time = curr_time
```

This is because of the speed in which everything is going to be running. You
have to remember that this is not running on an MCU s it is going to run a
whole lot faster. LVGL only has millisecond precision when it comes to time.
Running at the speeds of a PC we need to provide better timekeeping. That is
what this loop does.

The absolute last line in the _micropy code file MUST be "#end" It must be on
its own line and there is no newline after it. This is because of an echo that
happens to std_out when the code is fed into std_in. that marker is what tells
us when the code has been fully entered into MicroPython


data is sent into MicroPython as if you were typing it into the repl. To
get data out it is as if you were reading it from the repl. So what needs to be
done is you print the data you want to get out. When you do this it needs to be
done as follows.

```
print(f'result_variable_name = {repr(data_to_be_output)}')
```
where "result_variable_name" is the name of the variable that holds the data
to be matched in the results file and "data_to_be_output" is the name of the
variable where the data is stored in the running code in MicroPython. You can
have as many variables output as you like during a test, there is no limit. For
organization I would keep it limited to 5 at most.

In the results file you are going to have a bunch of variables and data in those variables.
The data is what is supposed to be output. if what is sent from MicroPython does
not align the test will fail.

the results file is executed in CPython to set things up. This means you can
have running code in the file. anything that is not a variable that is supposed
to be processed MUST be prefixed with an underscore. This includes any prefixes.
Anything that is prefixed with an underscore will be remooved when the comparison
is done. So if it is not a result of a test prefix it with an underscore.

The settings file. This defines a couple of things for the test.

```
TEST_TYPE = 'image'
IMG_WIDTH = 800
IMG_HEIGHT = 480
TIMEOUT = 30000
WAIT = 0
DURATION = 1000
```

There are currently only 2 test types, one that looks for frame data from the
flush function and the other is image data. you only need to specify the "TEST_TYPE"
if you are capturing framebuffer data. This needs to be set to "image" if that is the case.
IMG_WIDTH and IMG_HEIGHT are only needed if TEST_TYPE has been set to "image" This is set to the
resolution you created the display as.

The actual test gets run in a thread, this is done so if the test hangs it doesn't
hang the testing system. To have this work there is a watchdog timer and if that
timer is not reset then the test will fail under the assumption it has gotten stuck.
That is what TIMEOUT does. This is the amount of time in milliseconds the test can run
for without having the watchdog reset.

WAIT stlls the test after sending the code to MicroPython. If you have something
like an animation that you want to let run before starting the test this is how you do it.
Set the WAIT to the duration of the animation and the test will wait before it starts to
let that animation run. WAIT is in milliseconds

DURATION. This is only used when the TEST_TYPE is set to "image". This is how
long in milliseconds to capture frame data for. The frame data is captured in
the flush function. it is then broken up into 512 byte chunks, the chunks and
turned into a string of hex code. the hex code is not delimited so every byte
of data is exactly 2 characters long. FF = 0xFF etc... Every frame that passes
through the frame buffer gets sent back. Each frame gets processed and is
turned into a  PNG. each frame gets added to an APNG (animated).
The APNG as well as each frames PNG gets saved to an artifacts folder. The RAW
RGB data is also saved as wlel into a bin (binary) file.

How you need to handle capturing frames in the results file is not that hard to do.
Use PIL (pillow, Python Imaging Library) to load a saved PNG of the frame data.

If you specify a result file that has a single variable named "FRAME" in it the
testing system will attempt to match any of the frames receioived with this one variable.
If it finds a match the test passes. Optionally you can specify specific frames by
setting the result variable name to 'FRAME{number}' where "{number}" is the number of the
frame you want to compare against.

any image files used MUST be in the test folder. This includes any files used by
in the running code by MicroPython. on the CPython side you can import additional
code into the results or setting files if needed. If it is user code then it must
be in the same folder. If it is a library then that library needs to be installed
into CPython prior to running the tests.

The test that currently exists I recommend looking over to see how the code is done
for the Micropython side of things and how the results file is done. This is only
for doing a frame buffer captuure but it will give you a general idea of how things work.

