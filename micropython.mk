# For detauils see: https://docs.micropython.org/en/latest/develop/cmodules.html

LVGL_BINDING_DIR := $(USERMOD_DIR)

LVGL_DIR = $(LVGL_BINDING_DIR)/lvgl
LVGL_GENERIC_DRV_DIR = $(LVGL_BINDING_DIR)/driver/generic
INC += -I$(LVGL_BINDING_DIR) -I$(LVGL_BINDING_DIR)/include

ALL_LVGL_SRC = $(shell find $(LVGL_DIR) -type f -name '*.h') $(LVGL_BINDING_DIR)/lv_conf.h
LVGL_PP = $(BUILD)/lvgl/lvgl.pp.c
LVGL_MPY = $(BUILD)/lvgl/lv_mpy.c
LVGL_MPY_METADATA = $(BUILD)/lvgl/lv_mpy.json
QSTR_GLOBAL_DEPENDENCIES += $(LVGL_MPY)
CFLAGS_USERMOD += $(LV_CFLAGS) $(INC)


ifneq ($(MICROPY_FLOAT_IMPL),double)
# Tiny TTF library needs a number of math.h double functions
CFLAGS_USERMOD += -DLV_USE_TINY_TTF=0
endif

# Generate the main micropython bindings library
$(LVGL_MPY): $(ALL_LVGL_SRC) $(LVGL_BINDING_DIR)/gen/gen_mpy.py
	$(ECHO) "LVGL-GEN $@"
	$(Q)mkdir -p $(dir $@)
	$(Q)$(CPP) $(CFLAGS_USERMOD) $(CFLAGS_EXTRA) -DPYCPARSER -x c -I $(LVGL_BINDING_DIR)/pycparser/utils/fake_libc_include $(INC) $(LVGL_DIR)/lvgl.h > $(LVGL_PP)
	$(Q)$(PYTHON) $(LVGL_BINDING_DIR)/gen/gen_mpy.py -M lvgl -MP lv -MD $(LVGL_MPY_METADATA) -E $(LVGL_PP) $(LVGL_DIR)/lvgl.h > $@

# Add all lvgl source files to the module.
SRC_USERMOD += $(shell find $(LVGL_DIR)/src $(LVGL_DIR)/examples $(LVGL_GENERIC_DRV_DIR) -type f -name "*.c") $(LVGL_MPY)
CFLAGS_USERMOD += -Wno-unused-function

ifeq ($(notdir $(CURDIR)),unix)

UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
SRC_USERMOD += $(shell find $(LVGL_BINDING_DIR)/driver/SDL -type f -name "*.c")
LDFLAGS_USERMOD += -lSDL2
endif

ifneq ($(UNAME_S),Darwin)
SRC_USERMOD += $(LVGL_BINDING_DIR)/driver/linux/modfb.c
endif

# Additional optional libraries

RLOTTIE_CFLAGS_MOD :=  $(shell pkg-config --silence-errors --cflags rlottie)
RLOTTIE_LDFLAGS_MOD := $(shell pkg-config --silence-errors --libs   rlottie)
ifneq ($(RLOTTIE_LDFLAGS_MOD),)
CFLAGS_MOD += $(RLOTTIE_CFLAGS_MOD) -DMICROPY_RLOTTIE=1
LDFLAGS_MOD += $(RLOTTIE_LDFLAGS_MOD)
endif

FREETYPE_CFLAGS_MOD :=  $(shell pkg-config --silence-errors --cflags freetype2)
FREETYPE_LDFLAGS_MOD := $(shell pkg-config --silence-errors --libs   freetype2)
ifneq ($(FREETYPE_LDFLAGS_MOD),)
CFLAGS_MOD += $(FREETYPE_CFLAGS_MOD) -DMICROPY_FREETYPE=1
LDFLAGS_MOD += $(FREETYPE_LDFLAGS_MOD)
endif

FFMPEG_LIBS := libavformat libavcodec libswscale libavutil
FFMPEG_CFLAGS_MOD :=  $(shell pkg-config --silence-errors --cflags $(FFMPEG_LIBS))
FFMPEG_LDFLAGS_MOD := $(shell pkg-config --silence-errors --libs   $(FFMPEG_LIBS))
ifneq ($(FFMPEG_LDFLAGS_MOD),)
CFLAGS_MOD += $(FFMPEG_CFLAGS_MOD) -DMICROPY_FFMPEG=1
LDFLAGS_MOD += $(FFMPEG_LDFLAGS_MOD)
endif

endif  # unix port


