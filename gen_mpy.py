# TODO
# - On print extensions, print the reflected internal representation of the object
# - Verify that when mp_obj is given it is indeed the right type (mp_lv_obj_t). Report error if not. can be added to mp_to_lv.
# - Implement inheritance instead of embed base methods (how?)

from sys import argv
from pycparser import c_parser, c_ast, c_generator
from argparse import ArgumentParser
import subprocess, re

#
# Argument parsing
#

argParser = ArgumentParser()
argParser.add_argument('-I', '--include', dest='include', help='Preprocesor include path', metavar='<Include Path>', action='append')
argParser.add_argument('-X', '--exclude', dest='exclude', help='Exclude lvgl object', metavar='<Object Name>', action='append')
argParser.add_argument('input', nargs='+')
args = argParser.parse_args()

# 
# C proceprocessing
# 

pp_cmd = 'gcc -E -std=c99 {include} {input} {first_input}'.format(
    input=' '.join('-include %s' % inp for inp in args.input), 
    first_input= '%s' % args.input[0],
    include=' '.join('-I %s' % inc for inc in args.include))
s = subprocess.check_output(pp_cmd.split())

#
# Initialization and data structures
#

parser = c_parser.CParser()
gen = c_generator.CGenerator()
ast = parser.parse(s, filename='<none>')
func_defs = [x.decl for x in ast.ext if isinstance(x, c_ast.FuncDef)]
func_decls = [x for x in ast.ext if isinstance(x, c_ast.Decl) and isinstance(x.type, c_ast.FuncDecl)]
funcs = func_defs + func_decls
create_obj_pattern = re.compile('lv_([^_]+)_create')
excluded_ctors = ['lv_%s_create' % obj for obj in args.exclude]
obj_ctors = [func for func in funcs if create_obj_pattern.match(func.name) and not func.name in excluded_ctors]
for obj_ctor in obj_ctors:
    funcs.remove(obj_ctor)
obj_names = [re.match(create_obj_pattern, ctor.name).group(1) for ctor in obj_ctors]

def get_methods(obj_name, funcs):
    return [func for func in funcs if func.name.startswith('lv_%s_' % obj_name) and (not func.name == 'lv_%s_create' % obj_name)]

base_obj_name = 'obj'
base_methods = get_methods(base_obj_name, funcs)
base_ctor = next(ctor for ctor in obj_ctors if ctor.name == 'lv_%s_create' % base_obj_name)
obj_ctors.remove(base_ctor) # base_ctor is called explicitly

#
# Type convertors
#

class MissingConversionException(ValueError):
    pass

mp_to_lv = {
    'bool'                  : 'mp_obj_is_true',
    'char*'                 : 'mp_obj_str_get_str',
    'const char*'           : 'mp_obj_str_get_str',
    'lv_obj_t*'             : 'mp_to_lv',
    'const lv_obj_t*'       : 'mp_to_lv',
    'uint8_t'               : '(uint8_t)mp_obj_int_get_checked',
    'uint16_t'              : '(uint16_t)mp_obj_int_get_checked',
    'uint32_t'              : '(uint32_t)mp_obj_int_get_checked',
    'int8_t'                : '(int8_t)mp_obj_int_get_checked',
    'int16_t'               : '(int16_t)mp_obj_int_get_checked',
    'int32_t'               : '(int32_t)mp_obj_int_get_checked',
}

lv_to_mp = {
    'bool'          : 'convert_to_bool',
    'char*'         : 'convert_to_str',
    'const char*'   : 'convert_to_str',
    'uint8_t'       : 'mp_obj_new_int_from_uint',
    'uint16_t'      : 'mp_obj_new_int_from_uint',
    'uint32_t'      : 'mp_obj_new_int_from_uint',
    'int8_t'        : 'mp_obj_new_int',
    'int16_t'       : 'mp_obj_new_int',
    'int32_t'       : 'mp_obj_new_int',
}

#
# Emit Header
#

