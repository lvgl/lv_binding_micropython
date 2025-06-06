# LVGL MicroPython Development Notes

## Build Process and Current State

### Building LVGL MicroPython Bindings

**Quick Build Command:**
```bash
# From micropython root directory
make -j -C ports/unix USER_C_MODULES=$(pwd)/lib
```

**Testing the Build:**
```bash
# Basic functionality test
echo "import lvgl as lv; print('LVGL version:', lv.version_info())" | ./ports/unix/build-standard/micropython

# Widget availability test
echo "import lvgl as lv; print([name for name in dir(lv) if 'btn' in name or 'label' in name])" | ./ports/unix/build-standard/micropython
```

### Build Configuration

**Key Files:**
- `lib/lvgl/lv_conf.h` - Main LVGL configuration
- `lib/lvgl/micropython.mk` - Make-based build integration
- `lib/lvgl/micropython.cmake` - CMake build integration
- `lib/lvgl/gen/gen_mpy.py` - Binding generator script

**Build Process:**
1. C preprocessor processes LVGL headers with `lv_conf.h` settings
2. `gen_mpy.py` parses preprocessed headers using pycparser
3. Generates `lv_mpy.c` containing MicroPython module definitions
4. Build system compiles everything into MicroPython binary

**Current Build Settings:**
- Color depth: 16-bit (RGB565)
- Memory management: MicroPython garbage collector
- Operating system: None (single-threaded)
- Drawing engine: Software rendering
- Platform features: SDL2, FreeType, Linux framebuffer support

### Current Feature Status

**Enabled Widgets (from lv_conf.h):**
- ✅ Basic widgets: Button, Label, Slider, LED, Image
- ✅ Layout widgets: Arc, Bar, Chart, Canvas
- ✅ Input widgets: Checkbox, Dropdown, Keyboard, Textarea, Roller
- ✅ Container widgets: List, Menu, Tabview, Tileview, Window
- ✅ Display widgets: Calendar, Scale, Spinner, Table
- ✅ Advanced widgets: Animimg, Buttonmatrix, Msgbox, Span, Spinbox, Switch

**Enabled Features:**
- ✅ Flex and Grid layouts
- ✅ Default theme with light/dark mode support
- ✅ Font support: Montserrat 14, 16, 24
- ✅ Image decoders: PNG (lodepng), JPEG (tjpgd), GIF, QR codes, Barcodes
- ✅ File systems: Memory-mapped files (MEMFS)
- ✅ Styling and animations
- ✅ Event handling and callbacks
- ✅ Snapshot functionality

**Platform Support:**
- ✅ Unix/Linux (SDL2 for development)
- ✅ Linux framebuffer
- ✅ ESP32 (ILI9XXX displays, XPT2046 touch)
- ✅ STM32 (various displays)
- ✅ RP2 (Raspberry Pi Pico)
- ✅ FreeType font rendering

### Current Examples Analysis

**Basic Examples:**
- `example1.py` - Multi-platform display initialization
- `example3.py` - Basic widget showcase
- `fb_test.py` - Linux framebuffer with mouse

**Advanced Examples:**
- `advanced_demo.py` - Comprehensive GUI with animations, charts, custom styles
- `custom_widget_example.py` - Custom widget development
- `uasyncio_example1.py` - Async programming integration

**Specialized Examples:**
- `png_example.py` - Image handling
- `Dynamic_loading_font_example.py` - Font management
- Platform-specific driver examples

### Test Infrastructure

**Test Categories:**
- `tests/api/` - Automated API tests (can run in CI)
- `tests/display/` - Visual tests (require display)
- `tests/indev/` - Interactive tests (require user input)

**Test Runner:**
```bash
# Run all tests with timeout
cd lib/lvgl/tests && ./run.sh

# Run specific test category
cd tests && python run_test.py api/basic.py
```

### Memory Management

**Key Points:**
- LVGL uses MicroPython's garbage collector
- Structs are automatically collected when unreferenced
- **Important:** Screen objects (`lv.obj` with no parent) require explicit `screen.delete()` call
- Keep references to display and input drivers to prevent premature collection

### Current Limitations and Opportunities

**Missing Widget Examples:**
- Arc/Gauge dashboards
- Complex table implementations
- Advanced menu systems
- Canvas custom drawing
- Vector graphics

**Missing Advanced Features:**
- Vector graphics (ThorVG integration)
- Multi-language/i18n examples
- Performance profiling tools
- Complex gesture recognition
- Hardware acceleration examples

**Driver Improvements Needed:**
- More touch calibration tools
- Additional display driver examples
- Better hardware optimization examples

### Python Stub Files for IDE Support

**NEW FEATURE: Automatic Python stub (.pyi) file generation**

The LVGL bindings generator now automatically creates Python stub files that provide:
- Type hints for all LVGL functions and classes
- IDE autocompletion support
- Better development experience
- API documentation assistance

**Generated Stub Files:**
- `build-standard/lvgl/stubs/lvgl.pyi` - Complete module stub with all widgets, functions, and types

**Usage in IDE:**
1. Add the stubs directory to your IDE's Python path
2. Import LVGL as usual: `import lvgl as lv`
3. Enjoy full autocompletion and type checking

**Stub Generation:**
- Automatically triggered during build process
- Can be manually generated with: `gen_mpy.py -S <stubs_dir>`
- Updates whenever LVGL configuration changes

### Development Workflow

**Adding New Features:**
1. Check `lv_conf.h` for required feature flags
2. Test with basic examples first
3. Add comprehensive test cases
4. Document in examples directory
5. Update this notes file

**Testing Changes:**
1. Build: `make -j -C ports/unix USER_C_MODULES=$(pwd)/lib`
2. Quick test: Basic import and widget creation
3. Run test suite: `cd lib/lvgl/tests && ./run.sh`
4. Test on target hardware if applicable
5. **NEW:** Check generated stub files for API changes

**Code Style:**
- Follow existing LVGL Python patterns
- Use descriptive variable names
- Include error handling
- Document complex functionality
- Provide both basic and advanced examples

---
*Last updated: $(date)*