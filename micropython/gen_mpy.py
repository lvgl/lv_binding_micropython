# TODO
# - On print extensions, print the reflected internal representation of the object
# - Verify that when mp_obj is given it is indeed the right type (mp_lv_obj_t). Report error if not. can be added to mp_to_lv.
# - Implement inheritance instead of embed base methods (how? seems it's not supported, see https://github.com/micropython/micropython/issues/1159)

from __future__ import print_function
import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    
    
from sys import argv
from pycparser import c_parser, c_ast, c_generator
from argparse import ArgumentParser
import subprocess, re
from os.path import commonprefix

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
# lv text patterns
# IGNORECASE and "lower" are used to match both function and enum names
# 

base_obj_name = 'obj'
lv_ext_pattern = re.compile('^lv_([^_]+)_ext_t')
lv_obj_pattern = re.compile('^lv_([^_]+)', re.IGNORECASE)
lv_func_pattern = re.compile('^lv_(.+)', re.IGNORECASE)
create_obj_pattern = re.compile('^lv_([^_]+)_create')
lv_method_pattern = re.compile('^lv_[^_]+_(.+)', re.IGNORECASE)
lv_base_obj_pattern = re.compile('^(struct _){0,1}lv_%s_t' % (base_obj_name))
lv_callback_return_type_pattern = re.compile('^((void)|(lv_res_t))')


def obj_name_from_ext_name(ext_name):
    return re.match(lv_ext_pattern, ext_name).group(1)

def obj_name_from_func_name(func_name):
    return re.match(lv_obj_pattern, func_name).group(1)

def ctor_name_from_obj_name(obj_name):
    return 'lv_%s_create' % obj_name

def is_method_of(func_name, obj_name):
    return func_name.lower().startswith(('lv_%s_' % obj_name).lower())
    
def method_name_from_func_name(func_name):
    return re.match(lv_method_pattern, func_name).group(1)

def get_enum_name(enum):
    prefix = 'lv_'
    return enum[len(prefix):]

def get_enum_value(obj_name, enum_member):
    return '%s_%s' % (obj_name, enum_member)


#
# Initialization, data structures, helper functions
#

parser = c_parser.CParser()
gen = c_generator.CGenerator()
ast = parser.parse(s, filename='<none>')
typedefs = [x.type for x in ast.ext if isinstance(x, c_ast.Typedef)]
func_defs = [x.decl for x in ast.ext if isinstance(x, c_ast.FuncDef)]
func_decls = [x for x in ast.ext if isinstance(x, c_ast.Decl) and isinstance(x.type, c_ast.FuncDecl)]
funcs = func_defs + func_decls
excluded_ctors = [ctor_name_from_obj_name(obj) for obj in args.exclude]
obj_ctors = [func for func in funcs if create_obj_pattern.match(func.name) and not func.name in excluded_ctors]
for obj_ctor in obj_ctors:
    funcs.remove(obj_ctor)
obj_names = [re.match(create_obj_pattern, ctor.name).group(1) for ctor in obj_ctors]

def has_ctor(obj_name):
    return ctor_name_from_obj_name(obj_name) in [ctor.name for ctor in obj_ctors]
        
def get_ctor(obj_name):
    global obj_ctors
    return next(ctor for ctor in obj_ctors if ctor.name == ctor_name_from_obj_name(obj_name))

def get_methods(obj_name):
    global funcs
    return [func for func in funcs if is_method_of(func.name,obj_name) and (not func.name == ctor_name_from_obj_name(obj_name))]

def get_enum_members(obj_name):
    global enums
    if not obj_name in enums:
        return []
    prefix_len = len(obj_name)+1
    return [enum_member_name[prefix_len:] for enum_member_name, value in enums[obj_name].items()]
   
# By default all object (except base_obj) inherit from base_obj. Later we refine this according to hierarchy.
parent_obj_names = {child_name: base_obj_name for child_name in obj_names if child_name != base_obj_name} 
parent_obj_names[base_obj_name] = None