print ("""
/*
 * Auto-Generated file, DO NOT EDIT!
 *
 * Command line:
 * {cmd_line}
 *
 * Preprocessing command:
 * {pp_cmd}
 *
 */

/*
 * Mpy includes
 */

#include <string.h>
#include "py/obj.h"
#include "py/runtime.h"

/*
 * lvgl includes
 */

{lv_headers}
""".format(
        cmd_line=' '.join(argv),
        pp_cmd=pp_cmd,
        lv_headers='\n'.join('#include "%s"' % header for header in args.input)));


#
# Emit Mpy helper functions
#

print("""
/*
 * Helper functions
 */

typedef lv_obj_t* (*lv_create)(lv_obj_t * par, const lv_obj_t * copy);

typedef struct mp_lv_obj_t {
    mp_obj_base_t base;
    lv_obj_t *lv_obj;
} mp_lv_obj_t;

STATIC inline lv_obj_t *mp_to_lv(mp_obj_t *mp_obj)
{
    mp_lv_obj_t *mp_lv_obj = MP_OBJ_TO_PTR(mp_obj);
    return mp_lv_obj->lv_obj;
}

STATIC mp_obj_t make_new(
    lv_create create,
    const mp_obj_type_t *type,
    size_t n_args,
    size_t n_kw,
    const mp_obj_t *args)
{
    mp_arg_check_num(n_args, n_kw, 1, 2, false);
    mp_lv_obj_t *self = m_new_obj(mp_lv_obj_t);
    lv_obj_t *parent = mp_to_lv(args[0]);
    lv_obj_t *copy = n_args > 1? mp_to_lv(args[1]): NULL;
    *self = (mp_lv_obj_t){
        .base = {type}, 
        .lv_obj = create(parent, copy)
    };
    return MP_OBJ_FROM_PTR(self);
}

STATIC inline mp_obj_t convert_to_bool(bool b)
{
    return b? mp_const_true: mp_const_false;
}

STATIC inline mp_obj_t convert_to_str(const char *str)
{
    return mp_obj_new_str(str, strlen(str));
}

""")

#
# Emit Mpy function definitions
#

def get_arg_type(arg):
    indirect_level = 0
    while isinstance(arg,c_ast.PtrDecl):
        indirect_level += 1
        arg = arg.type
    return '{quals}{type}{indirection}'.format(
        quals=''.join('%s ' % qual for qual in arg.quals),
        type=gen.visit(arg),
        indirection='*' * indirect_level)

def build_arg(arg, index):
    arg_type = get_arg_type(arg.type)
    if not arg_type in mp_to_lv:
        raise MissingConversionException("Missing conversion to %s" % arg_type)
    return '{var} = {convertor}(args[{i}]);'.format(
        var = gen.visit(arg),
        convertor = mp_to_lv[arg_type],
        i = index) 

def gen_func(func):
    print("""
/*    
{ast}
*/
    """).format(ast=func)
    args = func.type.args.params
    param_count = len(args)
    return_type = get_arg_type(func.type.type)
    if return_type == "void":        
        build_result = ""
        build_return_value = "mp_const_none" 
    else:
        if not return_type in lv_to_mp:
            raise MissingConversionException("Missing convertion from %s" % return_type)
        build_result = "%s res = " % return_type
        build_return_value = "%s(res)" % lv_to_mp[return_type]
    print("""
/*
 * lvgl extension definition for:
 * {print_func}
 */
 
STATIC mp_obj_t mp_{func}(size_t n_args, const mp_obj_t *args)
{{
    {build_args}
    {build_result}{func}({send_args});
    return {build_return_value};
}}

MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(mp_{func}_obj, {count}, {count}, mp_{func});

 """).format(func=func.name, 
             print_func=gen.visit(func),
             count=param_count, 
             build_args="\n    ".join([build_arg(arg,i) for i,arg in enumerate(args) if arg.name]), 
             send_args=", ".join(arg.name for arg in args if arg.name),
             build_result=build_result,
             build_return_value=build_return_value)
    funcs.remove(func)


