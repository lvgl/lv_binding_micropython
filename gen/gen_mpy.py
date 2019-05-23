# TODO
# - Implement array. Convert python list to C pointer throught struct object. Useful lv_line_set_points or for setting "points" on lv_chart_series_t for example.
# - On print extensions, print the reflected internal representation of the object
# - Verify that when mp_obj is given it is indeed the right type (mp_lv_obj_t). Report error if not. can be added to mp_to_lv.
# - Implement inheritance instead of embed base methods (how? seems it's not supported, see https://github.com/micropython/micropython/issues/1159)
# - Prevent writing to const fields, but allow reading
# - When converting mp to ptr (and vice versa), verify that types are compatible. Now all pointers are casted to void*.

from __future__ import print_function
import collections
import sys
import struct
import copy
from itertools import chain

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    
from sys import argv
from argparse import ArgumentParser
import subprocess, re
from os.path import dirname, abspath
from os.path import commonprefix

script_path = dirname(abspath(__file__))
sys.path.append('%s/../pycparser' % script_path)
from pycparser import c_parser, c_ast, c_generator

#
# Argument parsing
#

argParser = ArgumentParser()
argParser.add_argument('-I', '--include', dest='include', help='Preprocesor include path', metavar='<Include Path>', action='append')
argParser.add_argument('-D', '--define', dest='define', help='Define preprocessor macro', metavar='<Macro Name>', action='append')
argParser.add_argument('-E', '--external-preprocessing', dest='ep', help='Prevent preprocessing. Assume input file is already preprocessed', metavar='<Preprocessed File>', action='store')
argParser.add_argument('input', nargs='+')
argParser.set_defaults(include=[], define=[], ep=None, input=[])
args = argParser.parse_args()

# 
# C proceprocessing, if needed, or just read the input files.
# 

if not args.ep:
    pp_cmd = 'gcc -E -std=c99 -DPYCPARSER {macros} {include} {input} {first_input}'.format(
        input=' '.join('-include %s' % inp for inp in args.input), 
        first_input= '%s' % args.input[0],
        macros = ' '.join('-D%s' % define for define in args.define),
        include=' '.join('-I %s' % inc for inc in args.include))
    s = subprocess.check_output(pp_cmd.split()).decode()
else:
    pp_cmd = 'Preprocessing was disabled.'
    s = ''
    with open(args.ep, 'r') as f:
        s += f.read()
# 
# AST parsing helper functions
#

def convert_array_to_ptr(ast):
    if hasattr(ast, 'type') and isinstance(ast.type, c_ast.ArrayDecl):
        ast.type = c_ast.PtrDecl(ast.type.quals if hasattr(ast.type, 'quals') else [], ast.type.type)
    if isinstance(ast, tuple):
        return convert_array_to_ptr(ast[1])
    for i, c1 in enumerate(ast.children()):
        child = ast.children()[i]
        convert_array_to_ptr(child)

def remove_quals(ast):
    if hasattr(ast,'quals'):
        ast.quals = []
    if hasattr(ast,'dim_quals'):
        ast.dim_quals = []
    if isinstance(ast, tuple):
        return remove_quals(ast[1])
    for i, c1 in enumerate(ast.children()):
        child = ast.children()[i]
        if not isinstance(child, c_ast.FuncDecl): # Don't remove quals which change function prorotype
            remove_quals(child)

def remove_explicit_struct(ast):
    if isinstance(ast, c_ast.TypeDecl) and isinstance(ast.type, c_ast.Struct):
        explicit_struct_name = ast.type.name
        # eprint('--> replace %s by %s in:\n%s' % (explicit_struct_name, explicit_structs[explicit_struct_name] if explicit_struct_name in explicit_structs else '???', ast))
        if explicit_struct_name and explicit_struct_name in explicit_structs:
            ast.type = c_ast.IdentifierType([explicit_structs[explicit_struct_name]])
    if isinstance(ast, tuple):
        return remove_explicit_struct(ast[1])
    for i, c1 in enumerate(ast.children()):
        child = ast.children()[i]
        remove_explicit_struct(child)

def get_type(arg, **kwargs):
    if isinstance(arg, str): 
        return arg
    remove_quals_arg = 'remove_quals' in kwargs and kwargs['remove_quals']
    arg_ast = copy.deepcopy(arg)
    remove_explicit_struct(arg_ast)
    if remove_quals_arg: remove_quals(arg_ast)
    return gen.visit(arg_ast)

def get_name(type):
    if isinstance(type, c_ast.Decl):
        return type.name
    if isinstance(type, c_ast.Struct) and type.name:
        return explicit_structs[type.name]
    if isinstance(type, c_ast.TypeDecl):
        return type.declname
    if isinstance(type, c_ast.IdentifierType):
        return type.names[0]
    if isinstance(type, c_ast.FuncDecl):
        return type.type.declname
    if isinstance(type, (c_ast.PtrDecl, c_ast.ArrayDecl)): 
        return get_type(type, remove_quals=True)
    else:
        return type

#
# lv text patterns
# IGNORECASE and "lower" are used to match both function and enum names
# 

base_obj_name = 'obj'
lv_ext_pattern = re.compile('^lv_([^_]+)_ext_t')
lv_obj_pattern = re.compile('^lv_([^_]+)', re.IGNORECASE)
lv_func_pattern = re.compile('^lv_(.+)', re.IGNORECASE)
create_obj_pattern = re.compile('^lv_([^_]+)_create')
lv_method_pattern = re.compile('^lv_[^_]+_(.+)', re.IGNORECASE)
lv_base_obj_pattern = re.compile('^(struct _){0,1}lv_%s_t( \*){0,1}' % (base_obj_name))
lv_callback_return_type_pattern = re.compile('^((void)|(lv_res_t))')
lv_numstr_pattern = re.compile('^(.*)_NUMSTR')
lv_str_enum_pattern = re.compile('^_LV_STR_(.+)')
lv_callback_type_pattern = re.compile('(lv_){0,1}(.+)_cb(_t){0,1}')
lv_global_callback_pattern = re.compile('.*g_cb_t')

def simplify_identifier(id):
    return re.match(lv_func_pattern, id).group(1)

def obj_name_from_ext_name(ext_name):
    return re.match(lv_ext_pattern, ext_name).group(1)

def obj_name_from_func_name(func_name):
    return re.match(lv_obj_pattern, func_name).group(1)

def ctor_name_from_obj_name(obj_name):
    return 'lv_%s_create' % obj_name

def is_method_of(func_name, obj_name):
    return func_name.lower().startswith(('lv_%s_' % obj_name).lower())
    
def method_name_from_func_name(func_name):
    res = re.match(lv_method_pattern, func_name).group(1)
    return res if res != "del" else "delete" # del is a resrved name, don't use it

def get_enum_name(enum):
    prefix = 'lv_'
    return enum[len(prefix):]

def str_enum_to_str(str_enum):
    res = re.match(lv_str_enum_pattern, str_enum).group(1)
    return 'LV_' + res

def user_data_from_callback_func(callback_func_name):
    return 'user_data'
    # res = re.match(lv_callback_type_pattern, callback_func_name)
    # return res.group(2) + '_user_data' if res and res.group(2) else None

def is_obj_ctor(func):
    # ctor name must match pattern
    if not create_obj_pattern.match(func.name): return False
    # ctor must return a base_obj type
    if not lv_base_obj_pattern.match(get_type(func.type.type, remove_quals=True)): return False
    # ctor must receive (at least) two base obj parameters
    args = func.type.args.params
    if len(args) < 2: return False
    if not lv_base_obj_pattern.match(get_type(args[0].type, remove_quals=True)): return False
    if not lv_base_obj_pattern.match(get_type(args[1].type, remove_quals=True)): return False
    return True

