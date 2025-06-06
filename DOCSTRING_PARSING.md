# LVGL Python Stub Generation with Documentation

The LVGL MicroPython bindings include comprehensive Python stub file generation with automatic docstring extraction from C headers. This provides full IDE support, autocompletion, and type hints for LVGL development in Python.

## Overview

**Key Features:**
- 🚀 **Fast Parallel Processing**: 6 seconds vs. minutes (uses all CPU cores)
- 📝 **Rich Documentation**: Automatic extraction from 1400+ LVGL functions  
- 🎯 **IDE Integration**: Full autocompletion and type hints (.pyi files)
- ⚡ **Separate Build**: Doesn't slow down main MicroPython builds
- 🔧 **Smart Formatting**: Bullet points, text wrapping, proper Python conventions

**Performance:**
- Processes 209 header files using parallel processing
- Extracts documentation from 1423 functions
- Generates type hints for 41 widget classes and 64 enums
- Uses all available CPU cores with progress feedback

## 1. **Source File Discovery**
```python
def load_lvgl_source_files(lvgl_dir):
    # Searches key LVGL directories:
    # - src/widgets/
    # - src/core/
    # - src/misc/
    # - src/draw/
    
    # Loads all .h files into memory as line arrays
    # Returns: {file_path: [line1, line2, ...]}
```

## 2. **Doxygen Comment Parsing**
```python
def parse_doxygen_comment(comment_text):
    # Input: Raw comment block from C header
    """
    /**
     * Set a new text for a label. Memory will be allocated to store the text by the label.
     * @param obj           pointer to a label object
     * @param text          '\0' terminated character string. NULL to refresh with the current text.
     */
    """
    
    # Output: Structured data
    {
        'description': 'Set a new text for a label. Memory will be allocated...',
        'params': [
            ('obj', 'pointer to a label object'),
            ('text', "'\\0' terminated character string. NULL to refresh...")
        ],
        'returns': None
    }
```

**Parsing Process:**
- Strips comment markers (`/**`, `*/`, `*`, `//`)
- Identifies `@param name description` patterns
- Handles `@return description` sections
- Supports multi-line descriptions
- Extracts main description text

**Implementation Note:** The Doxygen parsing is implemented using **custom regular expressions and string parsing** - no external documentation parsing libraries are used. This keeps the dependency footprint minimal while providing exactly the functionality needed for LVGL's documentation format.

## 3. **Function Documentation Lookup**
```python
def find_function_docs_in_sources(func_name, source_files):
    # For each source file:
    #   1. Search for function name pattern: "lv_label_set_text("
    #   2. Look backwards from function declaration
    #   3. Collect preceding comment block
    #   4. Parse with parse_doxygen_comment()
    
    # Example: "lv_label_set_text" finds docs in lv_label.h
```

## 4. **Python Docstring Generation**
```python
def format_python_docstring(func_name, doc_info, args_info):
    # Combines parsed docs with function signature info
    # Generates formatted Python docstring:
    
    """
    Set a new text for a label. Memory will be allocated to store the text by the label.
    
    Args:
        text (str): '\0' terminated character string. NULL to refresh with the current text.
    
    Returns:
        None
    """
```

**Formatting Rules:**
- Description comes first
- Args section with type hints: `param_name (type): description`
- Returns section when present
- Proper indentation and spacing

## 5. **Integration with Stub Generation**

**For Class Methods:**
```python
# 1. Look up documentation: "lv_label_set_text"
full_func_name = f"lv_{class_name}_{member_name}"
doc_info = find_function_docs_in_sources(full_func_name, source_files)

# 2. Generate stub with special handling
method_stub = generate_function_stub(member_name, member_info, doc_info, is_class_method=True)

# 3. Result:
def set_text(self: Self, text: str) -> None:
    """
    Set a new text for a label. Memory will be allocated to store the text by the label.
    
    Args:
        text (str): '\0' terminated character string. NULL to refresh with the current text.
    """
    ...
```

**For Regular Functions:**
```python
# Direct lookup and generation
doc_info = find_function_docs_in_sources(func_name, source_files)
stub = generate_function_stub(func_name, func_info, doc_info, is_class_method=False)
```

## 6. **Build System Integration**

**Separate Build Target (Fast):**
Since documentation parsing is slow (5-10 seconds), stub generation is now a separate optional target:

```bash
# Normal build (fast, no stubs):
make USER_C_MODULES=path/to/lvgl

# Generate Python stubs separately (slow, with documentation):
cd path/to/lvgl
python3 gen/gen_mpy.py -M lvgl -MP lv -S stubs_output_dir -E preprocessed_file.pp lvgl/lvgl.h
```