# Populate inheritance hierarchy according to lv_ext structures
exts = {obj_name_from_ext_name(ext.name): ext for ext in ast.ext if hasattr(ext, 'name') and ext.name is not None and lv_ext_pattern.match(ext.name)}
for obj_name, ext in exts.items():
    try:
        parent_ext_name = ext.type.type.decls[0].type.type.names[0]
        if lv_ext_pattern.match(parent_ext_name):
            parent_obj_names[obj_name] = obj_name_from_ext_name(parent_ext_name)
    except AttributeError:
        pass

# Parse Enums

enum_defs = [x for x in ast.ext if hasattr(x,'type') and isinstance(x.type, c_ast.Enum)]
enums = {}
for enum_def in enum_defs:
    member_names = [member.name for member in enum_def.type.values.enumerators]
    enum_name = commonprefix(member_names)
    enum_name = "_".join(enum_name.split("_")[:-1]) # remove suffix 
    enum = {}
    next_value = 0
    for member in enum_def.type.values.enumerators:
        if member.value == None:
            value = next_value
        else:
            value = int(member.value.value, 0)
        enum[member.name] = value
        next_value = value + 1
    enums[enum_name] = enum

# eprint(enums)

# parse function pointers
func_typedefs = [t for t in ast.ext if isinstance(t, c_ast.Typedef) and isinstance(t.type, c_ast.PtrDecl) and isinstance(t.type.type, c_ast.FuncDecl)]


#
# Type convertors
#

#action_index = {}
#
#def handle_lv_action(arg, index, func, obj_name):
#    global action_index
#    args = func.type.args.params
#    if not obj_name in action_index:
#        action_index[obj_name] = 0
#    prev_arg_type = mp_to_lv[get_arg_type(args[index-1].type)] if index > 0 else None
#    eprint("--> %s, %s" % (get_arg_type(args[index-1].type), mp_to_lv[get_arg_type(args[index-1].type)]))
#    if prev_arg_type  in enums:
#        variable_index = "%d + %s" % (action_index[obj_name], args[index-1].name)
#        action_index[obj_name] += len(enums[prev_arg_type])
#    else:
#        variable_index = "{action_index}".format(action_index = action_index[obj_name])
#        action_index[obj_name] += 1
#    return """mp_lv_obj_t *mp_lb_obj = lv_obj_get_free_ptr(obj);
#    {var} = mp_lb_obj.actions[{variable_index}];""".format(
#        var = gen.visit(arg), variable_index = variable_index)


class MissingConversionException(ValueError):
    pass

mp_to_lv = {
    'bool'                      : 'mp_obj_is_true',
    'char*'                     : '(char*)mp_obj_str_get_str',
    'const char*'               : 'mp_obj_str_get_str',
    'lv_obj_t*'                 : 'mp_to_lv',
    'const lv_obj_t*'           : 'mp_to_lv',
    'struct _lv_obj_t*'         : 'mp_to_lv',
    'const struct _lv_obj_t*'   : 'mp_to_lv',
    'uint8_t'                   : '(uint8_t)mp_obj_int_get_checked',
    'uint16_t'                  : '(uint16_t)mp_obj_int_get_checked',
    'uint32_t'                  : '(uint32_t)mp_obj_int_get_checked',
    'int8_t'                    : '(int8_t)mp_obj_int_get_checked',
    'int16_t'                   : '(int16_t)mp_obj_int_get_checked',
    'int32_t'                   : '(int32_t)mp_obj_int_get_checked',
#    'lv_action_t'               : handle_lv_action
}

lv_to_mp = {
    'bool'                      : 'convert_to_bool',
    'char*'                     : 'convert_to_str',
    'const char*'               : 'convert_to_str',
    'lv_obj_t*'                 : 'lv_to_mp',
    'const lv_obj_t*'           : 'lv_to_mp',
    'struct _lv_obj_t*'         : 'lv_to_mp',
    'const struct _lv_obj_t*'   : 'lv_to_mp',
    'uint8_t'                   : 'mp_obj_new_int_from_uint',
    'uint16_t'                  : 'mp_obj_new_int_from_uint',
    'uint32_t'                  : 'mp_obj_new_int_from_uint',
    'int8_t'                    : 'mp_obj_new_int',
    'int16_t'                   : 'mp_obj_new_int',
    'int32_t'                   : 'mp_obj_new_int',
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
 * Generating Objects: {objs}
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
        objs=", ".join(['%s(%s)' % (objname, parent_obj_names[objname]) for objname in obj_names]),
        lv_headers='\n'.join('#include "%s"' % header for header in args.input)))


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
    mp_obj_t *action;
} mp_lv_obj_t;

