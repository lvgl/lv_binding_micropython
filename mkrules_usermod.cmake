

find_package(Python3 REQUIRED COMPONENTS Interpreter)
find_program(AWK awk mawk gawk)

set(LV_BINDINGS_DIR ${CMAKE_CURRENT_LIST_DIR})

# first check
if(NOT DEFINED LV_CONF_PATH)
    set(LV_CONF_PATH ${LV_BINDINGS_DIR}/lv_conf.h)

    message(STATUS "LV_CONF_PATH=${LV_CONF_PATH}")
endif()

# Common function for creating LV bindings

function(lv_bindings)
    set(_options)
    set(_one_value_args OUTPUT)
    set(_multi_value_args INPUT DEPENDS COMPILE_OPTIONS PP_OPTIONS GEN_OPTIONS FILTER)
    cmake_parse_arguments(
        PARSE_ARGV 0 LV
        "${_options}"
        "${_one_value_args}"
        "${_multi_value_args}"
    )

    set(LV_PP ${LV_OUTPUT}.pp)
    set(LV_MPY_METADATA ${LV_OUTPUT}.json)

    # message(STATUS "LV_CONF_PATH=${LV_CONF_PATH}")
    # message(STATUS "LV_COMPILE_OPTIONS=${LV_COMPILE_OPTIONS}")

    # message(STATUS "LV_PP_OPTIONS=${LV_PP_OPTIONS}")
    # message(STATUS "LV_CFLAGS=${LV_CFLAGS}")

    add_custom_command(
        OUTPUT 
            ${LV_PP}
        COMMAND
        ${CMAKE_C_COMPILER} -E -DPYCPARSER -DLV_CONF_PATH="${LV_CONF_PATH}" ${LV_COMPILE_OPTIONS} ${LV_PP_OPTIONS} "${LV_CFLAGS}" -I ${LV_BINDINGS_DIR}/pycparser/utils/fake_libc_include ${MICROPY_CPP_FLAGS} ${LV_INPUT} > ${LV_PP}
        DEPENDS
            ${LV_INPUT}
            ${LV_DEPENDS}
            ${LV_BINDINGS_DIR}/pycparser/utils/fake_libc_include
        IMPLICIT_DEPENDS
            C ${LV_INPUT}
        COMMENT
            "LV_BINDINGS CPP"
        VERBATIM
        COMMAND_EXPAND_LISTS
    )

    # if(ESP_PLATFORM)
    #     target_compile_options(${COMPONENT_LIB} PRIVATE ${LV_COMPILE_OPTIONS})
    # else()
    # target_compile_options(usermod_lv_bindings INTERFACE ${LV_COMPILE_OPTIONS})
    # endif()

    if (DEFINED LV_FILTER)

        set(LV_PP_FILTERED ${LV_PP}.filtered)
        set(LV_AWK_CONDITION)
        foreach(_f ${LV_FILTER})
            string(APPEND LV_AWK_CONDITION "\$3!~\"${_f}\" && ")
        endforeach()
        string(APPEND LV_AWK_COMMAND "\$1==\"#\"{p=(${LV_AWK_CONDITION} 1)} p{print}")

        # message("AWK COMMAND: ${LV_AWK_COMMAND}")

        add_custom_command(
            OUTPUT
                ${LV_PP_FILTERED}
            COMMAND
                ${AWK} ${LV_AWK_COMMAND} ${LV_PP} > ${LV_PP_FILTERED}
            DEPENDS
                ${LV_PP}

            COMMENT
                "LV_BINDINGS: FILTER"
            VERBATIM
            COMMAND_EXPAND_LISTS
        )
    else()
        set(LV_PP_FILTERED ${LV_PP})
    endif()

    add_custom_command(
        OUTPUT
            ${LV_OUTPUT}
        COMMAND
            ${Python3_EXECUTABLE} ${LV_BINDINGS_DIR}/gen/gen_mpy.py ${LV_GEN_OPTIONS} -DLV_CONF_PATH="${LV_CONF_PATH}" -MD ${LV_MPY_METADATA} -E ${LV_PP_FILTERED} ${LV_INPUT} > ${LV_OUTPUT} || (rm -f ${LV_OUTPUT} && /bin/false)
        DEPENDS
            ${LV_BINDINGS_DIR}/gen/gen_mpy.py
            ${LV_PP_FILTERED}

        COMMENT
            "LV_BINDINGS GEN MPY"
        COMMAND_EXPAND_LISTS
    )

endfunction()

# Definitions for specific bindings

set(LVGL_DIR ${LV_BINDINGS_DIR}/lvgl)

set(LV_MP ${CMAKE_BINARY_DIR}/lv_mp.c)
# if(ESP_PLATFORM)
#     set(LV_ESPIDF ${CMAKE_BINARY_DIR}/lv_espidf.c)
# endif()

# Function for creating all specific bindings

function(all_lv_bindings)

    # LVGL bindings

    file(GLOB_RECURSE LVGL_HEADERS ${LVGL_DIR}/src/*.h ${LV_CONF_PATH})
    lv_bindings(
        OUTPUT
            ${LV_MP}
        INPUT
            ${LVGL_DIR}/lvgl.h
        DEPENDS
            ${LVGL_HEADERS}
        GEN_OPTIONS
            -M lvgl -MP lv
    )

        
    # ESPIDF bindings

    # if(ESP_PLATFORM)
    #     file(GLOB_RECURSE LV_ESPIDF_HEADERS ${IDF_PATH}/components/*.h ${LV_BINDINGS_DIR}/driver/esp32/*.h)
    #     lv_bindings(
    #         OUTPUT
    #             ${LV_ESPIDF}
    #         INPUT
    #             ${LV_BINDINGS_DIR}/driver/esp32/espidf.h
    #         DEPENDS
    #             ${LV_ESPIDF_HEADERS}
    #         GEN_OPTIONS
    #              -M espidf
    #         FILTER
    #             i2s_ll.h
    #             i2s_hal.h
    #             esp_intr_alloc.h
    #             soc/spi_periph.h
    #             rom/ets_sys.h
    #             soc/sens_struct.h
    #             soc/rtc.h
    #             driver/periph_ctrl.h
    #     )
    # endif(ESP_PLATFORM)

endfunction()

# Add includes to CMake component

set(LV_INCLUDE
    ${LV_BINDINGS_DIR}
)

# Add sources to CMake component

set(LV_SRC
    ${LV_MP}
)

# if(ESP_PLATFORM)
#     LIST(APPEND LV_SRC
#         ${LV_BINDINGS_DIR}/driver/esp32/espidf.c
#         ${LV_BINDINGS_DIR}/driver/esp32/modrtch.c
#         ${LV_BINDINGS_DIR}/driver/esp32/sh2lib.c
#         ${LV_ESPIDF}
#     )
# endif(ESP_PLATFORM)

