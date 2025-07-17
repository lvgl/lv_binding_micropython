#!/usr/bin/env python3
"""
LVGL Python stub file generator.

This module generates Python stub files (.pyi) for LVGL MicroPython bindings,
providing type hints and documentation for IDE autocompletion and type checking.
"""

import argparse
import json
import os
import sys
import re
import textwrap
from typing import Dict, List, Optional, Any

# Add the current directory to the path so we can import gen_utils
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gen_utils import (
    c_type_to_python_type,
    simplify_identifier,
    get_enum_name,
    find_function_docs_in_sources,
    sanitize_identifier,
    LVGL_DOC_SEARCH_DIRS
)

def eprint(*args, **kwargs):
    """Print to stderr."""
    print(*args, file=sys.stderr, **kwargs)

def parse_doxygen_comment(comment_text):
    """Parse a Doxygen comment and extract description and parameters."""
    if not comment_text:
        return None
    
    # Remove comment markers and normalize whitespace
    lines = []
    for line in comment_text.split('\n'):
        # Remove /** */ and * prefixes
        line = line.strip()
        if line.startswith('/**'):
            line = line[3:].strip()
        elif line.startswith('*/'):
            continue
        elif line.startswith('*'):
            line = line[1:].strip()
        elif line.startswith('//'):
            line = line[2:].strip()
        
        if line:
            lines.append(line)
    
    if not lines:
        return None
    
    # Parse the content
    description_lines = []
    params = []
    returns = None
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if line.startswith('@param'):
            # Parse parameter: @param name description
            parts = line.split(None, 2)
            if len(parts) >= 3:
                param_name = parts[1]
                param_desc = parts[2]
                
                # Collect multi-line parameter descriptions
                i += 1
                while i < len(lines) and not lines[i].startswith('@'):
                    param_desc += ' ' + lines[i]
                    i += 1
                i -= 1  # Back up one since loop will increment
                
                params.append((param_name, param_desc.strip()))
            
        elif line.startswith('@return'):
            # Parse return: @return description
            returns = line[7:].strip()
            
            # Collect multi-line return descriptions
            i += 1
            while i < len(lines) and not lines[i].startswith('@'):
                next_line = lines[i].strip()
                if next_line.startswith('- '):
                    # Preserve bullet points with line breaks
                    returns += '\n' + next_line
                else:
                    # Regular continuation - join with space
                    returns += ' ' + next_line
                i += 1
            i -= 1  # Back up one since loop will increment
            
        elif not line.startswith('@'):
            # Regular description line
            description_lines.append(line)
        
        i += 1
    
    description = ' '.join(description_lines).strip() if description_lines else None
    
    return {
        'description': description,
        'params': params,
        'returns': returns
    }

def wrap_text(text, width=85, indent=0):
    """Wrap text to specified width with optional indentation."""
    if not text:
        return []
    
    # Split on existing newlines first
    paragraphs = text.split('\n')
    wrapped_lines = []
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            wrapped_lines.append('')
            continue
            
        # Wrap each paragraph
        wrapper = textwrap.TextWrapper(
            width=width,
            initial_indent=' ' * indent,
            subsequent_indent=' ' * indent,
            break_long_words=False,
            break_on_hyphens=False
        )
        wrapped_lines.extend(wrapper.wrap(paragraph))
    
    return wrapped_lines

