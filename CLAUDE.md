# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repository contains MicroPython bindings for LVGL (Light and Versatile Graphics Library). It automatically generates Python bindings from LVGL C headers using the `gen_mpy.py` script, allowing LVGL to be used from MicroPython with native performance.

## Building and Integration

### As a MicroPython User Module

This module is typically used as a git submodule within a MicroPython project. The bindings are built automatically during the MicroPython build process.

**Build Integration:**
- **Make-based builds**: Uses `micropython.mk` with automatic binding generation
- **CMake-based builds**: Uses `micropython.cmake` and `mkrules_usermod.cmake`
- The build system automatically runs `gen/gen_mpy.py` to generate `lv_mpy.c` from LVGL headers

**Key Build Files:**
- `micropython.mk`: Make-based build rules and LVGL library integration
- `micropython.cmake`: CMake integration for ESP32/IDF and other platforms
- `lv_conf.h`: LVGL configuration (affects which bindings are generated)

### Building Standalone (for testing)

From a MicroPython repository with this as a user module:

```bash
# Unix port (for testing with SDL)
cd ports/unix
make USER_C_MODULES=/path/to/lv_binding_micropython/micropython.cmake
./build-lvgl/micropython

# ESP32 port
cd ports/esp32
make USER_C_MODULES=/path/to/lv_binding_micropython/micropython.cmake BOARD=ESP32_GENERIC
```

## Testing

### Automated Tests

**API Tests** (can be automated/CI):
```bash
# From micropython/tests directory
./run-tests.py ../../lib/lv_binding_micropython/tests/api/basic*.py -r .
```

**Display Tests** (visual feedback, no interaction):
```bash
# From micropython/tests directory  
./run-tests.py ../../lib/lv_binding_micropython/tests/display/basic*.py -r .
```

**Interactive Tests** (require user input):
```bash
# From micropython/tests directory
./run-tests.py ../../lib/lv_binding_micropython/tests/indev/basic*.py -r .
```

### Example Testing

Run all examples and demos:
```bash
cd tests
./run.sh
```

This runs all Python examples in parallel using GNU parallel, with 5-minute timeouts per test.

## Code Architecture

### Binding Generation System

**Core Components:**
- `gen/gen_mpy.py`: Main binding generator that parses LVGL headers and generates MicroPython C API
- `pycparser/`: Modified Python C parser for processing LVGL headers
- `lvgl/`: Git submodule containing the actual LVGL library

**Generation Process:**
1. C preprocessor processes LVGL headers with `lv_conf.h` settings
2. `gen_mpy.py` uses pycparser to parse the preprocessed headers
3. Generates `lv_mpy.c` containing MicroPython module definitions
4. Build system compiles everything into the MicroPython binary

### Driver Architecture

**Driver Locations:**
- `driver/esp32/`: ESP32-specific drivers (ILI9XXX, XPT2046, etc.)
- `driver/generic/`: Platform-independent Python drivers
- `driver/linux/`: Linux-specific drivers (evdev, etc.)
- `driver/stm32/`: STM32-specific drivers

**Driver Types:**
- **Pure Python**: Easiest to implement, runtime configurable
- **Pure C**: Best performance, requires rebuild for config changes  
- **Hybrid**: Critical parts in C, configuration in Python

### Memory Management

- LVGL is configured to use MicroPython's garbage collector
- Structs are automatically collected when no longer referenced
- **Important**: Screen objects (`lv.obj` with no parent) are not auto-collected - call `screen.delete()` explicitly
- Keep references to display and input drivers to prevent premature collection

### Callback System

**Callback Convention**: LVGL callbacks must follow specific patterns to work with MicroPython:
- Struct containing `void * user_data` field
- `user_data` passed as first argument to registration function and callback
- The binding automatically manages `user_data` for MicroPython callable objects

## Development Patterns

### Configuration Management

**Runtime Configuration**: Unlike typical LVGL C drivers, MicroPython drivers should allow runtime configuration:

```python
# Good - runtime configurable
from ili9XXX import ili9341
display = ili9341(dc=32, cs=33, mosi=23, clk=18)

# Avoid - requiring rebuild for pin changes
```

### Adding New Drivers

1. **Determine driver type** (Pure Python, C, or Hybrid)
2. **Follow existing patterns** in `driver/` subdirectories
3. **Make runtime configurable** - avoid hardcoded pins/settings
4. **Implement standard interface**:
   - Display drivers: `flush_cb` method or automatic setup
   - Input drivers: `read_cb` method or automatic setup

### Testing New Features

1. **Add API tests** in `tests/api/` for automated testing
2. **Add display tests** in `tests/display/` for visual verification  
3. **Follow existing test patterns** - see `tests/README.md`
4. **Test on multiple platforms** when possible

## Common Operations

### Regenerating Bindings

If you modify `lv_conf.h` or LVGL headers:
```bash
# Clean and rebuild to regenerate bindings
make clean
make USER_C_MODULES=/path/to/lv_binding_micropython/micropython.cmake
```

### Testing Configuration Changes

Use the examples to verify your changes:
```bash
# Run a simple test
./build-lvgl/micropython examples/example1.py

# Or run comprehensive tests
cd tests && ./run.sh
```

### Debugging Memory Issues

- Use `gc.collect()` to trigger garbage collection
- Call `screen.delete()` on screens when done
- Keep driver references in global variables or long-lived objects

## Integration Notes

- This module requires MicroPython's internal scheduler to be enabled
- LVGL task handler is called via `mp_sched_schedule` for screen refresh
- Single-threaded design - LVGL and MicroPython run on same thread
- Display drivers typically handle event loop setup automatically