def is_global_callback(arg_type):
    arg_type_str = get_name(arg_type.type)
    # print('/* --> is_global_callback %s: %s */' % (lv_global_callback_pattern.match(arg_type_str), arg_type_str))
    return lv_global_callback_pattern.match(arg_type_str)

#
# Initialization, data structures, helper functions
#

# We consider union as a struct, for simplicity
def is_struct(type):
    return isinstance(type, c_ast.Struct) or isinstance(type, c_ast.Union)

parser = c_parser.CParser()
gen = c_generator.CGenerator()
ast = parser.parse(s, filename='<none>')
func_defs = [x.decl for x in ast.ext if isinstance(x, c_ast.FuncDef)]
func_decls = [x for x in ast.ext if isinstance(x, c_ast.Decl) and isinstance(x.type, c_ast.FuncDecl)]
funcs = func_defs + func_decls
# eprint('... %s' % ',\n'.join(sorted('%s' % func.name for func in funcs)))
obj_ctors = [func for func in funcs if is_obj_ctor(func)]
for obj_ctor in obj_ctors:
    funcs.remove(obj_ctor)
obj_names = [re.match(create_obj_pattern, ctor.name).group(1) for ctor in obj_ctors]
typedefs = [x.type for x in ast.ext if isinstance(x, c_ast.Typedef)] # and not (hasattr(x.type, 'declname') and lv_base_obj_pattern.match(x.type.declname))]
# print('... %s' % str(typedefs))
struct_typedefs = [typedef for typedef in typedefs if is_struct(typedef.type)]
structs = collections.OrderedDict((typedef.declname, typedef.type) for typedef in struct_typedefs if typedef.declname) # and not lv_base_obj_pattern.match(typedef.declname)) 
explicit_structs = collections.OrderedDict((typedef.type.name, typedef.declname) for typedef in struct_typedefs if typedef.type.name) # and not lv_base_obj_pattern.match(typedef.type.name))
# print('/* --> structs:\n%s */' % ',\n'.join(sorted(struct_name for struct_name in structs)))

def has_ctor(obj_name):
    return ctor_name_from_obj_name(obj_name) in [ctor.name for ctor in obj_ctors]
        
def get_ctor(obj_name):
    global obj_ctors
    return next(ctor for ctor in obj_ctors if ctor.name == ctor_name_from_obj_name(obj_name))

def get_methods(obj_name):
    global funcs
    return [func for func in funcs if is_method_of(func.name,obj_name) and (not func.name == ctor_name_from_obj_name(obj_name))]

  
# All object should inherit directly from base_obj, and not according to lv_ext, as disccussed on https://github.com/littlevgl/lv_binding_micropython/issues/19
parent_obj_names = {child_name: base_obj_name for child_name in obj_names if child_name != base_obj_name} 
parent_obj_names[base_obj_name] = None

# Populate inheritance hierarchy according to lv_ext structures
# exts = {obj_name_from_ext_name(ext.name): ext for ext in ast.ext if hasattr(ext, 'name') and ext.name is not None and lv_ext_pattern.match(ext.name)}
# for obj_name, ext in exts.items():
#     try:
#         parent_ext_name = ext.type.type.decls[0].type.type.names[0]
#         if lv_ext_pattern.match(parent_ext_name):
#             parent_obj_names[obj_name] = obj_name_from_ext_name(parent_ext_name)
#     except AttributeError:
#         pass

# Parse Enums

enum_defs = [x for x in ast.ext if hasattr(x,'type') and isinstance(x.type, c_ast.Enum)]

# Enum member access functions.

def get_enum_members(obj_name):
    global enums
    if not obj_name in enums:
        return []
    return [enum_member_name for enum_member_name, value in enums[obj_name].items()]
 
def get_enum_member_name(enum_member):
    if enum_member[0].isdigit():
        enum_member = '_' + enum_member # needs to be a valid attribute name
    return enum_member

def get_enum_value(obj_name, enum_member):
    return enums[obj_name][enum_member]

# eprint(enums)

# parse function pointers
func_typedefs = collections.OrderedDict((t.name, t) for t in ast.ext if isinstance(t, c_ast.Typedef) and isinstance(t.type, c_ast.PtrDecl) and isinstance(t.type.type, c_ast.FuncDecl))

# Global blobs
blobs = collections.OrderedDict((decl.name, decl.type.type) for decl in ast.ext \
    if isinstance(decl, c_ast.Decl) \
        and 'extern' in decl.storage \
        and hasattr(decl, 'type') \
        and isinstance(decl.type, c_ast.TypeDecl))

#
# Type convertors
#

class MissingConversionException(ValueError):
    pass

mp_to_lv = {
    'void *'                    : 'mp_to_ptr',
    'const uint8_t *'           : 'mp_to_ptr',
    'const void *'              : 'mp_to_ptr',
    'bool'                      : 'mp_obj_is_true',
    'char *'                    : '(char*)mp_obj_str_get_str',
    'const char *'              : 'mp_obj_str_get_str',
    'lv_obj_t *'                : 'mp_to_lv',
    'uint8_t'                   : '(uint8_t)mp_obj_get_int',
    'uint16_t'                  : '(uint16_t)mp_obj_get_int',
    'uint32_t'                  : '(uint32_t)mp_obj_get_int',
    'int8_t'                    : '(int8_t)mp_obj_get_int',
    'int16_t'                   : '(int16_t)mp_obj_get_int',
    'int32_t'                   : '(int32_t)mp_obj_get_int',
    'size_t'                    : '(size_t)mp_obj_get_int',
    'int'                       : '(int)mp_obj_get_int',
}

lv_to_mp = {
    'void *'                    : 'ptr_to_mp',
    'const uint8_t *'           : 'ptr_to_mp',
    'const void *'              : 'ptr_to_mp',
    'bool'                      : 'convert_to_bool',
    'char *'                    : 'convert_to_str',
    'const char *'              : 'convert_to_str',
    'lv_obj_t *'                : 'lv_to_mp',
    'uint8_t'                   : 'mp_obj_new_int_from_uint',
    'uint16_t'                  : 'mp_obj_new_int_from_uint',
    'uint32_t'                  : 'mp_obj_new_int_from_uint',
    'int8_t'                    : 'mp_obj_new_int',
    'int16_t'                   : 'mp_obj_new_int',
    'int32_t'                   : 'mp_obj_new_int',
    'size_t'                    : 'mp_obj_new_int_from_uint',
    'int'                       : 'mp_obj_new_int',
}

lv_to_mp_byref = {}

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
 * Generating Objects: {objs}
 */

/*
 * Mpy includes
 */

#include <stdlib.h>
#include <string.h>
#include "py/obj.h"
#include "py/objstr.h"
#include "py/runtime.h"
#include "py/binary.h"

/*
 * lvgl includes
 */

{lv_headers}
""".format(
        cmd_line=' '.join(argv),
        pp_cmd=pp_cmd,
        objs=", ".join(['%s(%s)' % (objname, parent_obj_names[objname]) for objname in obj_names]),
        lv_headers='\n'.join('#include "%s"' % header for header in args.input)))


#
# Emit Mpy helper functions
#

print("""
/*
 * Helper functions
 */


// Custom function mp object

typedef struct _mp_lv_obj_fun_builtin_var_t {
    mp_obj_base_t base;
    mp_uint_t n_args;
    mp_fun_var_t mp_fun;
    void *lv_fun;
} mp_lv_obj_fun_builtin_var_t;

STATIC mp_obj_t lv_fun_builtin_var_call(mp_obj_t self_in, size_t n_args, size_t n_kw, const mp_obj_t *args);
STATIC mp_int_t mp_func_get_buffer(mp_obj_t self_in, mp_buffer_info_t *bufinfo, mp_uint_t flags);