def gen_func_error(method, exp):
    global funcs
    print("""
/*
 * function NOT generated:
 * {problem}
 * {method}
 */
    """.format(method=gen.visit(method), problem=exp))
    funcs.remove(method)
                 

#
# Emit Mpy objects definitions
#

def gen_obj_methods(obj_name, methods):
    method_prefix = "lv_%s_" % obj_name
    return ["{{MP_OBJ_NEW_QSTR(MP_QSTR_{method_name}), (mp_obj_t)&mp_{method}_obj}}".\
                    format(method=method.name, method_name=method.name[len(method_prefix):]) for method in methods]

def gen_obj(obj_ctor):
    obj_name = re.match(create_obj_pattern, obj_ctor.name).group(1)
    should_add_base_methods = obj_name != 'obj'
    methods = base_methods if obj_name == base_obj_name else get_methods(obj_name, funcs)
    for method in methods[:]: # copy the list because we remove elements while iterating it...
        try:
            gen_func(method)
        except MissingConversionException as exp:
            gen_func_error(method, exp)
            methods.remove(method)
       
    # print([method.name for method in methods])
    print("""
    
/*
 * lvgl {obj} object definitions
 */

STATIC const mp_rom_map_elem_t {obj}_locals_dict_table[] = {{
    {locals_dict_entries}
}};

STATIC MP_DEFINE_CONST_DICT({obj}_locals_dict, {obj}_locals_dict_table);

STATIC void {obj}_print(const mp_print_t *print,
    mp_obj_t self_in,
    mp_print_kind_t kind)
{{
    mp_printf(print, "lvgl {obj}");
}}

STATIC mp_obj_t {obj}_make_new(
    const mp_obj_type_t *type,
    size_t n_args,
    size_t n_kw,
    const mp_obj_t *args)
{{
    return make_new(&lv_{obj}_create, type, n_args, n_kw, args);           
}}

STATIC const mp_obj_type_t {obj}_type = {{
    {{ &mp_type_type }},
    .name = MP_QSTR_{obj},
    .print = {obj}_print,
    .make_new = {obj}_make_new,
    .locals_dict = (mp_obj_dict_t*)&{obj}_locals_dict,
}};
    """.format(obj=obj_name, locals_dict_entries=",\n    ".join(
         (gen_obj_methods(base_obj_name, base_methods) if should_add_base_methods else []) + gen_obj_methods(obj_name, methods))))

# Generate base object
gen_obj(base_ctor) # base methods must appear first because they are used on every object

# Generate all other objects
for obj_ctor in obj_ctors:
    gen_obj(obj_ctor)

for module_func in funcs:
    try:
        gen_func(module_func)
    except MissingConversionException as exp:
        gen_func_error(module_func, exp)
    
print("""
/*
 * Functions not generated:
 * {funcs}
 *
 */

""".format(funcs = "\n * ".join([func.name for func in funcs])))

#
# Emit Mpy Module definition
#

print("""

/*
 * lvgl module definitions
 * User should implement lv_mp_init. Display can be initialized there, if needed.
 */

extern void lv_mp_init();

STATIC mp_obj_t _lv_mp_init()
{
    lv_mp_init();
    return mp_const_none;
}

STATIC MP_DEFINE_CONST_FUN_OBJ_0(lv_mp_init_obj, _lv_mp_init);

STATIC const mp_rom_map_elem_t lvgl_globals_table[] = {
    { MP_OBJ_NEW_QSTR(MP_QSTR___name__), MP_OBJ_NEW_QSTR(MP_QSTR_lvgl) },
    { MP_OBJ_NEW_QSTR(MP_QSTR___init__), (mp_obj_t)&lv_mp_init_obj },
    %s
};
""" % ',\n    '.join(['{{ MP_OBJ_NEW_QSTR(MP_QSTR_{obj}), (mp_obj_t)&{obj}_type }}'.format(obj = x) for x in obj_names]))

print("""
STATIC MP_DEFINE_CONST_DICT (
    mp_module_lvgl_globals,
    lvgl_globals_table
);

const mp_obj_module_t mp_module_lvgl = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&mp_module_lvgl_globals
};
""")

