
################################################################################
# LVGL unix optional libraries
# Update CFLAGS_USERMOD and LDFLAGS_USERMOD for LVGL extenral library,
# but do that only on the unix port, for unix specific dependencies
ifeq ($(notdir $(CURDIR)),unix)
ifneq ($(UNAME_S),Darwin)
CFLAGS_USERMOD += -DMICROPY_FB=1
endif

SDL_CFLAGS_USERMOD :=  $(shell pkg-config --silence-errors --cflags sdl2)
SDL_LDFLAGS_USERMOD := $(shell pkg-config --silence-errors --libs   sdl2)
ifneq ($(SDL_LDFLAGS_USERMOD),)
CFLAGS_USERMOD += $(SDL_CFLAGS_USERMOD) -DMICROPY_SDL=1
LDFLAGS_USERMOD += $(SDL_LDFLAGS_USERMOD)
endif

# Avoid including unwanted local headers other than sdl2 
ifeq ($(UNAME_S),Darwin)
CFLAGS_USERMOD:=$(filter-out -I/usr/local/include,$(CFLAGS_USERMOD))
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

# Enable FFMPEG
# FFMPEG_LIBS := libavformat libavcodec libswscale libavutil
# FFMPEG_CFLAGS_USERMOD :=  $(shell pkg-config --silence-errors --cflags $(FFMPEG_LIBS))
# FFMPEG_LDFLAGS_USERMOD := $(shell pkg-config --silence-errors --libs   $(FFMPEG_LIBS))
# ifneq ($(FFMPEG_LDFLAGS_USERMOD),)
# CFLAGS_USERMOD += $(FFMPEG_CFLAGS_USERMOD) -DMICROPY_FFMPEG=1
# LDFLAGS_USERMOD += $(FFMPEG_LDFLAGS_USERMOD)
# endif

endif

################################################################################

# LVGL build rules


LVGL_BINDING_DIR := $(USERMOD_DIR)
ifeq ($(LV_CONF_PATH),)
LV_CONF_PATH = $(LVGL_BINDING_DIR)/lv_conf.h
endif

# LV_CONF_PATH DEBUG
$(info    LV_CONF_PATH is $(LV_CONF_PATH))


LVGL_DIR = $(LVGL_BINDING_DIR)/lvgl
LVGL_GENERIC_DRV_DIR = $(LVGL_BINDING_DIR)/driver/generic
INC += -I$(LVGL_BINDING_DIR)
ALL_LVGL_SRC = $(shell find $(LVGL_DIR) -type f -name '*.h') $(LV_CONF_PATH)
LVGL_PP = $(BUILD)/lvgl/lvgl.pp.c
LVGL_MPY = $(BUILD)/lvgl/lv_mpy.c
LVGL_MPY_METADATA = $(BUILD)/lvgl/lv_mpy.json
CFLAGS_USERMOD += $(LV_CFLAGS)

# MAKE SURE LV_CONF_PATH is a STRING
CFLAGS_USERMOD += -DLV_CONF_PATH='"$(LV_CONF_PATH)"'
# CFLAGS_USERMOD += -DLV_CONF_PATH=$(LV_CONF_PATH)


# CFLAGS DEBUG
$(info CFLAGS_USERMOD is $(CFLAGS_USERMOD))

$(LVGL_MPY): $(ALL_LVGL_SRC) $(LVGL_BINDING_DIR)/gen/gen_mpy.py 
	$(ECHO) "LVGL-GEN $@"
	$(Q)mkdir -p $(dir $@)
	$(Q)$(CPP) $(CFLAGS_USERMOD) -DPYCPARSER -x c -I $(LVGL_BINDING_DIR)/pycparser/utils/fake_libc_include $(INC) $(LVGL_DIR)/lvgl.h > $(LVGL_PP)
	$(Q)$(PYTHON) $(LVGL_BINDING_DIR)/gen/gen_mpy.py -M lvgl -MP lv -MD $(LVGL_MPY_METADATA) -E $(LVGL_PP) $(LVGL_DIR)/lvgl.h > $@

.PHONY: LVGL_MPY
LVGL_MPY: $(LVGL_MPY)

CFLAGS_USERMOD += -Wno-unused-function
CFLAGS_EXTRA += -Wno-unused-function
SRC_USERMOD_LIB_C += $(subst $(TOP)/,,$(shell find $(LVGL_DIR)/src $(LVGL_DIR)/examples $(LVGL_GENERIC_DRV_DIR) -type f -name "*.c"))
SRC_USERMOD_C += $(LVGL_MPY)