STATIC const mp_obj_type_t mp_lv_type_fun_builtin_var = {
    { &mp_type_type },
    .name = MP_QSTR_function,
    .call = lv_fun_builtin_var_call,
    .unary_op = mp_generic_unary_op,
    .buffer_p = { .get_buffer = mp_func_get_buffer }
};

STATIC mp_obj_t lv_fun_builtin_var_call(mp_obj_t self_in, size_t n_args, size_t n_kw, const mp_obj_t *args) {
    assert(MP_OBJ_IS_TYPE(self_in, &mp_lv_type_fun_builtin_var));
    mp_lv_obj_fun_builtin_var_t *self = MP_OBJ_TO_PTR(self_in);
    mp_arg_check_num(n_args, n_kw, self->n_args, self->n_args, false);
    return self->mp_fun(n_args, args);
}

STATIC mp_int_t mp_func_get_buffer(mp_obj_t self_in, mp_buffer_info_t *bufinfo, mp_uint_t flags) {
    (void)flags;
    assert(MP_OBJ_IS_TYPE(self_in, &mp_lv_type_fun_builtin_var));
    mp_lv_obj_fun_builtin_var_t *self = MP_OBJ_TO_PTR(self_in);

    bufinfo->buf = &self->lv_fun;
    bufinfo->len = sizeof(self->lv_fun);
    bufinfo->typecode = BYTEARRAY_TYPECODE;
    return 0;
}

#define MP_DEFINE_CONST_LV_FUN_OBJ_VAR(obj_name, n_args, mp_fun, lv_fun) \\
    const mp_lv_obj_fun_builtin_var_t obj_name = \\
        {{&mp_lv_type_fun_builtin_var}, n_args, mp_fun, lv_fun}

// lvgl object handling

typedef lv_obj_t* (*lv_create)(lv_obj_t * par, const lv_obj_t * copy);

typedef struct mp_lv_obj_t {
    mp_obj_base_t base;
    lv_obj_t *lv_obj;
    lv_obj_t *callbacks;
} mp_lv_obj_t;

STATIC mp_obj_t get_native_obj(mp_obj_t *mp_obj)
{
    const mp_obj_type_t *native_type = ((mp_obj_base_t*)mp_obj)->type;
    if (native_type->parent == NULL) return mp_obj;
    while (native_type->parent) native_type = native_type->parent;
    return mp_instance_cast_to_native_base(mp_obj, MP_OBJ_FROM_PTR(native_type));
}

STATIC mp_obj_t dict_to_struct(mp_obj_t dict, const mp_obj_type_t *type);

STATIC mp_obj_t *cast(mp_obj_t *mp_obj, const mp_obj_type_t *mp_type)
{
    mp_obj_t *res = NULL;
    if (MP_OBJ_IS_OBJ(mp_obj)){
        res = get_native_obj(mp_obj);
        if (res){
            const mp_obj_type_t *res_type = ((mp_obj_base_t*)res)->type;
            if (res_type != mp_type){
                if (res_type == &mp_type_dict) res = dict_to_struct(res, mp_type);
                else res = NULL;
            }
        }
    }
    if (res == NULL) nlr_raise(
        mp_obj_new_exception_msg_varg(
            &mp_type_SyntaxError, "Can't convert %s to %s!", mp_obj_get_type_str(mp_obj), qstr_str(mp_type->name)));
    return res;
}

STATIC inline lv_obj_t *mp_to_lv(mp_obj_t *mp_obj)
{
    if (mp_obj == NULL || mp_obj == mp_const_none) return NULL;
    mp_lv_obj_t *mp_lv_obj = MP_OBJ_TO_PTR(get_native_obj(mp_obj));
    return mp_lv_obj->lv_obj;
}

STATIC inline lv_obj_t *mp_get_callbacks(mp_obj_t mp_obj)
{
    if (mp_obj == NULL || mp_obj == mp_const_none) return NULL;
    mp_lv_obj_t *mp_lv_obj = MP_OBJ_TO_PTR(get_native_obj(mp_obj));
    if (!mp_lv_obj->callbacks) mp_lv_obj->callbacks = mp_obj_new_dict(0);
    return mp_lv_obj->callbacks;
}

STATIC inline const mp_obj_type_t *get_BaseObj_type();

STATIC inline mp_obj_t *lv_to_mp(lv_obj_t *lv_obj)
{
    mp_lv_obj_t *self = (mp_lv_obj_t*)lv_obj->user_data;
    if (!self) 
    {
        self = m_new_obj(mp_lv_obj_t);
        *self = (mp_lv_obj_t){
            .base = {get_BaseObj_type()},
            .lv_obj = lv_obj,
            .callbacks = NULL,
        };
        lv_obj->user_data = self;
    }
    return MP_OBJ_FROM_PTR(self);
}