def format_python_docstring(func_name, doc_info, args_info, c_func_name=None):
    """Format parsed documentation into a Python docstring."""
    if not doc_info:
        return None
    
    lines = []
    
    # Add description with text wrapping
    if doc_info.get('description'):
        desc_lines = wrap_text(doc_info['description'], width=85)
        lines.extend(desc_lines)
        lines.append('')
    
    # Add parameters section
    params_from_doc = {name: desc for name, desc in doc_info.get('params', [])}
    if args_info and (params_from_doc or any(arg.get('name') for arg in args_info)):
        lines.append('Args:')
        for arg in args_info:
            arg_name = arg.get('name', 'arg')
            arg_type = c_type_to_python_type(arg.get('type', 'Any'))
            
            # Get description from documentation
            param_desc = params_from_doc.get(arg_name, '')
            if param_desc:
                # Format parameter with proper indentation
                param_header = f'    {arg_name} ({arg_type}): '
                
                # Wrap the description text separately to maintain indentation
                desc_wrapper = textwrap.TextWrapper(
                    width=85,
                    initial_indent=param_header,
                    subsequent_indent=' ' * (len(param_header)),
                    break_long_words=False,
                    break_on_hyphens=False
                )
                wrapped_param_lines = desc_wrapper.wrap(param_desc)
                lines.extend(wrapped_param_lines)
            else:
                lines.append(f'    {arg_name} ({arg_type}): Parameter description not available.')
        lines.append('')
    
    # Add returns section with proper formatting
    if doc_info.get('returns'):
        lines.append('Returns:')
        # Split return description on periods and dashes for better formatting
        return_desc = doc_info["returns"]
        
        # Handle common patterns in LVGL return descriptions
        if '\n- ' in return_desc:
            # Handle newline-separated bullet points from preserved formatting
            parts = return_desc.split('\n')
            first_part = parts[0].strip()
            if first_part:
                wrapped_first = wrap_text(first_part, width=81, indent=4)
                lines.extend(wrapped_first)
            
            for part in parts[1:]:
                part = part.strip()
                if part and part.startswith('- '):
                    wrapped_part = wrap_text(part, width=81, indent=4)
                    lines.extend(wrapped_part)
                elif part:
                    # Non-bullet continuation line
                    wrapped_part = wrap_text(part, width=81, indent=4)
                    lines.extend(wrapped_part)
        elif ' - ' in return_desc:
            # Handle space-separated bullet points (fallback)
            parts = return_desc.split(' - ')
            first_part = parts[0].strip()
            if first_part:
                wrapped_first = wrap_text(first_part, width=81, indent=4)
                lines.extend(wrapped_first)
            
            for part in parts[1:]:
                part = part.strip()
                if part:
                    wrapped_part = wrap_text(f'- {part}', width=81, indent=4)
                    lines.extend(wrapped_part)
        else:
            # Regular return description - wrap normally
            wrapped_return = wrap_text(return_desc, width=81, indent=4)
            lines.extend(wrapped_return)
        lines.append('')
    
    # Add source reference if available
    if doc_info.get('source_file') and doc_info.get('source_line'):
        source_file = doc_info['source_file']
        source_line = doc_info['source_line']
        
        # Make path relative to LVGL directory for cleaner display
        if '/lvgl/src/' in source_file:
            relative_path = source_file.split('/lvgl/', 1)[1]
        elif '/lvgl/' in source_file:
            relative_path = source_file.split('/lvgl/', 1)[1]
        else:
            relative_path = os.path.basename(source_file)
        
        # Clean up any remaining path artifacts
        if relative_path.startswith('gen/../lvgl/'):
            relative_path = relative_path[12:]  # Remove 'gen/../lvgl/'
        elif relative_path.startswith('../lvgl/'):
            relative_path = relative_path[8:]   # Remove '../lvgl/'
        
        if lines:
            lines.append('')
        
        # Add C function name if provided
        if c_func_name:
            lines.append(f'C function: {c_func_name}')
        
        lines.append(f'Source: {relative_path}:{source_line}')
    
    if lines and lines[-1] == '':
        lines.pop()  # Remove trailing empty line
    
    return lines

def extract_function_docs(source_lines, func_name):
    """Extract documentation for a specific function from source lines."""
    # Look for the function declaration and preceding comment
    func_pattern = rf'\b{re.escape(func_name)}\s*\('
    
    for i, line in enumerate(source_lines):
        if re.search(func_pattern, line):
            # Found function declaration, look backwards for documentation
            comment_lines = []
            j = i - 1
            
            # Skip empty lines and whitespace
            while j >= 0 and source_lines[j].strip() == '':
                j -= 1
            
            # Collect comment lines
            while j >= 0:
                line_stripped = source_lines[j].strip()
                if line_stripped.endswith('*/'):
                    # End of comment block, collect backwards
                    while j >= 0:
                        comment_line = source_lines[j].strip()
                        comment_lines.insert(0, comment_line)
                        if comment_line.startswith('/**'):
                            break
                        j -= 1
                    break
                elif line_stripped.startswith('*') or line_stripped.startswith('//'):
                    comment_lines.insert(0, line_stripped)
                    j -= 1
                else:
                    break
            
            if comment_lines:
                comment_text = '\n'.join(comment_lines)
                return parse_doxygen_comment(comment_text)
    
    return None

