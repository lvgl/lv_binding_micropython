################################################################################
# LVGL build rules for ports based on Makefile

# For details see: https://docs.micropython.org/en/latest/develop/cmodules.html

LVGL_BINDING_DIR := $(USERMOD_DIR)

LVGL_DIR = $(LVGL_BINDING_DIR)/lvgl
LVGL_GENERIC_DRV_DIR = $(LVGL_BINDING_DIR)/driver/generic

ifeq ($(LV_CONF_PATH),)
LV_CONF_PATH = $(LVGL_BINDING_DIR)/lv_conf.h
endif
$(info    LV_CONF_PATH is $(LV_CONF_PATH))
CFLAGS_USERMOD += -DLV_CONF_PATH="<$(abspath $(LV_CONF_PATH))>"

ifeq ($(wildcard $(LVGL_DIR)/.),,)
$(info lvgl submodule not init)
else
# This listing of all lvgl src files is used by make to track when the bindings need to be regenerated
ALL_LVGL_SRC = $(shell find $(LVGL_DIR) -type f -name '*.h') $(LV_CONF_PATH)
endif

LVGL_PP = $(BUILD)/lvgl/lvgl.pp.c
LVGL_MPY = $(BUILD)/lvgl/lv_mpy.c
LVGL_MPY_METADATA = $(BUILD)/lvgl/lv_mpy.json
QSTR_GLOBAL_DEPENDENCIES += $(LVGL_MPY)
INC += -I$(LVGL_BINDING_DIR) -I$(LVGL_BINDING_DIR)/include -I$(LVGL_DIR)/src
CFLAGS_USERMOD += $(INC) $(LV_CFLAGS)

ifneq ($(MICROPY_FLOAT_IMPL),double)
# Tiny TTF library needs a number of math.h double functions
CFLAGS_USERMOD += -DLV_USE_TINY_TTF=0
endif

# chain lvgl submodule check off the micropython submodules rule.
LVGL_SUBMODULES = lvgl pycparser
submodules: lvgl_submodule
lvgl_submodule:
	$(ECHO) "Updating submodules: $(LVGL_SUBMODULES)"
	$(Q)cd $(LVGL_BINDING_DIR) && git submodule sync $(LVGL_SUBMODULES)
	$(Q)cd $(LVGL_BINDING_DIR) && git submodule update --init $(LVGL_SUBMODULES)
.PHONY: lvgl_submodule

# Generate the main micropython bindings library
$(LVGL_MPY): $(ALL_LVGL_SRC) $(LVGL_BINDING_DIR)/gen/gen_mpy.py
	$(ECHO) "LVGL-GEN $@"
	$(Q)mkdir -p $(dir $@)
	$(Q)$(CPP) $(CFLAGS_USERMOD) -DPYCPARSER -x c -I $(LVGL_BINDING_DIR)/pycparser/utils/fake_libc_include $(INC) $(LVGL_DIR)/lvgl.h > $(LVGL_PP)
	$(Q)$(PYTHON) $(LVGL_BINDING_DIR)/gen/gen_mpy.py -M lvgl -MP lv -MD $(LVGL_MPY_METADATA) -E $(LVGL_PP) $(LVGL_DIR)/lvgl.h > $@

# Add all lvgl source files to the module.
SRC_USERMOD += $(shell find $(LVGL_DIR)/src $(LVGL_DIR)/examples $(LVGL_GENERIC_DRV_DIR) -type f -name "*.c")
SRC_USERMOD += $(LVGL_MPY)

CFLAGS_USERMOD += -Wno-unused-function

FROZEN_MANIFEST += $(LVGL_BINDING_DIR)/manifest.py

################################################################################
# Per-port Support 

MICROPY_PORT = $(notdir $(CURDIR))
$(info MICROPY_PORT: $(MICROPY_PORT))

ifeq ($(MICROPY_PORT),mimxrt)
CFLAGS_USERMOD += -DLV_USE_PXP=1 -DLV_USE_DRAW_PXP=1 -DLV_USE_GPU_NXP_PXP=1 -DLV_USE_GPU_NXP_PXP_AUTO_INIT=1

$(BUILD)/$(MOD_DIRNAME)/lvgl/src/draw/nxp/pxp/lv_draw_pxp.o: CFLAGS_USERMOD += -Wno-error=unused-variable
$(BUILD)/$(MOD_DIRNAME)/lvgl/src/draw/nxp/pxp/lv_draw_pxp_img.o: CFLAGS_USERMOD += -Wno-error=float-conversion

endif

ifeq ($(MICROPY_PORT),unix)
# This section only included when building the micropython unix port
UNAME_S := $(shell uname -s)

ifneq ($(UNAME_S),Darwin)
# On macos enable framebuffer support
CFLAGS_USERMOD += -DMICROPY_FB=1
endif

ifneq (,$(shell which pkg-config))
# Linux Support: if pkg-config is installed use it to 
# check for and use optional libraries

SDL_CFLAGS_USERMOD :=  $(shell pkg-config --silence-errors --cflags sdl2)
SDL_LDFLAGS_USERMOD := $(shell pkg-config --silence-errors --libs   sdl2)
ifneq ($(SDL_LDFLAGS_USERMOD),)
CFLAGS_USERMOD += $(SDL_CFLAGS_USERMOD) -DMICROPY_SDL=1
LDFLAGS_USERMOD += $(SDL_LDFLAGS_USERMOD)
endif

RLOTTIE_CFLAGS_USERMOD :=  $(shell pkg-config --silence-errors --cflags rlottie)
RLOTTIE_LDFLAGS_USERMOD := $(shell pkg-config --silence-errors --libs   rlottie)
ifneq ($(RLOTTIE_LDFLAGS_USERMOD),)
CFLAGS_USERMOD += $(RLOTTIE_CFLAGS_USERMOD) -DMICROPY_RLOTTIE=1
LDFLAGS_USERMOD += $(RLOTTIE_LDFLAGS_USERMOD)
endif

FREETYPE_CFLAGS_USERMOD :=  $(shell pkg-config --silence-errors --cflags freetype2)
FREETYPE_LDFLAGS_USERMOD := $(shell pkg-config --silence-errors --libs   freetype2)
ifneq ($(FREETYPE_LDFLAGS_USERMOD),)
CFLAGS_USERMOD += $(FREETYPE_CFLAGS_USERMOD) -DMICROPY_FREETYPE=1
LDFLAGS_USERMOD += $(FREETYPE_LDFLAGS_USERMOD)
endif

FFMPEG_LIBS := libavformat libavcodec libswscale libavutil
FFMPEG_CFLAGS_USERMOD :=  $(shell pkg-config --silence-errors --cflags $(FFMPEG_LIBS))
FFMPEG_LDFLAGS_USERMOD := $(shell pkg-config --silence-errors --libs   $(FFMPEG_LIBS))
ifneq ($(FFMPEG_LDFLAGS_USERMOD),)
CFLAGS_USERMOD += $(FFMPEG_CFLAGS_USERMOD) -DMICROPY_FFMPEG=1
LDFLAGS_USERMOD += $(FFMPEG_LDFLAGS_USERMOD)
endif

endif  # Linux

endif  # unix port
