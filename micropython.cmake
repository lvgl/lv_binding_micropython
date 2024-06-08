
# This file is to be given as "make USER_C_MODULES=..." when building Micropython port

# Include LVGL component, ignore KCONFIG

idf_build_set_property(LV_MICROPYTHON 1)
idf_build_component(${CMAKE_CURRENT_LIST_DIR}/lvgl)
idf_build_set_property(COMPILE_DEFINITIONS "-DLV_KCONFIG_IGNORE" APPEND)
separate_arguments(LV_CFLAGS_ENV UNIX_COMMAND $ENV{LV_CFLAGS})
idf_build_set_property(COMPILE_DEFINITIONS "${LV_CFLAGS}" APPEND)
idf_build_set_property(COMPILE_OPTIONS "-Wno-unused-function" APPEND)
idf_build_set_property(SRCS "${LV_SRC}" APPEND)
idf_build_set_property(INCLUDE_DIRS "${LV_INCLUDE}" APPEND)

include(${CMAKE_CURRENT_LIST_DIR}/mkrules_usermod.cmake)

# Add lv_bindings rules

all_lv_bindings()


# # # make usermod (target declared by Micropython for all user compiled modules) link to bindings
# # # this way the bindings (and transitively lvgl_interface) get proper compilation flags
# target_link_libraries(usermod INTERFACE usermod_lvgl)

file(GLOB_RECURSE SOURCES ${CMAKE_CURRENT_LIST_DIR}/lvgl/src/*.c)

add_library(lvgl_interface INTERFACE)

target_sources(lvgl_interface INTERFACE ${SOURCES})
target_compile_options(lvgl_interface INTERFACE ${LV_CFLAGS})

# # lvgl bindings target (the mpy module)

add_library(usermod_lvgl INTERFACE)
target_sources(usermod_lvgl INTERFACE ${LV_SRC})
target_include_directories(usermod_lvgl INTERFACE ${LV_INCLUDE})


file(WRITE ${LV_MP} "")

target_link_libraries(usermod_lvgl INTERFACE lvgl_interface)

# # # make usermod (target declared by Micropython for all user compiled modules) link to bindings
# # # this way the bindings (and transitively lvgl_interface) get proper compilation flags
target_link_libraries(usermod INTERFACE usermod_lvgl)