**Process Flow:**
1. Main build generates MicroPython bindings quickly (no documentation parsing)
2. Optional stub generation loads 200+ LVGL header files using parallel processing
3. Generator builds documentation index using multiple CPU cores  
4. For each function/method, looks up docs from pre-built index
5. Generates Python stubs with rich docstrings
6. Outputs `.pyi` files for IDE consumption

**Performance:**
- **Parallel Processing**: Uses all CPU cores to process header files simultaneously
- **Pre-indexing**: Builds function documentation index once, avoids repeated searches
- **Speed**: ~6 seconds for 209 files and 1423 functions (vs. minutes with old approach)

## 7. **Usage Examples**

### Generated Stub Content

**Class Methods with Documentation:**
```python
class label:
    def set_text(self: Self, text: str) -> None:
        """
        Set a new text for a label. Memory will be allocated to store the text by the label.
        
        Args:
            text (str): '\0' terminated character string. NULL to refresh with the current text.
        
        Source: src/widgets/label/lv_label.h:88
        """
        ...
    
    def get_scroll_x(self: Self) -> int:
        """
        Get current X scroll position. Identical to `lv_obj_get_scroll_left()`.
        
        Returns:
            current scroll position from left edge
            - If Widget is not scrolled return 0.
            - If scrolled return > 0.
            - If scrolled inside (elastic scroll) return < 0.
        
        Source: src/core/lv_obj_scroll.h:122
        """
        ...
```

**Module Functions:**
```python
def task_handler() -> int:
    """
    Call it periodically to handle lv_timers and refresh the display.
    
    Returns:
        time till next timer should run
    
    Source: src/core/lv_timer.h:77
    """
    ...
```

### IDE Benefits

- **Autocompletion**: Full function and method suggestions
- **Type Hints**: Proper Python type annotations for all parameters
- **Documentation**: Rich docstrings with parameter descriptions
- **Source Navigation**: File:line references for quick access to C implementation
- **Error Prevention**: Type checking catches incorrect parameter types
- **Code Understanding**: Easy navigation between Python API and LVGL internals

## 8. **Key Features**

- **🚀 Performance**: Parallel processing using all CPU cores
- **📝 Automatic**: No manual documentation writing required  
- **🔍 Comprehensive**: Processes entire LVGL codebase (200+ headers)
- **🎯 Smart**: Handles class methods vs static methods appropriately
- **📊 Type-aware**: Converts C types to Python type hints
- **🎨 IDE-friendly**: Generates standard Python docstring format
- **🔗 Source Navigation**: File:line references to original C implementation
- **⚡ Custom Implementation**: Uses regex-based parsing, no external dependencies
- **🔧 Separate Build**: Optional target that doesn't slow down main builds

## 9. **Technical Details**

### Parallel Processing Architecture
- **ProcessPoolExecutor**: Distributes file processing across CPU cores
- **Progress Reporting**: Updates every 50 processed files
- **Graceful Fallback**: Falls back to serial processing if parallel fails
- **Pre-indexing**: Builds function documentation index once for O(1) lookups

### Doxygen Parsing Implementation
The Doxygen comment parsing is implemented entirely with Python's built-in `re` (regular expressions) module and string manipulation. Key parsing functions:

- `process_file_for_docs()`: Extract all function docs from a single file (parallel)
- `parse_doxygen_comment()`: Main parser using string splitting and pattern matching  
- `find_function_docs_in_sources()`: O(1) lookup in pre-built documentation index

### Source Reference Generation
- Captures source file path and line number during documentation extraction
- Cleans paths to show relative LVGL paths (e.g., `src/widgets/label/lv_label.h:88`)
- Adds `Source: file:line` reference at end of each docstring
- Uses 1-based line numbering for editor compatibility

### Supported Doxygen Tags
- `@param name description` - Function parameters
- `@return description` - Return value documentation (with bullet point formatting)
- Main description text (everything not starting with @)
- Multi-line descriptions for all sections with proper text wrapping

### File Processing
- Processes all `.h` files in LVGL source tree using parallel workers
- Handles UTF-8 encoding with fallback for problematic files
- Builds documentation index in memory for efficient lookup
- Gracefully handles missing or malformed documentation
- Progress feedback and timing information

## 10. **Development Impact**

The result is that Python developers get:
- **Full IDE autocompletion** for all LVGL functions and methods
- **Rich documentation** automatically extracted from C source comments
- **Source navigation** with direct file:line references to C implementation
- **Proper type hints** for better code quality and error prevention  
- **Fast build times** with documentation generation as separate optional step
- **Professional development experience** matching modern Python libraries

All this without requiring external documentation parsing libraries or manual documentation maintenance.