STATIC mp_obj_t make_new(
    lv_create create,
    const mp_obj_type_t *type,
    size_t n_args,
    size_t n_kw,
    const mp_obj_t *args)
{
    mp_arg_check_num(n_args, n_kw, 0, 2, false);
    mp_lv_obj_t *self = m_new_obj(mp_lv_obj_t);
    lv_obj_t *parent = n_args > 0? mp_to_lv(args[0]): NULL;
    lv_obj_t *copy = n_args > 1? mp_to_lv(args[1]): NULL;
    *self = (mp_lv_obj_t){
        .base = {type}, 
        .lv_obj = create(parent, copy),
        .callbacks = NULL,
    };
    self->lv_obj->user_data = self;
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

STATIC mp_int_t mp_obj_get_buffer(mp_obj_t self_in, mp_buffer_info_t *bufinfo, mp_uint_t flags) {
    (void)flags;
    mp_lv_obj_t *self = MP_OBJ_TO_PTR(self_in);

    bufinfo->buf = &self->lv_obj;
    bufinfo->len = sizeof(self->lv_obj);
    bufinfo->typecode = BYTEARRAY_TYPECODE;
    return 0;
}

// lvgl struct handling

STATIC void field_not_found(qstr struct_name, qstr field_name)
{
    nlr_raise(
        mp_obj_new_exception_msg_varg(
            &mp_type_SyntaxError, 
            "Cannot access field %s. Field does not exist in struct %s!", 
            qstr_str(field_name), 
            qstr_str(struct_name)));
}

typedef struct mp_lv_struct_t
{
    mp_obj_base_t base;
    void *data;
} mp_lv_struct_t;

STATIC inline mp_lv_struct_t *mp_to_lv_struct(mp_obj_t mp_obj)
{
    if (mp_obj == NULL || mp_obj == mp_const_none) return NULL;
    if (!MP_OBJ_IS_OBJ(mp_obj)) nlr_raise(
            mp_obj_new_exception_msg(
                &mp_type_SyntaxError, "Struct argument is not an object!"));
    mp_lv_struct_t *mp_lv_struct = MP_OBJ_TO_PTR(get_native_obj(mp_obj));
    return mp_lv_struct;
}

STATIC inline size_t get_lv_struct_size(const mp_obj_type_t *type)
{
    mp_obj_t size_obj = mp_obj_dict_get(type->locals_dict, MP_OBJ_NEW_QSTR(MP_QSTR_SIZE));
    return (size_t)mp_obj_get_int(size_obj);
}

STATIC mp_obj_t make_new_lv_struct(
    const mp_obj_type_t *type,
    size_t n_args,
    size_t n_kw,
    const mp_obj_t *args)
{
    size_t size = get_lv_struct_size(type);
    mp_arg_check_num(n_args, n_kw, 0, 1, false);
    mp_lv_struct_t *self = m_new_obj(mp_lv_struct_t);
    *self = (mp_lv_struct_t){
        .base = {type}, 
        .data = malloc(size)
    };
    mp_lv_struct_t *other = n_args > 0? mp_to_lv_struct(cast(args[0], type)): NULL;
    if (other) {
        memcpy(self->data, other->data, size);
    }
    return MP_OBJ_FROM_PTR(self);
}

STATIC void *copy_buffer(const void *buffer, size_t size)
{
    void *new_buffer = malloc(size);
    memcpy(new_buffer, buffer, size);
    return new_buffer;
}

// Reference an existing lv struct (or part of it)

STATIC mp_obj_t lv_to_mp_struct(const mp_obj_type_t *type, void *lv_struct)
{
    mp_lv_struct_t *self = m_new_obj(mp_lv_struct_t);
    *self = (mp_lv_struct_t){
        .base = {type},
        .data = lv_struct
    };
    return MP_OBJ_FROM_PTR(self);
}

// Convert dict to struct

STATIC mp_obj_t dict_to_struct(mp_obj_t dict, const mp_obj_type_t *type)
{
    mp_obj_t mp_struct = make_new_lv_struct(type, 0, 0, NULL);
    mp_obj_t *native_dict = cast(dict, &mp_type_dict);
    mp_map_t *map = mp_obj_dict_get_map(native_dict);
    if (map == NULL) return mp_const_none;
    for (uint i = 0; i < map->alloc; i++) {
        mp_obj_t key = map->table[i].key;
        mp_obj_t value = map->table[i].value;
        if (key != MP_OBJ_NULL) {
            type->attr(mp_struct, mp_obj_str_get_qstr(key), (mp_obj_t[]){MP_OBJ_SENTINEL, value});
        }
    }
    return mp_struct;
}


// Blob is a wrapper for void* 

STATIC void mp_blob_print(const mp_print_t *print,
    mp_obj_t self_in,
    mp_print_kind_t kind)
{
    mp_printf(print, "lvgl Blob");
}

STATIC mp_int_t mp_blob_get_buffer(mp_obj_t self_in, mp_buffer_info_t *bufinfo, mp_uint_t flags) {
    (void)flags;
    mp_lv_struct_t *self = MP_OBJ_TO_PTR(self_in);

    bufinfo->buf = &self->data;
    bufinfo->len = sizeof(self->data);
    bufinfo->typecode = BYTEARRAY_TYPECODE;
    return 0;
}

STATIC const mp_obj_type_t mp_blob_type = {
    { &mp_type_type },
    .name = MP_QSTR_Blob,
    .print = mp_blob_print,
    //.make_new = make_new_blob,
    //.attr = mp_blob_attr,
    //.locals_dict = (mp_obj_dict_t*)&mp_blob_locals_dict,
    .buffer_p = { .get_buffer = mp_blob_get_buffer }
};

STATIC void* mp_to_ptr(mp_obj_t self_in)
{
    mp_buffer_info_t buffer_info;
    if (self_in == mp_const_none)
        return NULL;
    mp_get_buffer_raise(self_in, &buffer_info, MP_BUFFER_READ);
    const mp_obj_type_t *self_in_type = ((mp_obj_base_t*)self_in)->type;
    if (self_in_type == &mp_type_bytes || 
        self_in_type == &mp_type_bytearray ||
        self_in_type == &mp_type_memoryview ||
        self_in_type == &mp_type_str)
            return buffer_info.buf;
    else
    {
        void *result;
        if (buffer_info.len != sizeof(result) || buffer_info.typecode != BYTEARRAY_TYPECODE){
            nlr_raise(
                mp_obj_new_exception_msg_varg(
                    &mp_type_SyntaxError, "Cannot convert %s to pointer!", mp_obj_get_type_str(self_in)));
        }
        memcpy(&result, buffer_info.buf, sizeof(result));
        return result;
    }
}

STATIC inline mp_obj_t ptr_to_mp(void *data)
{
    if (data == NULL) return mp_const_none;
    return lv_to_mp_struct(&mp_blob_type, data);
}

// Cast pointer to struct

STATIC mp_obj_t mp_lv_cast(mp_obj_t type_obj, mp_obj_t ptr_obj)
{
    mp_lv_struct_t *self = m_new_obj(mp_lv_struct_t);
    *self = (mp_lv_struct_t){
        .base = {(const mp_obj_type_t*)type_obj}, 
        .data = mp_to_ptr(ptr_obj)
    };
    return self;
}

STATIC MP_DEFINE_CONST_FUN_OBJ_2(mp_lv_cast_obj, mp_lv_cast);
STATIC MP_DEFINE_CONST_CLASSMETHOD_OBJ(mp_lv_cast_class_method, MP_ROM_PTR(&mp_lv_cast_obj));

STATIC const mp_obj_type_t mp_obj_type;

// Callback function handling
// Callback is either a callable object or a pointer. If it's a callable object, set user_data to the callback.
// Multiple callbacks are kept per object/struct using a dict that associate callback name with callback object
// In case of an lv_obj_t, user_data is mp_lv_obj_t which contains a member "callbacks" for that dict.
// In case of a struct, user_data is a pointer to that dict directly

STATIC mp_obj_t get_callback_dict_from_user_data(void *user_data)
{
    if (user_data){
        mp_obj_t obj = MP_OBJ_FROM_PTR(user_data);
        return 
            MP_OBJ_IS_TYPE(obj, &mp_type_dict)? obj: // Handle the case of dict for a struct
            mp_get_callbacks(obj); // Handle the case of mp_lv_obj_t for an lv_obj_t
    }
    return NULL;
}

STATIC void *mp_lv_callback(mp_obj_t mp_callback, void *lv_callback, qstr callback_name, void **user_data_ptr)
{
    if (lv_callback && mp_obj_is_callable(mp_callback)){
        if (user_data_ptr){
            // user_data is either a dict of callbacks in case of struct, or a pointer to mp_lv_obj_t in case of lv_obj_t
            if (! (*user_data_ptr) ) *user_data_ptr = MP_OBJ_TO_PTR(mp_obj_new_dict(0)); // if it's NULL - it's a dict for a struct
            mp_obj_t callbacks = get_callback_dict_from_user_data(*user_data_ptr);
            mp_obj_dict_store(callbacks, MP_OBJ_NEW_QSTR(callback_name), mp_callback);
        }
        return lv_callback;
    } else {
        return mp_to_ptr(mp_callback);
    }
}

// Dict to hold user data for global callbacks (callbacks without context)

static void *mp_lv_user_data = NULL;

""")

#
# Add regular enums with integer values
#

enums = collections.OrderedDict()
for enum_def in enum_defs:
    member_names = [member.name for member in enum_def.type.values.enumerators if not member.name.startswith('_')]
    enum_name = commonprefix(member_names)
    enum_name = "_".join(enum_name.split("_")[:-1]) # remove suffix 
    enum = collections.OrderedDict()
    for member in enum_def.type.values.enumerators:
        if member.name.startswith('_'):
            continue
        member_name = member.name[len(enum_name)+1:]
        enum[member_name] = 'MP_ROM_INT(%s_%s)' % (enum_name, member_name)
    if len(enum) > 0: enums[enum_name] = enum

# Add special string enums

print ('''
/*
 * LVGL string constants
 */
''')

for enum_def in enum_defs:
    member_names = [str_enum_to_str(member.name) for member in enum_def.type.values.enumerators if lv_str_enum_pattern.match(member.name)]
    enum_name = commonprefix(member_names)
    enum_name = "_".join(enum_name.split("_")[:-1]) # remove suffix 
    enum = collections.OrderedDict()
    if enum_name:
        for member in enum_def.type.values.enumerators:
            full_name = str_enum_to_str(member.name)
            member_name = full_name[len(enum_name)+1:]
            print('MP_DEFINE_STR_OBJ(mp_%s, %s);' % (full_name, full_name))
            enum[member_name] = '&mp_%s' % full_name
        if len(enum) > 0: enums[enum_name] = enum

# eprint('-->\n%s' % enums)



# eprint(',\n'.join(sorted('%s : %s' % (name, get_type(blobs[name])) for name in blobs)))

#
# Callbacks helper functions
#

def decl_to_callback(decl):
    if (isinstance(decl.type, c_ast.PtrDecl) and isinstance(decl.type.type, c_ast.FuncDecl)):
        return (decl.name, decl.type.type)
        # print('/* callback: ADDED CALLBACK: %s\n%s */' % (gen.visit(decl.type.type), decl.type.type))
    elif isinstance(decl.type, c_ast.FuncDecl):
        return (decl.name, decl.type)
        # print('/* callback: ADDED CALLBACK: %s\n%s */' % (gen.visit(decl.type.type), decl.type.type))
    elif isinstance(decl.type, c_ast.TypeDecl) and hasattr(decl.type.type,'names'):
        func_typedef_name = decl.type.type.names[0]
        # print('/* --> callback: TYPEDEF CALLBACK: %s: %s */' % (decl.name, func_typedef_name))
        if func_typedef_name in func_typedefs:
            return (decl.name, func_typedefs[func_typedef_name].type.type)
            # print('/* callback: ADDED CALLBACK: %s\n%s */' % (func_typedef_name, func_typedefs[func_typedef_name]))
    else: return None

def get_user_data(func, func_name = None, containing_struct = None, containing_struct_name = None):
    args = func.args.params
    if not func_name: func_name = get_arg_name(func.type)
    # print('/* --> callback: func_name = %s */' % func_name)
    user_data_found = False
    user_data = 'None'
    if len(args) > 0 and isinstance(args[0].type, c_ast.PtrDecl):
        struct_arg_type_name = get_type(args[0].type.type, remove_quals = True)
        if containing_struct_name and struct_arg_type_name != containing_struct_name:
            return None
        if not containing_struct:
            try_generate_type(args[0].type)
            if struct_arg_type_name in structs: containing_struct = structs[struct_arg_type_name] 
            #if struct_arg_type_name in mp_to_lv:
            #    print('/* --> callback: %s First argument is %s */' % (gen.visit(func), struct_arg_type_name))
        if containing_struct:
            flatten_struct_decls = flatten_struct(containing_struct.decls)
            user_data = user_data_from_callback_func(func_name)
            user_data_found = user_data in [decl.name for decl in flatten_struct_decls]
            # print('/* --> callback: user_data=%s user_data_found=%s containing_struct=%s */' % (user_data, user_data_found, containing_struct))
               
    if user_data_found: return user_data
    else: return None


#
# Generate structs when needed
#

generated_structs = collections.OrderedDict()
struct_aliases = collections.OrderedDict()
callbacks_used_on_structs = []

def flatten_struct(struct_decls):
    result = []
    for decl in struct_decls:
        if is_struct(decl.type):
            result.extend(flatten_struct(decl.type.decls))
        else:
            result.append(decl)
    return result
    
def try_generate_struct(struct_name, struct, structs_in_progress = None):
    global lv_to_mp
    global mp_to_lv
    if not structs_in_progress: structs_in_progress = collections.OrderedDict()
    structs_in_progress[struct_name] = True
    if struct_name in mp_to_lv:
        return mp_to_lv[struct_name]
    # print('/* --> try_generate_struct %s: %s */' % (struct_name, gen.visit(struct)))
    flatten_struct_decls = flatten_struct(struct.decls)
    # Go over fields and try to generate type convertors for each
    # print('!! %s' % struct)
    # print('!!! %s' % flatten_struct_decls)
    write_cases = []
    read_cases = []
    for decl in flatten_struct_decls:
        # print('/* ==> decl %s: %s */' % (gen.visit(decl), decl))
        converted = try_generate_type(decl.type, structs_in_progress)
        type_name = get_type(decl.type, remove_quals = True)
        # print('/* --> %s: %s (%s)*/' % (decl.name, type_name, mp_to_lv[type_name] if type_name in mp_to_lv else '---'))
        # Handle the case of nested struct
        if not converted and is_struct(decl.type.type):
            parent_name = struct_name
            child_name = decl.type.declname
            type_name = '%s_%s_t' % (parent_name[:-2], child_name) 
            print('typedef typeof( (({parent}*)(0))->{child} ) {new_struct};'.format(
                parent = parent_name, child = child_name, new_struct = type_name))
            try_generate_struct(type_name, decl.type.type)

        # print('==> %s %s: %s' % (type_name, str(type_name in mp_to_lv), decl))

        if type_name not in mp_to_lv or type_name not in lv_to_mp:
            # eprint("[%s] %s or %s : %s" % (isinstance(decl.type,c_ast.PtrDecl), type_name, get_type(decl.type), decl.type))
            raise MissingConversionException('Missing conversion to %s when generating struct %s.%s' % (type_name, struct_name, get_name(decl)))             

        mp_to_lv_convertor = mp_to_lv[type_name]
        lv_to_mp_convertor = lv_to_mp_byref[type_name] if type_name in lv_to_mp_byref else lv_to_mp[type_name]
        
        cast = '(void*)' if isinstance(decl.type, c_ast.PtrDecl) else '' # needed when field is const. casting to void overrides it

        callback = decl_to_callback(decl)

        if callback:
            func_name, arg_type  = callback
            user_data = get_user_data(arg_type, func_name = func_name, containing_struct = struct, containing_struct_name = struct_name)
            callbacks_used_on_structs.append(callback)
            # Emit callback forward decl.
            if user_data in [user_data_decl.name for user_data_decl in flatten_struct_decls]:
                full_user_data = '&data->%s' % user_data
                lv_callback = '%s_callback' % func_name
                print('STATIC %s %s_callback(%s);' % (get_type(arg_type.type, remove_quals = False), func_name, gen.visit(arg_type.args)))
            else:
                full_user_data = 'NULL'
                lv_callback = 'NULL'
                if not user_data:
                    gen_func_error(decl, "Missing 'user_data' as a field of the first parameter of the callback function '%s_callback'" % func_name)
                else:
                    gen_func_error(decl, "Missing 'user_data' member in struct '%s'" % struct_name)
            write_cases.append('case MP_QSTR_{field}: data->{field} = {cast}mp_lv_callback(dest[1], {lv_callback} ,MP_QSTR_{field}, {user_data}); break; // converting to {type_name}'.
                format(field = decl.name, lv_callback = lv_callback, user_data = full_user_data, type_name = type_name, cast = cast))
            read_cases.append('case MP_QSTR_{field}: dest[0] = {convertor}({cast}data->{field}); break; // converting from {type_name}'.
                format(field = decl.name, convertor = lv_to_mp_convertor, type_name = type_name, cast = cast))
        else:
            user_data = None
            # Arrays must be handled by memcpy, otherwise we would get "assignment to expression with array type" error
            if isinstance(decl.type, c_ast.ArrayDecl):
                memcpy_size = 'sizeof(%s)*%s' % (gen.visit(decl.type.type), decl.type.dim.value)
                write_cases.append('case MP_QSTR_{field}: memcpy(&data->{field}, {cast}{convertor}(dest[1]), {size}); break; // converting to {type_name}'.
                    format(field = decl.name, convertor = mp_to_lv_convertor, type_name = type_name, cast = cast, size = memcpy_size))
                read_cases.append('case MP_QSTR_{field}: dest[0] = {convertor}({cast}&data->{field}); break; // converting from {type_name}'.
                    format(field = decl.name, convertor = lv_to_mp_convertor, type_name = type_name, cast = cast))
            else:
                write_cases.append('case MP_QSTR_{field}: data->{field} = {cast}{convertor}(dest[1]); break; // converting to {type_name}'.
                    format(field = decl.name, convertor = mp_to_lv_convertor, type_name = type_name, cast = cast))
                read_cases.append('case MP_QSTR_{field}: dest[0] = {convertor}({cast}data->{field}); break; // converting from {type_name}'.
                    format(field = decl.name, convertor = lv_to_mp_convertor, type_name = type_name, cast = cast))
    print('''
/*
 * Struct {struct_name}
 */

STATIC inline const mp_obj_type_t *get_mp_{struct_name}_type();

STATIC inline {struct_name}* mp_write_ptr_{struct_name}(mp_obj_t self_in)
{{
    mp_lv_struct_t *self = MP_OBJ_TO_PTR(cast(self_in, get_mp_{struct_name}_type()));
    return ({struct_name}*)self->data;
}}

#define mp_write_{struct_name}(struct_obj) *mp_write_ptr_{struct_name}(struct_obj)

STATIC inline mp_obj_t mp_read_ptr_{struct_name}({struct_name} *field)
{{
    return lv_to_mp_struct(get_mp_{struct_name}_type(), field);
}}

#define mp_read_{struct_name}(field) mp_read_ptr_{struct_name}(copy_buffer(&field, sizeof({struct_name})))
#define mp_read_byref_{struct_name}(field) mp_read_ptr_{struct_name}(&field)

STATIC void mp_{struct_name}_attr(mp_obj_t self_in, qstr attr, mp_obj_t *dest)
{{
    mp_lv_struct_t *self = MP_OBJ_TO_PTR(self_in);
    {struct_name} *data = ({struct_name}*)self->data;

    if (dest[0] == MP_OBJ_NULL) {{
        // load attribute
        switch(attr)
        {{
            {read_cases};
            default: field_not_found(MP_QSTR_{struct_name}, attr);
        }}
    }} else {{
        if (dest[1])
        {{
            // store attribute
            switch(attr)
            {{
                {write_cases};
                default: field_not_found(MP_QSTR_{struct_name}, attr);
            }}

            dest[0] = MP_OBJ_NULL; // indicate success
        }}
    }}
}}

STATIC void mp_{struct_name}_print(const mp_print_t *print,
    mp_obj_t self_in,
    mp_print_kind_t kind)
{{
    mp_printf(print, "lvgl struct {struct_name}");
}}

STATIC const mp_rom_map_elem_t mp_{struct_name}_locals_dict_table[] = {{
    {{ MP_ROM_QSTR(MP_QSTR_SIZE), MP_ROM_PTR(MP_ROM_INT(sizeof({struct_name}))) }},
    {{ MP_ROM_QSTR(MP_QSTR_cast), MP_ROM_PTR(&mp_lv_cast_class_method) }},
}};

STATIC MP_DEFINE_CONST_DICT(mp_{struct_name}_locals_dict, mp_{struct_name}_locals_dict_table);

STATIC const mp_obj_type_t mp_{struct_name}_type = {{
    {{ &mp_type_type }},
    .name = MP_QSTR_{struct_name},
    .print = mp_{struct_name}_print,
    .make_new = make_new_lv_struct,
    .attr = mp_{struct_name}_attr,
    .locals_dict = (mp_obj_dict_t*)&mp_{struct_name}_locals_dict,
    .buffer_p = {{ .get_buffer = mp_blob_get_buffer }}
}};

STATIC inline const mp_obj_type_t *get_mp_{struct_name}_type()
{{
    return &mp_{struct_name}_type;
}}
    '''.format(
            struct_name = struct_name,
            write_cases = ';\n                '.join(write_cases),
            read_cases  = ';\n            '.join(read_cases)));

    lv_to_mp[struct_name] = 'mp_read_%s' % struct_name
    lv_to_mp_byref[struct_name] = 'mp_read_byref_%s' % struct_name
    mp_to_lv[struct_name] = 'mp_write_%s' % struct_name
    lv_to_mp['%s *' % struct_name] = 'mp_read_ptr_%s' % struct_name
    mp_to_lv['%s *' % struct_name] = 'mp_write_ptr_%s' % struct_name
    lv_to_mp['const %s *' % struct_name] = 'mp_read_ptr_%s' % struct_name
    mp_to_lv['const %s *' % struct_name] = 'mp_write_ptr_%s' % struct_name
    generated_structs[struct_name] = True
    # print('/* --> struct "%s" generated! */' % (struct_name))
    return struct_name


#
# Generate types from typedefs when needed
#

def get_arg_name(arg):
    if isinstance(arg, c_ast.PtrDecl) or isinstance(arg, c_ast.FuncDecl):
        return get_arg_name(arg.type)
    return arg.declname if hasattr(arg, 'declname') else arg.name

# print("// Typedefs: " + ", ".join(get_arg_name(t) for t in typedefs))

def try_generate_type(type_ast, structs_in_progress = None):
    # print('/* --> try_generate_type %s: %s */' % (get_name(type_ast), type_ast))
    if isinstance(type_ast, basestring): raise SyntaxError('Internal error! try_generate_type argument is a string.')
    # Handle the case of a pointer 
    if isinstance(type_ast, c_ast.TypeDecl): 
        return try_generate_type(type_ast.type, structs_in_progress)
    type = get_name(type_ast)
    if isinstance(type, c_ast.Node):
        return None
    if type in mp_to_lv:
        return mp_to_lv[type]
    if isinstance(type_ast, (c_ast.PtrDecl, c_ast.ArrayDecl)): 
        type = get_name(type_ast.type.type)
        # print('/* --> try_generate_type IS PtrDecl!! %s: %s */' % (type, type_ast))
        if type in structs and ((not structs_in_progress) or type not in structs_in_progress): # prevent recursion
            generated_struct = try_generate_struct(type, structs[type], structs_in_progress) if type in structs else None
        ptr_type = get_type(type_ast, remove_quals=True)
        # print('/* --> PTR %s */' % ptr_type)
        if not ptr_type in mp_to_lv: mp_to_lv[ptr_type] = mp_to_lv['void *']
        if not ptr_type in lv_to_mp: lv_to_mp[ptr_type] = lv_to_mp['void *']
        return mp_to_lv[ptr_type]
    if type in structs:
        if try_generate_struct(type, structs[type]):
            return mp_to_lv[type]
    for new_type_ast in [x for x in typedefs if get_arg_name(x) == type]:
        new_type = get_type(new_type_ast, remove_quals=True)
        if new_type in structs:
            if (try_generate_struct(new_type, structs[new_type])):
                struct_aliases[new_type] = type
        if try_generate_type(new_type_ast, structs_in_progress):
           # print('/* --> try_generate_type TYPEDEF!! %s: %s */' % (type, mp_to_lv[new_type]))
           mp_to_lv[type] = mp_to_lv[new_type]
           type_ptr = '%s *' % type
           new_type_ptr = '%s *' % new_type
           if new_type_ptr in mp_to_lv:
               mp_to_lv[type_ptr] = mp_to_lv[new_type_ptr]
           if new_type in lv_to_mp:
               lv_to_mp[type] = lv_to_mp[new_type]
               if new_type in lv_to_mp_byref:
                   lv_to_mp_byref[type] = lv_to_mp_byref[new_type]
               if new_type_ptr in lv_to_mp:
                   lv_to_mp[type_ptr] = lv_to_mp[new_type_ptr]
           # print('/* --> %s = (%s) */' % (type, new_type))
           return mp_to_lv[type] 
    return None
  

#
# Emit C callback functions 
#

generated_callbacks = collections.OrderedDict()

def build_callback_func_arg(arg, index, func):
    arg_type = get_type(arg.type, remove_quals = True)
    cast = '(void*)' if isinstance(arg.type, c_ast.PtrDecl) else '' # needed when field is const. casting to void overrides it
    if not arg_type in lv_to_mp:
        try_generate_type(arg.type)
        if not arg_type in lv_to_mp:
            raise MissingConversionException("Callback: Missing conversion to %s" % arg_type)
    return 'args[{i}] = {convertor}({cast}arg{i});'.format(
                convertor = lv_to_mp[arg_type],
                i = index, cast = cast) 


def gen_callback_func(func, func_name = None):
    global mp_to_lv
    if func_name in generated_callbacks:
        return
    # print('/* --> callback: %s */' % (gen.visit(func)))
    args = func.args.params
    if not func_name: func_name = get_arg_name(func.type)
    # print('/* --> callback: func_name = %s */' % func_name)
    if is_global_callback(func):
        full_user_data = 'mp_lv_user_data'
    else:
        user_data = get_user_data(func, func_name)
        full_user_data = 'arg0->%s' % user_data
        # if user_data: print('/* --> callback: %s user_data found!! %s */' %(gen.visit(func), user_data))
        # else: print('/* --> callback: user_data NOT FOUND !! %s */' % (gen.visit(func)))
        if not user_data:
            raise MissingConversionException("Callback: user_data NOT FOUND! %s" % (gen.visit(func)))
        if len(args) < 1 or hasattr(args[0].type.type, 'names') and lv_base_obj_pattern.match(args[0].type.type.names[0]):
            raise MissingConversionException("Callback: First argument of callback function must be lv_obj_t")
    return_type = get_type(func.type, remove_quals = False)
    if return_type != 'void' and not return_type in mp_to_lv:
        try_generate_type(func.type)
        if not return_type in mp_to_lv:
            raise MissingConversionException("Callback return value: Missing conversion to %s" % return_type)

    #if not lv_callback_return_type_pattern.match(return_type):
    #    raise MissingConversionException("Callback: Can only handle callbaks that return lv_res_t or void")
    
    print("""
/*
 * Callback function {func_name}
 * {func_prototype}
 */

STATIC {return_type} {func_name}_callback({func_args})
{{
    mp_obj_t args[{num_args}];
    {build_args}
    mp_obj_t callbacks = get_callback_dict_from_user_data({user_data});
    {return_value_assignment}mp_call_function_n_kw(mp_obj_dict_get(callbacks, MP_OBJ_NEW_QSTR(MP_QSTR_{func_name})) , {num_args}, 0, args);
    return{return_value};
}}
""".format(
        func_prototype = gen.visit(func),
        func_name = func_name,
        return_type = return_type,
        func_args = ', '.join(["%s arg%s" % (get_type(arg.type, remove_quals = False), i) for i,arg in enumerate(args)]),
        num_args=len(args),
        build_args="\n    ".join([build_callback_func_arg(arg, i, func) for i,arg in enumerate(args)]),
        user_data=full_user_data,
        return_value_assignment = '' if return_type == 'void' else 'mp_obj_t callback_result = ',
        return_value='' if return_type == 'void' else ' %s(callback_result)' % mp_to_lv[return_type]))
    generated_callbacks[func_name] = True

#
# Emit Mpy function definitions
#

generated_funcs = collections.OrderedDict()

def build_mp_func_arg(arg, index, func, obj_name, first_arg):
    # print('/* --> ARG: %s */' % arg)
    fixed_arg = copy.deepcopy(arg)
    convert_array_to_ptr(fixed_arg)
    callback = decl_to_callback(arg)
    if callback:
        func_name, arg_type  = callback
        callback_name = '&%s_callback' % func_name
        try:
            if is_global_callback(arg_type):
                full_user_data = '&mp_lv_user_data'
            else:
                if index == 0:
                    raise MissingConversionException("Callback argument '%s' cannot be the first argument! We assume the first argument contains the user_data" % gen.visit(arg))
                user_data = get_user_data(arg_type, func_name)
                if not user_data:
                    raise MissingConversionException("Callback function '%s' must receive a struct pointer with user_data member as its first argument!" % gen.visit(arg))
                full_user_data = '&%s->%s' % (first_arg.name, user_data)
            gen_callback_func(arg_type, func_name)
            return 'void *{arg_name} = mp_lv_callback(args[{i}], {callback_name}, MP_QSTR_{func_name}, {full_user_data});'.format(
                i = index,
                arg_name = fixed_arg.name,
                callback_name = callback_name,
                func_name = func_name,
                obj = first_arg.name,
                full_user_data = full_user_data)
        except MissingConversionException as exp:
            gen_func_error(arg, exp)
            callback_name = 'NULL'
            full_user_data = 'NULL'
    arg_type = get_type(arg.type, remove_quals = True)
    # print('/* --> arg = %s, arg_type = %s */' %(gen.visit(arg), arg_type))
    if not arg_type in mp_to_lv:
        try_generate_type(arg.type)
        if not arg_type in mp_to_lv:
            raise MissingConversionException('Missing conversion to %s' % arg_type)
    return '{var} = {convertor}(args[{i}]);'.format(
            var = gen.visit(fixed_arg),
            convertor = mp_to_lv[arg_type],
            i = index) 

def gen_mp_func(func, obj_name):
    # print("/*\n{ast}\n*/").format(ast=func)
    args = func.type.args.params
    # Handle the case of a single function argument which is "void"
    if len(args)==1 and get_type(args[0].type, remove_quals = True) == "void":
        param_count = 0
        args = []
    else:
        param_count = len(args)
    return_type = get_type(func.type.type, remove_quals = False)
    # print('/* --> return_type = %s, func.type.type = %s\n%s */' % (return_type, gen.visit(func.type.type), func.type.type))
    if return_type == "void":        
        build_result = ""
        build_return_value = "mp_const_none" 
    else:
        if not return_type in lv_to_mp:
            try_generate_type(func.type.type)
            if not return_type in lv_to_mp:
                raise MissingConversionException("Missing convertion from %s" % return_type)
        build_result = "%s res = " % return_type
        cast = '(void*)' if isinstance(func.type.type, c_ast.PtrDecl) else '' # needed when field is const. casting to void overrides it
        build_return_value = "{type}({cast}res)".format(type = lv_to_mp[return_type], cast = cast)
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

STATIC MP_DEFINE_CONST_LV_FUN_OBJ_VAR(mp_{func}_obj, {count}, mp_{func}, {func});

 """.format(func=func.name, 
             print_func=gen.visit(func),
             count=param_count, 
             build_args="\n    ".join([build_mp_func_arg(arg, i, func, obj_name, args[0]) for i,arg in enumerate(args) if arg.name]), 
             send_args=", ".join(arg.name for arg in args if arg.name),
             build_result=build_result,
             build_return_value=build_return_value))
    generated_funcs[func.name] = True