def process_file_for_docs(file_path):
    """Process a single header file to extract all function documentation."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_lines = f.readlines()
    except (UnicodeDecodeError, IOError):
        return {}
    
    func_docs = {}
    i = 0
    while i < len(source_lines):
        line = source_lines[i]
        
        # Look for function declarations
        # Match patterns like: type func_name(args) or type *func_name(args)
        func_match = re.search(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', line)
        if func_match and not line.strip().startswith('*') and not line.strip().startswith('//'):
            func_name = func_match.group(1)
            
            # Skip common false positives
            if func_name in ['if', 'while', 'for', 'switch', 'sizeof', 'return']:
                i += 1
                continue
            
            # Look backwards for documentation
            comment_lines = []
            j = i - 1
            
            # Skip empty lines and whitespace
            while j >= 0 and source_lines[j].strip() == '':
                j -= 1
            
            # Collect comment lines
            while j >= 0:
                line_stripped = source_lines[j].strip()
                if line_stripped.endswith('*/'):
                    # End of comment block, collect backwards
                    while j >= 0:
                        comment_line = source_lines[j].strip()
                        comment_lines.insert(0, comment_line)
                        if comment_line.startswith('/**'):
                            break
                        j -= 1
                    break
                elif line_stripped.startswith('*') or line_stripped.startswith('//'):
                    comment_lines.insert(0, line_stripped)
                    j -= 1
                else:
                    break
            
            if comment_lines:
                comment_text = '\n'.join(comment_lines)
                doc_info = parse_doxygen_comment(comment_text)
                if doc_info:
                    # Add source file information
                    doc_info['source_file'] = file_path
                    doc_info['source_line'] = i + 1  # Convert to 1-based line numbering
                    func_docs[func_name] = doc_info
        
        i += 1
    
    return func_docs

def load_lvgl_source_files(lvgl_dir):
    """Load LVGL header files and build documentation index with parallel processing."""
    import multiprocessing
    from concurrent.futures import ProcessPoolExecutor, as_completed
    
    # Find all header files
    header_files = []
    search_dirs = [os.path.join(lvgl_dir, dir_path) for dir_path in LVGL_DOC_SEARCH_DIRS]
    
    for search_dir in search_dirs:
        if os.path.exists(search_dir):
            for root, dirs, files in os.walk(search_dir):
                for file in files:
                    if file.endswith('.h'):
                        header_files.append(os.path.join(root, file))
    
    if not header_files:
        return {}
    
    # Process files in parallel
    eprint(f"Processing {len(header_files)} header files for documentation...")
    
    doc_index = {}
    
    try:
        # Use parallel processing with progress feedback
        with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            # Submit all tasks
            future_to_file = {executor.submit(process_file_for_docs, file_path): file_path 
                             for file_path in header_files}
            
            processed_count = 0
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    file_docs = future.result()
                    doc_index.update(file_docs)
                    processed_count += 1
                    
                    # Progress feedback every 50 files
                    if processed_count % 50 == 0:
                        eprint(f"Processed {processed_count}/{len(header_files)} files...")
                        
                except Exception as e:
                    eprint(f"Error processing {file_path}: {e}")
    
    except Exception as e:
        eprint(f"Parallel processing failed, falling back to serial: {e}")
        # Fallback to serial processing
        for file_path in header_files:
            try:
                file_docs = process_file_for_docs(file_path)
                doc_index.update(file_docs)
            except Exception as e:
                eprint(f"Error processing {file_path}: {e}")
    
    return doc_index

def generate_function_stub(func_name, func_info, doc_info=None, is_class_method=False, c_func_name=None):
    """Generate a Python stub for a function."""
    return_type = c_type_to_python_type(func_info.get("return_type", "None"))
    
    # Generate arguments
    args = []
    if is_class_method:
        args.append("self: Self")
    
    for arg in func_info.get("args", []):
        arg_name = sanitize_identifier(arg.get("name", "arg"))
        arg_type = c_type_to_python_type(arg.get("type", "Any"))
        args.append(f"{arg_name}: {arg_type}")
    
    args_str = ", ".join(args)
    
    # Generate function signature
    lines = [f"def {func_name}({args_str}) -> {return_type}:"]
    
    # Generate docstring
    if doc_info:
        docstring_lines = format_python_docstring(func_name, doc_info, func_info.get("args", []), c_func_name)
        if docstring_lines:
            lines.append('    """')
            for line in docstring_lines:
                lines.append(f'    {line}' if line else '    ')
            lines.append('    """')
    
    lines.append("    ...")
    lines.append("")
    
    return "\n".join(lines)

