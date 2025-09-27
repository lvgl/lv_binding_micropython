# LVGL Type Stubs

This package provides type stubs for LVGL MicroPython bindings, enabling IDE autocompletion, type checking, and better development experience.

## Installation

### Development Installation

For development with the latest stubs:

```bash
pip install -e /path/to/lv_binding_micropython/stubs
```

### From Built Package

After building the stubs:

```bash
pip install lvgl-stubs
```

## Usage

Once installed, your IDE (VS Code, PyCharm, etc.) will automatically use these stubs for:

- Autocompletion
- Type checking with mypy
- Function signatures and documentation
- Parameter hints

## Building

The stubs are automatically generated from the LVGL C headers when running the MicroPython bindings build process. The generated `lvgl.pyi` file will be placed in the `lvgl-stubs/` directory.

## Requirements

- Python 3.8+
- Generated from LVGL C headers with Doxygen-style documentation