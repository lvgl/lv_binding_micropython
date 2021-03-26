
find_package(Python3 REQUIRED COMPONENTS Interpreter)

set(LV_BINDINGS_DIR ${MICROPY_DIR}/lib/lv_bindings)

# Common function for creating LV bindings

function(lv_bindings)
    # LV_PP_OPTIONS and LV_GEN_OPTIONS must be quoted when calling lv_bindings since they are lists.

    set(_options)
    set(_one_value_args OUTPUT INPUT FILTER)
    set(_multi_value_args DEPENDS PP_OPTIONS GEN_OPTIONS)
    cmake_parse_arguments(
        PARSE_ARGV 0 LV 
        "${_options}" 
        "${_one_value_args}" 
        "${_multi_value_args}"
      )

    set(LV_PP ${LV_OUTPUT}.pp)
    set(LV_MPY_METADATA ${LV_OUTPUT}.json)

    add_custom_command(
        OUTPUT 
            ${LV_PP}
        COMMAND
        ${CMAKE_C_COMPILER} -E ${LV_PP_OPTIONS} ${LV_CFLAGS} -I ${LV_BINDINGS_DIR}/pycparser/utils/fake_libc_include ${MICROPY_CPP_FLAGS} ${LV_INPUT} > ${LV_PP}
        DEPENDS
            ${LV_INPUT}
            ${LV_DEPENDS}
            ${LV_BINDINGS_DIR}/pycparser/utils/fake_libc_include
        VERBATIM
        COMMAND_EXPAND_LISTS
    )

    add_custom_command(
        OUTPUT
            ${LV_OUTPUT}
        COMMAND
            ${Python3_EXECUTABLE} ${LV_BINDINGS_DIR}/gen/gen_mpy.py ${LV_GEN_OPTIONS} -MD ${LV_MPY_METADATA} -E ${LV_PP} ${LV_INPUT} > ${LV_OUTPUT}
        DEPENDS
            ${LV_BINDINGS_DIR}/gen/gen_mpy.py
            ${LV_PP}
        VERBATIM
        COMMAND_EXPAND_LISTS
    )

endfunction()

# Definitions for specific bindings

set(LVGL_DIR ${LV_BINDINGS_DIR}/lvgl)
set(LV_PNG_DIR ${LV_BINDINGS_DIR}/driver/png/lodepng)

set(LV_MP ${CMAKE_BINARY_DIR}/lv_mp.c)
set(LV_PNG ${CMAKE_BINARY_DIR}/lv_png.c)
set(LV_PNG_C ${CMAKE_BINARY_DIR}/lv_png_c.c)
set(LV_ESPIDF ${CMAKE_BINARY_DIR}/lv_espidf.c)

# Function for creating all specific bindings

function(all_lv_bindings)

    # LVGL bindings

    lv_bindings(
        OUTPUT
            ${LV_MP}
        INPUT
            ${LVGL_DIR}/lvgl.h
        DEPENDS
            ${LVGL_DIR}
        GEN_OPTIONS
            -M lvgl -MP lv
    )
        
    # LODEPNG bindings

    configure_file(${LV_PNG_DIR}/lodepng.cpp ${LV_PNG_C} COPYONLY)
    idf_build_set_property(COMPILE_DEFINITIONS "${LV_PNG_PP_OPTIONS}" APPEND)
    lv_bindings(
        OUTPUT
            ${LV_PNG}
        INPUT
            ${LV_PNG_DIR}/lodepng.h
        DEPENDS
            ${LV_PNG_DIR}
        PP_OPTIONS
            -DLODEPNG_NO_COMPILE_ENCODER -DLODEPNG_NO_COMPILE_DISK -DLODEPNG_NO_COMPILE_ALLOCATORS
        GEN_OPTIONS
            -M lodepng
    )

    # ESPIDF bindings

    set(LV_ESPIDF_DEP ${IDF_PATH}/components ${LV_BINDINGS_DIR}/driver/esp32)
    lv_bindings(
        OUTPUT
            ${LV_ESPIDF}
        INPUT
            ${LV_BINDINGS_DIR}/driver/esp32/espidf.h
        DEPENDS
            "${LV_ESPIDF_DEP}"
        PP_OPTIONS
            -DPYCPARSER
        GEN_OPTIONS
             -M espidf
    )

endfunction()

# Add includes to CMake component

set(LV_INCLUDE
    ${LV_BINDINGS_DIR}
    ${LV_PNG_DIR}
)

# Add sources to CMake component

set(LV_SRC
    ${LV_MP}

    ${LV_BINDINGS_DIR}/driver/esp32/espidf.c
    ${LV_BINDINGS_DIR}/driver/esp32/modlvesp32.c
    ${LV_BINDINGS_DIR}/driver/esp32/modrtch.c
    ${LV_BINDINGS_DIR}/driver/esp32/sh2lib.c

    ${LV_PNG}
    ${LV_PNG_C}
    ${LV_BINDINGS_DIR}/driver/png/mp_lodepng.c

    # ${LV_ESPIDF}
)