STATIC inline lv_obj_t *mp_to_lv(mp_obj_t *mp_obj)
{
    if (mp_obj == NULL || mp_obj == mp_const_none) return NULL;
    mp_lv_obj_t *mp_lv_obj = MP_OBJ_TO_PTR(mp_obj);
    return mp_lv_obj->lv_obj;
}

STATIC inline mp_obj_t *mp_to_lv_action(mp_obj_t *mp_obj)
{
    if (mp_obj == NULL || mp_obj == mp_const_none) return NULL;
    mp_lv_obj_t *mp_lv_obj = MP_OBJ_TO_PTR(mp_obj);
    return mp_lv_obj->action;
}

STATIC inline void set_action(mp_obj_t *mp_obj, mp_obj_t *action)
{
    if (mp_obj == NULL || mp_obj == mp_const_none) return;
    mp_lv_obj_t *mp_lv_obj = MP_OBJ_TO_PTR(mp_obj);
    mp_lv_obj->action = action;
}

STATIC inline const mp_obj_type_t *get_BaseObj_type();

STATIC inline mp_obj_t *lv_to_mp(lv_obj_t *lv_obj)
{
    mp_lv_obj_t *self = lv_obj_get_free_ptr(lv_obj);
    if (!self) 
    {
        self = m_new_obj(mp_lv_obj_t);
        *self = (mp_lv_obj_t){
            .base = {get_BaseObj_type()},
            .lv_obj = lv_obj,
            .action = NULL
        };
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
    mp_arg_check_num(n_args, n_kw, 1, 2, false);
    mp_lv_obj_t *self = m_new_obj(mp_lv_obj_t);
    lv_obj_t *parent = mp_to_lv(args[0]);
    lv_obj_t *copy = n_args > 1? mp_to_lv(args[1]): NULL;
    *self = (mp_lv_obj_t){
        .base = {type}, 
        .lv_obj = create(parent, copy),
        .action = NULL
    };
    lv_obj_set_free_ptr(self->lv_obj, self);
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
# Generate types from typedefs when needed
#

def get_arg_type(arg):
    indirect_level = 0
    while isinstance(arg, c_ast.PtrDecl):
        indirect_level += 1
        arg = arg.type
    return '{quals}{type}{indirection}'.format(
        quals=''.join('%s ' % qual for qual in arg.quals) if hasattr(arg, 'quals') else '',
        type=gen.visit(arg),
        indirection='*' * indirect_level)

def get_arg_name(arg):
    if isinstance(arg, c_ast.PtrDecl) or isinstance(arg, c_ast.FuncDecl):
        return get_arg_name(arg.type)
    return arg.declname if hasattr(arg, 'declname') else arg.name

# print "// Typedefs: " + ", ".join(get_arg_name(t) for t in typedefs)

def try_generate_type(type):
    global typedefs
    global mp_to_lv, lv_to_mp
    if type in mp_to_lv:
        return True
    for new_type in [get_arg_type(x) for x in typedefs if get_arg_name(x) == type]:
        if try_generate_type(new_type):
           mp_to_lv[type] = mp_to_lv[new_type]
           if new_type in lv_to_mp:
               lv_to_mp[type] = lv_to_mp[new_type]
           # print "// %s = (%s)" % (type, new_type)
           return True
    return False
  

#
# Emit C callback functions 
#

def build_callback_func_arg(arg, index, func):
    arg_type = get_arg_type(arg.type)
    if not arg_type in lv_to_mp:
        try_generate_type(arg_type)
        if not arg_type in lv_to_mp:
            raise MissingConversionException("Callback: Missing conversion to %s" % arg_type)
    return lv_to_mp[arg_type](arg, index, func, obj_name) if callable(lv_to_mp[arg_type]) else \
        'args[{i}] = {convertor}(arg{i});'.format(
            convertor = lv_to_mp[arg_type],
            i = index) 


def gen_callback_func(func):
    global mp_to_lv
    args = func.args.params
    if len(args) < 1 or hasattr(args[0].type.type, 'names') and lv_base_obj_pattern.match(args[0].type.type.names[0]):
        raise MissingConversionException("Callback: First argument of callback function must be lv_obj_t")
    func_name = get_arg_name(func.type)
    return_type = get_arg_type(func.type)
    if not lv_callback_return_type_pattern.match(return_type):
        raise MissingConversionException("Callback: Can only handle callbaks that return lv_res_t or void")
    
    print("""
/*
 * Callback function {func_name}
 * {func_prototype}
 */

STATIC {return_type} {func_name}_callback({func_args})
{{
    mp_obj_t args[{num_args}];
    {build_args}
    mp_obj_t action = mp_to_lv_action(args[0]);
    mp_obj_t arg_list = mp_obj_new_list({num_args}, args);
    bool schedule_result = mp_sched_schedule(action, arg_list, NULL);
    return{return_value};
}}
""".format(
        func_prototype = gen.visit(func),
        func_name = func_name,
        return_type = return_type,
        func_args = ', '.join(["%s arg%s" % (get_arg_type(arg.type), i) for i,arg in enumerate(args)]),
        num_args=len(args),
        build_args="\n    ".join([build_callback_func_arg(arg, i, func) for i,arg in enumerate(args)]),
        return_value='' if return_type=='void' else ' schedule_result? LV_RES_OK: LV_RES_INV'))
    def register_callback(arg, index, func, obj_name):
        return """set_action(args[0], args[{i}]);
    {arg} = &{func_name}_callback;""".format(
            i = index,
            arg = gen.visit(arg),
            func_name = func_name)
    mp_to_lv[func_name] = register_callback

#
# Emit Mpy function definitions
#

generated_funcs = {}

def build_mp_func_arg(arg, index, func, obj_name):
    arg_type = get_arg_type(arg.type)
    if not arg_type in mp_to_lv:
        try_generate_type(arg_type)
        if not arg_type in mp_to_lv:
            raise MissingConversionException("Missing conversion to %s" % arg_type)
    return mp_to_lv[arg_type](arg, index, func, obj_name) if callable(mp_to_lv[arg_type]) else \
        '{var} = {convertor}(args[{i}]);'.format(
            var = gen.visit(arg),
            convertor = mp_to_lv[arg_type],
            i = index) 

def gen_mp_func(func, obj_name):
    # print("/*\n{ast}\n*/").format(ast=func)
    args = func.type.args.params
    # Handle the case of a single function argument which is "void"
    if len(args)==1 and get_arg_type(args[0].type) == "void":
        param_count = 0
    else:
        param_count = len(args)
    return_type = get_arg_type(func.type.type)
    if return_type == "void":        
        build_result = ""
        build_return_value = "mp_const_none" 
    else:
        if not return_type in lv_to_mp:
            try_generate_type(return_type)
            if not return_type in lv_to_mp:
                raise MissingConversionException("Missing convertion from %s" % return_type)
        build_result = "%s res = " % return_type
        build_return_value = lv_to_mp[return_type](func, obj_name) if callable(lv_to_mp[return_type]) else \
            "%s(res)" % lv_to_mp[return_type]
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

 """.format(func=func.name, 
             print_func=gen.visit(func),
             count=param_count, 
             build_args="\n    ".join([build_mp_func_arg(arg, i, func, obj_name) for i,arg in enumerate(args) if arg.name]), 
             send_args=", ".join(arg.name for arg in args if arg.name),
             build_result=build_result,
             build_return_value=build_return_value))
    generated_funcs[func] = True


def gen_func_error(method, exp):
    global funcs
    print("""
/*
 * Function NOT generated:
 * {problem}
 * {method}
 */
    """.format(method=gen.visit(method), problem=exp))
    try:
        funcs.remove(method)
    except:
        pass
                 

#
# Emit Mpy objects definitions
#

enum_referenced = {}

def gen_obj_methods(obj_name):
    global enums
    members = ["{{ MP_OBJ_NEW_QSTR(MP_QSTR_{method_name}), MP_ROM_PTR(&mp_{method}_obj) }}".
                    format(method=method.name, method_name=method_name_from_func_name(method.name)) for method in get_methods(obj_name)]
    # add parent methods
    parent_members = []
    if obj_name in parent_obj_names and parent_obj_names[obj_name] != None:
        parent_members += gen_obj_methods(parent_obj_names[obj_name])
    # add enum members
    enum_members = ["{{ MP_OBJ_NEW_QSTR(MP_QSTR_{enum_member}), MP_ROM_PTR(MP_ROM_INT({enum_member_value})) }}".
                    format(enum_member = enum_memebr_name, enum_member_value = get_enum_value(obj_name, enum_memebr_name)) for enum_memebr_name in get_enum_members(obj_name)]
    # add enums that match object name
    obj_enums = [enum_name for enum_name in enums.keys() if is_method_of(enum_name, obj_name)]
    enums_memebrs = ["{{ MP_OBJ_NEW_QSTR(MP_QSTR_{name}), MP_ROM_PTR(&mp_{enum}_type) }}".
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
}};
    """.format(obj = obj_name, base_obj = base_obj_name,
            base_class = '&mp_%s_type' % base_obj_name if should_add_base_methods else 'NULL',
            locals_dict_entries = ",\n    ".join(gen_obj_methods(obj_name)),
            ctor = ctor.format(obj = obj_name) if has_ctor(obj_name) else '',
            make_new = '.make_new = %s_make_new,' % obj_name if has_ctor(obj_name) else '',
            ))


# Generate Enum objects

for enum_name in list(enums.keys()):
    gen_obj(enum_name)


# Generate callback functions

for func_typedef in func_typedefs:
    func = func_typedef.type.type
    try:
        gen_callback_func(func)
    except MissingConversionException as exp:
        gen_func_error(func, exp)

# Generate all other objects. Generate parent objects first

generated_obj_names = {}
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


# Generate all module functions (not including method functions which were already generated)

print("""
/* 
 *
 * Global Module Functions
 *
 */
""")

module_funcs = [func for func in funcs if not func in generated_funcs]
for module_func in module_funcs[:]:
    try:
        gen_mp_func(module_func, None)
    except MissingConversionException as exp:
        gen_func_error(module_func, exp)
        module_funcs.remove(module_func)
    
functions_not_generated = [func.name for func in funcs if not func in generated_funcs]
if len(functions_not_generated) > 0:
    print("""
/*
 * Functions not generated:
 * {funcs}
 *
 */

""".format(funcs = "\n * ".join(functions_not_generated)))

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
{{
    lv_mp_init();
    return mp_const_none;
}}

STATIC MP_DEFINE_CONST_FUN_OBJ_0(lv_mp_init_obj, _lv_mp_init);

STATIC const mp_rom_map_elem_t lvgl_globals_table[] = {{
    {{ MP_OBJ_NEW_QSTR(MP_QSTR___name__), MP_OBJ_NEW_QSTR(MP_QSTR_lvgl) }},
    {{ MP_OBJ_NEW_QSTR(MP_QSTR___init__), MP_ROM_PTR(&lv_mp_init_obj) }},
    {objects},
    {functions},
    {enums},
}};
""".format(
        objects = ',\n    '.join(['{{ MP_OBJ_NEW_QSTR(MP_QSTR_{obj}), MP_ROM_PTR(&mp_{obj}_type) }}'.
            format(obj = o) for o in obj_names]),
        functions =  ',\n    '.join(['{{ MP_OBJ_NEW_QSTR(MP_QSTR_{func_name}), MP_ROM_PTR(&mp_{func}_obj) }}'.
            format(func = f.name, func_name = re.match(lv_func_pattern, f.name).group(1)) for f in module_funcs]),
        enums = ',\n    '.join(["{{ MP_OBJ_NEW_QSTR(MP_QSTR_{name}), MP_ROM_PTR(&mp_{enum}_type) }}".
            format(name=get_enum_name(enum_name), enum=enum_name) for enum_name in enums.keys() if enum_name not in enum_referenced])))
        

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

