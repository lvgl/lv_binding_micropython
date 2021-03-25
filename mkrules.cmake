
find_package(Python3 REQUIRED COMPONENTS Interpreter)

set(LV_BINDINGS_DIR ${MICROPY_DIR}/lib/lv_bindings)

# Common function for creating LV bindings

function(lv_bindings LV_OUTPUT LV_INPUT LV_DEP LV_PP_OPTIONS LV_GEN_OPTIONS)
    # LV_PP_OPTIONS and LV_GEN_OPTIONS must be quoted when calling lv_bindings since they are lists.

    set(LV_PP ${LV_OUTPUT}.pp)
    set(LV_MPY_METADATA ${LV_OUTPUT}.json)

    add_custom_command(
        OUTPUT 
            ${LV_PP}
        COMMAND
        ${CMAKE_C_COMPILER} -E ${LV_PP_OPTIONS} ${LV_CFLAGS} -I ${LV_BINDINGS_DIR}/pycparser/utils/fake_libc_include ${MICROPY_CPP_FLAGS} ${LV_INPUT} > ${LV_PP}
        DEPENDS
            ${LV_INPUT}
            ${LV_DEP}
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

    set(LV_MP_PP_OPTIONS)
    set(LV_MP_GEN_OPTIONS -M lvgl -MP lv)
    lv_bindings(${LV_MP} ${LVGL_DIR}/lvgl.h ${LVGL_DIR} "${LV_MP_PP_OPTIONS}" "${LV_MP_GEN_OPTIONS}")

    # LODEPNG bindings

    set(LV_PNG_PP_OPTIONS -DLODEPNG_NO_COMPILE_ENCODER -DLODEPNG_NO_COMPILE_DISK -DLODEPNG_NO_COMPILE_ALLOCATORS)
    set(LV_PNG_GEN_OPTIONS -M lodepng)
    configure_file(${LV_PNG_DIR}/lodepng.cpp ${LV_PNG_C} COPYONLY)
    idf_build_set_property(COMPILE_DEFINITIONS "${LV_PNG_PP_OPTIONS}" APPEND)
    lv_bindings(${LV_PNG} ${LV_PNG_DIR}/lodepng.h ${LV_PNG_DIR} "${LV_PNG_PP_OPTIONS}" "${LV_PNG_GEN_OPTIONS}")

    # ESPIDF bindings

    set(LV_ESPIDF_PP_OPTIONS -DPYCPARSER)
    set(LV_ESPIDF_GEN_OPTIONS -M espidf)
    set(LV_ESPIDF_DEP ${IDF_PATH}/components ${LV_BINDINGS_DIR}/driver/esp32)
    lv_bindings(${LV_ESPIDF} ${LV_BINDINGS_DIR}/driver/esp32/espidf.h "${LV_ESPIDF_DEP}" "${LV_ESPIDF_PP_OPTIONS}" "${LV_ESPIDF_GEN_OPTIONS}")

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

    #    ${LV_ESPIDF}
)