def gen_func_error(method, exp):
    global funcs
    print("""
/*
 * Function NOT generated:
 * {problem}
 * {method}
 */
    """.format(method=gen.visit(method) if isinstance(method, c_ast.Node) else method, problem=exp))
    try:
        funcs.remove(method)
    except:
        pass
                 

#
# Emit Mpy objects definitions
#

enum_referenced = collections.OrderedDict()

def gen_obj_methods(obj_name):
    global enums
    members = ["{{ MP_ROM_QSTR(MP_QSTR_{method_name}), MP_ROM_PTR(&mp_{method}_obj) }}".
                    format(method=method.name, method_name=method_name_from_func_name(method.name)) for method in get_methods(obj_name)]
    # add parent methods
    parent_members = []
    if obj_name in parent_obj_names and parent_obj_names[obj_name] != None:
        parent_members += gen_obj_methods(parent_obj_names[obj_name])
    # add enum members
    enum_members = ["{{ MP_ROM_QSTR(MP_QSTR_{enum_member}), MP_ROM_PTR({enum_member_value}) }}".
                    format(enum_member = get_enum_member_name(enum_memebr_name), enum_member_value = get_enum_value(obj_name, enum_memebr_name)) for enum_memebr_name in get_enum_members(obj_name)]
    # add enums that match object name
    obj_enums = [enum_name for enum_name in enums.keys() if is_method_of(enum_name, obj_name)]
    enums_memebrs = ["{{ MP_ROM_QSTR(MP_QSTR_{name}), MP_ROM_PTR(&mp_{enum}_type) }}".
                    format(name=method_name_from_func_name(enum_name), enum=enum_name) for enum_name in obj_enums]
    for enum_name in obj_enums:
        enum_referenced[enum_name] = True
    return members + parent_members + enum_members + enums_memebrs

