
### Tests:

- `api/`: These tests are to test MicroPython-LVGL bindings. They can be
automated/included in CI. 
To run from `micropython/tests`:
```
 ./run-tests.py ../../user_modules/lv_binding_micropython/tests/api/basic*.py -r .
```

- `display/`: These are to test the `api` + display driver. Intended for HIL
(Hardware in the loop) testing. Display only, no touch interface, touch is
automated and simulated in software.
To run from `micropython/tests`:
```
./run-tests.py ../../user_modules/lv_binding_micropython/tests/display/basic*.py -r .
```
e.g. in unix port a display will appear to provide visual feedback.


- `indev/`: These are to test the `display` + indev (touch) driver. Intended for
interactive HIL testing, e.g. they expect user input to complete the test. 

To run from `micropython/tests`:
```
./run-tests.py ../../user_modules/lv_binding_micropython/tests/indev/basic*.py -r .
```
e.g. in unix port a display will appear to allow user input.

All tests are intended/expected to be run both in desktop (unix port) and in devices with the same result.

For devices `testrunner.py`, `testdisplay.py` and `display_config.py` need to be
uploaded. Also for display/indev testing a `hwdisplay.py` with a display driver
called `display` is expected. This `display` driver is expected to have at least a 
```py

    def blit(self, x1, y1, w, h, buff):
```
method or handle the lv display setup by itself (e.g setting buffers, `flush_cb`, etc)

For interactive indev tests, it is required to have a 
```py

    def read_cb(self, indev, data):
```
method too, or handle indev creation by itself.
