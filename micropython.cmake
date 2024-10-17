# For detauils see: https://docs.micropython.org/en/latest/develop/cmodules.html

set(LVGL_ROOT_DIR ${CMAKE_CURRENT_LIST_DIR})

include(${CMAKE_CURRENT_LIST_DIR}/env_support/cmake/micropython.cmake)

# Link our INTERFACE library to the usermod target.
target_link_libraries(usermod INTERFACE lvgl_interface)