def gen_obj(obj_name):
    should_add_base_methods = obj_name != 'obj'
    for method in get_methods(obj_name):
        try:
            gen_mp_func(method, obj_name)
        except MissingConversionException as exp:
            gen_func_error(method, exp)
       
    # print([method.name for method in methods])
    ctor = """
STATIC mp_obj_t {obj}_make_new(
    const mp_obj_type_t *type,
    size_t n_args,
    size_t n_kw,
    const mp_obj_t *args)
{{
    return make_new(&lv_{obj}_create, type, n_args, n_kw, args);           
}}
"""

    print("""
/*
 * lvgl {obj} object definitions
 */
    """.format(obj = obj_name))

    print("""
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

{ctor}

STATIC const mp_obj_type_t mp_{obj}_type = {{
    {{ &mp_type_type }},
    .name = MP_QSTR_{obj},
    .print = {obj}_print,
    {make_new}
    .locals_dict = (mp_obj_dict_t*)&{obj}_locals_dict,
    .buffer_p = {{ .get_buffer = mp_obj_get_buffer }},
    .parent = {parent},
}};
    """.format(obj = obj_name, base_obj = base_obj_name,
            base_class = '&mp_%s_type' % base_obj_name if should_add_base_methods else 'NULL',
            locals_dict_entries = ",\n    ".join(gen_obj_methods(obj_name)),
            ctor = ctor.format(obj = obj_name) if has_ctor(obj_name) else '',
            make_new = '.make_new = %s_make_new,' % obj_name if has_ctor(obj_name) else '',
            parent = 'NULL' # parent = '&mp_%s_type' % parent_obj_names[obj_name] if obj_name in parent_obj_names and parent_obj_names[obj_name] else 'NULL',
            ))

