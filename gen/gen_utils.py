"""
Shared utilities for LVGL MicroPython binding generation.

This module contains common functions and constants used by both
gen_mpy.py and gen_stubs.py to ensure consistency.
"""

import re

# LVGL source directories to search for documentation
LVGL_DOC_SEARCH_DIRS = [
    "src/widgets",
    "src/core", 
    "src/misc",
    "src/draw",
]

def create_patterns(module_prefix, base_obj_name):
    """Create regex patterns for LVGL identifiers."""
    patterns = {
        'lv_func_pattern': re.compile(
            "^{prefix}_(.+)".format(prefix=module_prefix), re.IGNORECASE
        ),
        'lv_enum_name_pattern': re.compile(
            "^(ENUM_){{0,1}}({prefix}_){{0,1}}(.*)".format(prefix=module_prefix.upper())
        ),
        'lv_ext_pattern': re.compile("^{prefix}_([^_]+)_ext_t".format(prefix=module_prefix)),
        'lv_obj_pattern': re.compile(
            "^{prefix}_([^_]+)".format(prefix=module_prefix), re.IGNORECASE
        ),
        'lv_method_pattern': re.compile(
            "^{prefix}_[^_]+_(.+)".format(prefix=module_prefix), re.IGNORECASE
        ),
        'create_obj_pattern': re.compile("^{prefix}_(.+)_create$".format(prefix=module_prefix)),
        'lv_str_enum_pattern': re.compile(
            "^_?{prefix}_STR_(.+)".format(prefix=module_prefix.upper())
        ),
    }
    return patterns

def simplify_identifier(id, module_prefix="lv"):
    """Simplify C identifier for Python use."""
    lv_func_pattern = re.compile(
        "^{prefix}_(.+)".format(prefix=module_prefix), re.IGNORECASE
    )
    match_result = lv_func_pattern.match(id)
    return match_result.group(1) if match_result else id

def get_enum_name(enum, module_prefix="lv"):
    """Extract enum name from LVGL enum identifier."""
    lv_enum_name_pattern = re.compile(
        "^(ENUM_){{0,1}}({prefix}_){{0,1}}(.*)".format(prefix=module_prefix.upper())
    )
    match_result = lv_enum_name_pattern.match(enum)
    return match_result.group(3) if match_result else enum

def c_type_to_python_type(c_type):
    """Convert C types to Python type hints."""
    if not c_type:
        return "None"
    
    # Remove pointer and const qualifiers for basic mapping
    clean_type = c_type.replace("*", "").replace("const", "").strip()
    
    # Basic type mappings
    type_map = {
        "void": "None",
        "bool": "bool",
        "int": "int",
        "uint8_t": "int",
        "uint16_t": "int", 
        "uint32_t": "int",
        "int8_t": "int",
        "int16_t": "int",
        "int32_t": "int",
        "size_t": "int",
        "char": "str",
        "float": "float",
        "double": "float",
        "NoneType": "None",
    }
    
    if clean_type in type_map:
        return type_map[clean_type]
    elif clean_type.startswith("lv_"):
        # LVGL objects - keep the type name but remove lv_ prefix for Python
        if clean_type.endswith("_t"):
            return clean_type[3:-2]  # Remove "lv_" and "_t"
        return clean_type[3:]  # Remove "lv_"
    elif "*" in c_type:
        return "Any"  # Pointers become Any type
    else:
        return "Any"  # Unknown types

def find_function_docs_in_sources(func_name, doc_index):
    """Find documentation for a function in the source documentation index."""
    return doc_index.get(func_name) if doc_index else None

def sanitize_identifier(name):
    """Sanitize identifier to avoid Python reserved words."""
    # Python reserved words that need to be avoided
    reserved_words = {
        'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del', 
        'elif', 'else', 'except', 'exec', 'finally', 'for', 'from', 'global',
        'if', 'import', 'in', 'is', 'lambda', 'not', 'or', 'pass', 'print',
        'raise', 'return', 'try', 'while', 'with', 'yield', 'None', 'True', 'False'
    }
    
    if name in reserved_words:
        return name + "_"
    return name