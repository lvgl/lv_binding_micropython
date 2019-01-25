
# Bindings for LittelvGL

## Micropython

Micropython Binding for lvgl (LittlelvGL) provides an automatically generated Micropython module with classes and functions that allow the user access much of the lvgl library.  
The module is generated automatically by the script [`gen_mpy.py`](https://github.com/littlevgl/lv_bindings/blob/master/micropython/gen_mpy.py).  
This script reads, preprocesses and parses lvgl header files, and generates a C file `lv_mpy.c` which defines the Micropython module (API) for accessing lvgl from Micropython.  
Micopython's build script (Makefile) should run `gen_mpy.py` automatically to generate and compile `lv_mpy.c`.

- If you would like to see an example of how a generated `lv_mpy.c` looks like, have a look at [`v_mpy_example.c`](https://github.com/littlevgl/lv_bindings/blob/master/micropython/lv_mpy_example.c). Note that it's only exported (non static) symbol is `mp_module_lvgl` which should be registered in Micropython as a module.  
- An example project that builds Micropython + lvgl + lvgl-bindings: [`lv_mpy`](https://github.com/littlevgl/lv_mpy)

It's worth noting that the Mircopython Bindings module (`lv_mpy.c`) is dependant on lvgl configuration. lvgl is configured by `lv_conf.h` where different objects and features could be enabled or disabled. lvgl bindings are generated only for the enabled objects and features. Changing `lv_conf.h` requires re running `gen_mpy.py`, therfore it's useful to run it automatically in the build script.

### Memory Management

When lvgl is built as a Micropython library, it is configured to allocate memory using Micropython memory allocation functions and take advantage of Micropython *Garbage Collection* ("gc").  
This means that structs allocated for lvgl use don't need to be deallocated explicitly, gc takes care of that.  
For this to work correctly, lvgl needs to be configured to use gc and to use Micropython's memory allocation functions, and also register all lvgl "root" global variables to Micropython's gc.

### Concurrency

This implementation of Micropython Bindings to lvgl assumes that Micropython and lvgl are running **on a single thread** and **on the same thread** (or alternatively, running without multithreading at all).  
No synchronization means (locks, mutexes) are taken.  
However, asynchronous calls to lvgl still take place in a few cases:

- When a callback is called. For example, when a button is clicked.
- When screen needs to be refreshed.

This is achieved by using the internal Micropython scheduler (that must be enabled), by calling `mp_sched_schedule`.  
`mp_sched_schedule` is called on the following occasions:

- When a callback is fired, within lv_mpy.c
- When screen need to be refreshed. lvgl expects the function `lv_task_handler` to be called periodically (see [lvgl/README.md#porting](https://github.com/littlevgl/lvgl/blob/6718decbb7b561b68e450203b83dff60ce3d802c/README.md#porting).  
Here is [an example](https://github.com/littlevgl/lv_mpy/blob/bc635700e4186f39763e5edee73660fbe1a27cd4/ports/unix/lv_mpy_hal.c#L28) of calling `lv_task_handler` with `mp_sched_schedule` for refreshing lvgl.  

With REPL (interactive console), when waiting for the user input, asynchronous events can also happen. In [this example](https://github.com/littlevgl/lv_mpy/blob/bc635700e4186f39763e5edee73660fbe1a27cd4/ports/unix/unix_mphal.c#L176) we just call `mp_handle_pending` periodically when waiting for a keypress. `mp_handle_pending` takes care of dispatching asynchronous events registered with `mp_sched_schedule`.

### Adding Micropython Bindings to a project

An example project of "Micropython + lvgl + Bindings" is [`lv_mpy`](https://github.com/littlevgl/lv_mpy).  
The following examples are taken from there:

- Add [`lv_bindings`](https://github.com/littlevgl/lv_bindings) as a sub-module under `lib`.
- Add `lv_conf.h` in `lib`
- Edit the Makefile to run `gen_mpy.py` and build its product automatically. Here is [an example](https://github.com/littlevgl/lv_mpy/blob/bc635700e4186f39763e5edee73660fbe1a27cd4/py/py.mk#L122).
- Register lvgl module in Micropython as a builtin module. [An example](https://github.com/littlevgl/lv_mpy/blob/bc635700e4186f39763e5edee73660fbe1a27cd4/ports/unix/mpconfigport.h#L233).
- Add lvgl roots to gc roots. [An example](https://github.com/littlevgl/lv_mpy/blob/bc635700e4186f39763e5edee73660fbe1a27cd4/ports/unix/mpconfigport.h#L301). Configure lvgl to use *Garbage Collection* by setting several `LV_MEM_CUSTOM_*` and `LV_GC_*` macros [example](https://github.com/littlevgl/lv_mpy/blob/bc635700e4186f39763e5edee73660fbe1a27cd4/lib/lv_conf.h#L28)
- Implement `lv_mp_init`. This function is called right after `import lvgl` and allows you to initialize the screen hardware (if you need to) and do some lvgl initializations such as registering a tick handler and schedule a call to `lv_task_handler`. [An example](https://github.com/littlevgl/lv_mpy/blob/bc635700e4186f39763e5edee73660fbe1a27cd4/ports/unix/lv_mpy_hal.c#L71)
- Something I forgot? Please let me know.


### gen_mpy.py syntax
```
usage: gen_mpy.py [-h] [-I <Include Path>] [-X <Object Name>]
                  input [input ...]

positional arguments:
  input

optional arguments:
  -h, --help            show this help message and exit
  -I <Include Path>, --include <Include Path>
                        Preprocesor include path
  -X <Object Name>, --exclude <Object Name>
                        Exclude lvgl object
```

Example: 

```
python ../../lib/lv_bindings/micropython/gen_mpy.py -X anim -X group -X task -I../../lib/berkeley-db-1.xx/PORT/include -I../../lib/lv_bindings/lvgl -I. -I../.. -Ibuild -I../../lib/mp-readline -I ../../lib/lv_bindings/micropython/pycparser/utils/fake_libc_include ../../lib/lv_bindings/lvgl/lvgl.h > ../../lib/lv_bindings/micropython/lv_mpy_example.c
```

## Micropython Bindings Usage

A simple example: [`advanced_demo.py`](https://github.com/littlevgl/lv_bindings/blob/master/micropython/advanced_demo.py).

#### Importing LittlelvGL
```python
import lvgl as lv
```

#### Creating an instance of a struct
```python
symbolstyle = lv.style_t(lv.style_plain)
```
symbolstyle would be an instance of `lv_style_t` initialized to the same value of `lv_style_plain`

#### Setting a field in a struct
```python
symbolstyle.text.color = lv.color_hex(0xffffff)
```
symbolstyle.text.color would be initialized to the color struct returned by `lv_color_hex`

#### Setting a nested struct using dict
```python
symbolstyle.text.color = {"red":0xff, "green":0xff, "blue":0xff}
```

#### Creating an instance of an object
```python
self.tabview = lv.tabview(lv.scr_act())
```
The first argument to an object constructor is the parent object, the second is which element to copy this element from

#### Calling an object method
```python
self.symbol.align(self, lv.ALIGN.CENTER,0,0)
```
In this example `lv.ALIGN` is an enum and `lv.ALIGN.CENTER` is an enum member (an integer value).

#### Using callbacks
```python
btn.set_action(lv.btn.ACTION.CLICK, lambda action,name=name: self.label.set_text('%s click' % name))
```
Currently the binding is limited to one callback per object.

#### Listing available functions/memebers/constants etc.
```python
print('\n'.join(dir(lvgl)))
print('\n'.join(dir(lvgl.btn)))
...
```