#
# Generate Enum objects
#

for enum_name in list(enums.keys()):
    gen_obj(enum_name)

#
# Generate all other objects. Generate parent objects first
#

generated_obj_names = collections.OrderedDict()
for obj_name in obj_names:
    # eprint("--> %s [%s]" % (obj_name, ", ".join([name for name in generated_obj_names])))
    parent_obj_name = parent_obj_names[obj_name] if obj_name in parent_obj_names else None

    while parent_obj_name != None and not parent_obj_name in generated_obj_names:
        gen_obj(parent_obj_name)
        generated_obj_names[parent_obj_name] = True
        parent_obj_name = parent_obj_names[parent_obj_name] if parent_obj_name in parent_obj_names else None

    if not obj_name in generated_obj_names:
        # eprint("--> gen obj %s" % obj_name)
        gen_obj(obj_name)
        generated_obj_names[obj_name] = True

print ("""
STATIC inline const mp_obj_type_t *get_BaseObj_type()
{{
    return &mp_{base_obj}_type;
}}
""".format(base_obj=base_obj_name));

#
# Generate all module functions (not including method functions which were already generated)
#

print("""
/* 
 *
 * Global Module Functions
 *
 */
""")

module_funcs = [func for func in funcs if not func.name in generated_funcs]
for module_func in module_funcs[:]:
    try:
        gen_mp_func(module_func, None)
    except MissingConversionException as exp:
        gen_func_error(module_func, exp)
        module_funcs.remove(module_func)
    
