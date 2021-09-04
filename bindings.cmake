include(${CMAKE_CURRENT_LIST_DIR}/mkrules.cmake)

# create targets for generated files
all_lv_bindings()

# bindings target (the mpy module)
add_library(usermod_lv_bindings INTERFACE)
target_sources(usermod_lv_bindings INTERFACE ${LV_SRC})
target_include_directories(usermod_lv_bindings INTERFACE ${LV_INCLUDE})
if(0)
    # BUG?? this fails to make usermod link to lvgl_interface
    # even though INTERFACE libs should link transitively
    #
    # ${LVGL_DIR}/CMakeLists.txt should contain something like this (for non-ESP platforms, that is)
    # (not yet integrated upstream)
    if(0)
        file(GLOB_RECURSE SOURCES ${CMAKE_CURRENT_LIST_DIR}/src/*.c)
        file(GLOB_RECURSE EXAMPLE_SOURCES ${CMAKE_CURRENT_LIST_DIR}/examples/*.c)
        # this is consumed by micropython build; could also be guarded by if(MICROPY_DIR)
        add_library(lvgl_interface INTERFACE ${SOURCES})
        target_compile_options(lvgl_interface INTERFACE -Wno-unused-function)
        # this is for regular build
        add_library(lvgl STATIC ${SOURCES})
        add_library(lvgl_examples STATIC ${EXAMPLE_SOURCES})
    endif()
    # bindings depend on lvgl itself, pull it in
    include(${LVGL_DIR}/CMakeLists.txt)
    target_link_libraries(usermod_lv_bindings INTERFACE lvgl_interface)
else()
    # so for now just include the source directly, side-stepping lvgl/CMakeLists.txt
    file(GLOB_RECURSE LVGL_SRC ${CMAKE_CURRENT_LIST_DIR}/lvgl/src/*.c)
    target_sources(usermod_lv_bindings INTERFACE ${LVGL_SRC})
    target_compile_options(usermod_lv_bindings INTERFACE -Wno-unused-function)
endif()
# make usermod (target declared by Micropython for all user compiled modules) link to bindings
# this way the bindings (and transitively lvgl_interface) gets proper compilation flags etc
target_link_libraries(usermod INTERFACE usermod_lv_bindings)