def generate_class_stub(class_name, class_info, doc_index=None):
    """Generate a Python stub for a class."""
    lines = [f"class {class_name}:"]
    
    # Add class docstring
    lines.append(f'    """LVGL {class_name} widget."""')
    lines.append("")
    
    # Generate methods
    for member_name, member_info in class_info.items():
        if member_info.get("type") == "function":
            # Try to find documentation
            doc_info = None
            if doc_index:
                full_func_name = f"lv_{class_name}_{member_name}"
                doc_info = find_function_docs_in_sources(full_func_name, doc_index)
            
            method_stub = generate_function_stub(member_name, member_info, doc_info, is_class_method=True, c_func_name=full_func_name)
            # Indent the method
            method_lines = method_stub.split('\n')
            for line in method_lines:
                if line.strip():
                    lines.append(f"    {line}")
                else:
                    lines.append("")
        elif member_info.get("type") == "property":
            # Generate property stub
            prop_type = c_type_to_python_type(member_info.get("type", "Any"))
            lines.append(f"    {member_name}: {prop_type}")
    
    lines.append("")
    return "\n".join(lines)

def generate_enum_stub(enum_name, enum_info):
    """Generate a Python stub for an enum."""
    lines = [f"class {enum_name}:"]
    lines.append(f'    """LVGL {enum_name} enum."""')
    
    # Add enum values
    for value_name, value_info in enum_info.items():
        if isinstance(value_info, dict) and value_info.get("type") == "int_constant":
            lines.append(f"    {value_name}: int = ...")
        elif isinstance(value_info, int):
            lines.append(f"    {value_name}: int = {value_info}")
    
    lines.append("")
    return "\n".join(lines)

def generate_main_stub(module_name, metadata, doc_index=None):
    """Generate the main module stub file."""
    lines = [
        '"""LVGL MicroPython bindings stub file.',
        "",
        "This file provides type hints for LVGL MicroPython bindings to enable",
        "IDE autocompletion and type checking. It is automatically generated",
        "from the LVGL C headers.",
        "",
        f"Generated content:",
        f"- {len(metadata.get('objects', {}))} widget classes",
        f"- {len(metadata.get('functions', {}))} module functions", 
        f"- {len(metadata.get('enums', {}))} enum classes",
        f"- {len(metadata.get('int_constants', []))} integer constants",
        f"- {len(metadata.get('structs', []))} struct types",
        '"""',
        "",
        "from typing import Any, Callable, Optional, Union",
        "from typing_extensions import Self",
        "",
    ]
    
    # Add module-level functions
    functions = metadata.get("functions", {})
    for func_name, func_info in functions.items():
        # Try to find documentation for this function
        doc_info = None
        if doc_index:
            doc_info = find_function_docs_in_sources(func_name, doc_index)
        
        lines.append(generate_function_stub(func_name, func_info, doc_info, c_func_name=func_name))
    
    # Add classes
    objects = metadata.get("objects", {})
    for obj_name, obj_info in objects.items():
        lines.append(generate_class_stub(obj_name, obj_info, doc_index))
    
    # Add enums
    enums = metadata.get("enums", {})
    for enum_name, enum_info in enums.items():
        lines.append(generate_enum_stub(enum_name, enum_info))
    
    # Add integer constants
    int_constants = metadata.get("int_constants", [])
    if int_constants:
        lines.append("# Integer constants")
        for const_name in int_constants:
            lines.append(f"{const_name}: int = ...")
        lines.append("")
    
    # Add version info function
    lines.append("def version_info() -> dict:")
    lines.append('    """Get LVGL version information."""')
    lines.append("    ...")
    lines.append("")
    
    return "\n".join(lines)

def validate_metadata_consistency(metadata):
    """Ensure metadata structure is complete and consistent."""
    required_sections = ["objects", "functions", "enums", "structs", "int_constants"]
    
    for section in required_sections:
        if section not in metadata:
            raise ValueError(f"Missing required metadata section: {section}")
    
    # Validate function signatures
    for func_name, func_info in metadata["functions"].items():
        if "args" not in func_info:
            eprint(f"Warning: Function {func_name} missing args metadata")
        if "return_type" not in func_info:
            eprint(f"Warning: Function {func_name} missing return_type metadata")