functions_not_generated = [func.name for func in funcs if not func.name in generated_funcs]
if len(functions_not_generated) > 0:
    print("""
/*
 * Functions not generated:
 * {funcs}
 *
 */

""".format(funcs = "\n * ".join(functions_not_generated)))

#
# Generate globals
#

def gen_global(global_name, global_type_ast):
    global_type = get_type(global_type_ast, remove_quals=True)
    try_generate_type(global_type_ast)
    if not global_type in generated_structs:
        raise MissingConversionException('Missing conversion to %s when generating global %s' % (global_type, global_name))

    print("""
/*
 * lvgl {global_name} global definitions
 */

STATIC const mp_lv_struct_t mp_{global_name} = {{
    {{ &mp_{struct_name}_type }},
    &{global_name}
}};
    """.format(
        global_name = global_name,
        struct_name = global_type))

generated_globals = []
for global_name in blobs:
    try:
        gen_global(global_name, blobs[global_name])
        generated_globals.append(global_name)
    except MissingConversionException as exp:
        gen_func_error(global_name, exp)

#
# Generate callback functions
#

# for func_typedef in func_typedefs:
#     func = func_typedef.type.type
#     try:
#         gen_callback_func(func)
#     except MissingConversionException as exp:
#         gen_func_error(func, exp)
#         func_name = get_arg_name(func.type)
#         lv_to_mp[func_name] = lv_to_mp['void *']
#         mp_to_lv[func_name] = mp_to_lv['void *']

for (func_name, func) in callbacks_used_on_structs:
    try:
        gen_callback_func(func, func_name = func_name)
    except MissingConversionException as exp:
        gen_func_error(func, exp)
        # func_name = get_arg_name(func.type)
        # lv_to_mp[func_name] = lv_to_mp['void *']
        # mp_to_lv[func_name] = mp_to_lv['void *']

#
# Emit Mpy Module definition
#

print("""

/*
 * lvgl module definitions
 */

STATIC const mp_rom_map_elem_t lvgl_globals_table[] = {{
    {{ MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_lvgl) }},
    {objects},
    {functions},
    {enums},
    {structs},
    {struct_aliases},
    {blobs}
}};
""".format(
        objects = ',\n    '.join(['{{ MP_ROM_QSTR(MP_QSTR_{obj}), MP_ROM_PTR(&mp_{obj}_type) }}'.
            format(obj = o) for o in obj_names]),
        functions =  ',\n    '.join(['{{ MP_ROM_QSTR(MP_QSTR_{name}), MP_ROM_PTR(&mp_{func}_obj) }}'.
            format(name = simplify_identifier(f.name), func = f.name) for f in module_funcs]),
        enums = ',\n    '.join(["{{ MP_ROM_QSTR(MP_QSTR_{name}), MP_ROM_PTR(&mp_{enum}_type) }}".
            format(name = get_enum_name(enum_name), enum=enum_name) for enum_name in enums.keys() if enum_name not in enum_referenced]),
        structs = ',\n    '.join(["{{ MP_ROM_QSTR(MP_QSTR_{name}), MP_ROM_PTR(&mp_{struct_name}_type) }}".
            format(name = simplify_identifier(struct_name), struct_name = struct_name) for struct_name in structs.keys() if struct_name in generated_structs]),
        struct_aliases = ',\n    '.join(["{{ MP_ROM_QSTR(MP_QSTR_{alias_name}), MP_ROM_PTR(&mp_{struct_name}_type) }}".
            format(struct_name = struct_name, alias_name = simplify_identifier(struct_aliases[struct_name])) for struct_name in struct_aliases.keys()]),
        blobs = ',\n    '.join(["{{ MP_ROM_QSTR(MP_QSTR_{name}), MP_ROM_PTR(&mp_{global_name}) }}".
            format(name = simplify_identifier(global_name), global_name = global_name) for global_name in generated_globals])))
        

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

