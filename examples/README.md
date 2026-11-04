# LVGL MicroPython Examples

This directory contains comprehensive examples demonstrating LVGL (Light and Versatile Graphics Library) usage with MicroPython bindings.

## Quick Start

All examples are compatible with LVGL v9 API. To run an example:

```bash
# Unix port (with SDL for GUI simulation)
cd /path/to/micropython/ports/unix
./build-lvgl/micropython /path/to/examples/example_name.py

# ESP32 port (upload to device)
# Copy the example to your ESP32 and run it
```

## Examples Overview

### Basic Examples

- **`generic-st77xx-with-xpt2046.py`**: Simple button example for ST77XX displays with XPT2046 touch
- **`fb_test.py`**: Linux framebuffer test with basic button and label
- **`example1.py`**: Comprehensive platform-agnostic example with display initialization
- **`example3.py`**: Multi-widget example with sliders, LEDs, buttons, and keyboard

### Advanced Examples

- **`advanced_demo.py`**: Complex multi-platform demo with themes, animations, and charts
- **`custom_widget_example.py`**: Custom widget class creation and theming
- **`uasyncio_example1.py`**: Async/await integration with LVGL using uasyncio

### Specialized Examples

- **`png_example.py`**: PNG image loading and display with drag functionality
- **`Dynamic_loading_font_example.py`**: Loading custom binary fonts for multiple languages

### Migration Guide

- **`LvglV8ToV9MigrationGuide.md`**: Comprehensive guide for migrating from LVGL v8 to v9 API

## Platform Support

Examples support multiple platforms:

- **Unix/Linux**: SDL-based simulation
- **ESP32**: With various display drivers (ILI9341, ST77XX)
- **STM32**: Built-in display support
- **Raspberry Pi Pico**: RP2 platform with SPI displays

## Display Driver Integration

Examples demonstrate integration with various display drivers:

- **ILI9341**: Common SPI TFT display
- **ST77XX**: ST7789/ST7735 family displays
- **SDL**: Cross-platform simulation
- **Framebuffer**: Linux framebuffer support

## Touch Input Support

Touch input examples include:

- **XPT2046**: Resistive touch controller
- **Built-in touch**: Platform-specific touch sensors
- **Mouse simulation**: SDL mouse input

## Key Features Demonstrated

### Widgets
- Buttons, labels, sliders, LEDs
- Text areas and keyboards
- Charts and progress indicators
- Images and custom graphics

### Event Handling
- Button clicks and touch events
- Value change events
- Custom event callbacks
- Async event processing

### Styling and Theming
- Custom styles and themes
- Color and gradient management
- Shadow and border effects
- Layout and alignment

### Advanced Features
- Custom widget creation
- Font loading and text rendering
- Image decoding (PNG)
- Animation systems
- Memory management

## Requirements

### Common Requirements
- MicroPython with LVGL bindings
- Appropriate display driver for your hardware
- Sufficient RAM for graphics operations

### Platform-Specific Requirements

**Unix/Linux:**
- SDL2 development libraries
- X11 or Wayland display server

**ESP32:**
- ESP-IDF or Arduino framework
- SPI display hardware
- Touch controller (optional)

**STM32:**
- STM32 development board with display
- Touch sensor support

## Error Handling

All examples include comprehensive error handling:
- Missing driver detection
- File loading failures
- Platform compatibility checks
- Graceful fallbacks when resources unavailable

## Best Practices

Examples demonstrate LVGL best practices:

1. **Proper initialization**: LVGL init before any operations
2. **Resource management**: Proper cleanup and memory management
3. **Cross-platform compatibility**: Platform detection and appropriate drivers
4. **Error handling**: Graceful failure modes
5. **Code organization**: Clear structure and documentation

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure all required drivers are available
2. **Display not showing**: Check display driver initialization
3. **Touch not working**: Verify touch driver configuration
4. **Memory errors**: Increase heap size or reduce graphics complexity

### Debug Tips

- Enable verbose output in examples for debugging
- Check LVGL configuration (lv_conf.h)
- Verify platform compatibility
- Test with simpler examples first

## Contributing

When adding new examples:

1. Follow existing code style and structure
2. Include comprehensive docstrings
3. Add error handling and platform detection
4. Update this README with new example descriptions
5. Test on multiple platforms when possible

## License

Examples are provided under the same license as the LVGL MicroPython bindings.