def validate_documentation_coverage(doc_index, metadata):
    """Report on documentation coverage for generated functions."""
    if not doc_index:
        eprint("No documentation index available for coverage analysis")
        return 0
    
    total_functions = len(metadata["functions"])
    documented_functions = 0
    
    for func_name in metadata["functions"]:
        if find_function_docs_in_sources(func_name, doc_index):
            documented_functions += 1
    
    coverage_pct = (documented_functions / total_functions) * 100 if total_functions > 0 else 0
    eprint(f"Documentation coverage: {documented_functions}/{total_functions} ({coverage_pct:.1f}%)")
    
    return coverage_pct

def validate_stub_syntax(stub_content):
    """Validate that generated stub has valid Python syntax."""
    try:
        import ast
        # Try to parse the stub content
        ast.parse(stub_content)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error in generated stub: {e}"
    except Exception as e:
        return False, f"Error parsing stub: {e}"

def validate_generated_stubs(stubs_path, metadata):
    """Validate generated stub files."""
    if not os.path.exists(stubs_path):
        eprint(f"Warning: Generated stub file not found at {stubs_path}")
        return False
    
    # Read the generated stub file
    try:
        with open(stubs_path, 'r') as f:
            stub_content = f.read()
    except Exception as e:
        eprint(f"Error reading stub file: {e}")
        return False
    
    # Validate syntax
    valid_syntax, syntax_error = validate_stub_syntax(stub_content)
    if not valid_syntax:
        eprint(f"Stub validation failed: {syntax_error}")
        return False
    
    # Basic content validation
    expected_functions = len(metadata.get("functions", {}))
    expected_classes = len(metadata.get("objects", {}))
    expected_enums = len(metadata.get("enums", {}))
    
    function_count = stub_content.count("def ")
    class_count = stub_content.count("class ")
    
    eprint(f"Stub validation: {function_count} functions, {class_count} classes generated")
    eprint(f"Expected from metadata: {expected_functions} functions, {expected_classes + expected_enums} classes")
    
    # Check for basic required imports
    if "from typing import" not in stub_content:
        eprint("Warning: Missing typing imports in stub file")
    
    if "from typing_extensions import Self" not in stub_content:
        eprint("Warning: Missing Self import in stub file")
    
    eprint("Stub validation completed successfully")
    return True

def main():
    """Main entry point for stub generation."""
    parser = argparse.ArgumentParser(description="Generate LVGL Python stub files")
    parser.add_argument("--metadata", required=True, help="JSON metadata file from gen_mpy.py")
    parser.add_argument("--stubs-dir", required=True, help="Output directory for stub files")
    parser.add_argument("--lvgl-dir", help="LVGL source directory for documentation")
    parser.add_argument("--module-name", default="lvgl", help="Module name")
    parser.add_argument("--validate", action="store_true", help="Enable validation checks")
    
    args = parser.parse_args()
    
    # Load metadata
    try:
        with open(args.metadata, 'r') as f:
            metadata = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        eprint(f"Error loading metadata file {args.metadata}: {e}")
        return 1
    
    # Validate metadata if requested
    if args.validate:
        try:
            validate_metadata_consistency(metadata)
        except ValueError as e:
            eprint(f"Metadata validation failed: {e}")
            return 1
    
    # Create output directory
    os.makedirs(args.stubs_dir, exist_ok=True)
    
    # Load documentation index
    doc_index = None
    if args.lvgl_dir and os.path.exists(args.lvgl_dir):
        eprint(f"Loading LVGL source files for documentation extraction from: {args.lvgl_dir}")
        doc_index = load_lvgl_source_files(args.lvgl_dir)
        eprint(f"Built documentation index with {len(doc_index)} functions")
        
        if args.validate:
            validate_documentation_coverage(doc_index, metadata)
    else:
        eprint(f"LVGL directory not found at {args.lvgl_dir}, generating stubs without documentation")
    
    # Generate main module stub
    eprint(f"Generating stub file for module: {args.module_name}")
    main_stub_content = generate_main_stub(args.module_name, metadata, doc_index)
    main_stub_path = os.path.join(args.stubs_dir, f"{args.module_name}.pyi")
    
    with open(main_stub_path, "w") as stub_file:
        stub_file.write(main_stub_content)
    
    eprint(f"Generated Python stub file: {main_stub_path}")
    eprint(f"Generated Python stub file with {len(metadata.get('objects', {}))} widgets, {len(metadata.get('functions', {}))} functions, and {len(metadata.get('enums', {}))} enums")
    
    # Validate generated stubs if requested
    if args.validate:
        eprint("Validating generated stub files...")
        if not validate_generated_stubs(main_stub_path, metadata):
            eprint("Stub validation failed!")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())