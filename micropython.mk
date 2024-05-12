
################################################################################
# LVGL unix optional libraries
# Update CFLAGS_EXTMOD and LDFLAGS_EXTMOD for LVGL extenral library,
# but do that only on the unix port, for unix specific dependencies
ifeq ($(notdir $(CURDIR)),unix)
ifneq ($(UNAME_S),Darwin)
CFLAGS_EXTMOD += -DMICROPY_FB=1
endif

SDL_CFLAGS_EXTMOD :=  $(shell pkg-config --silence-errors --cflags sdl2)
SDL_LDFLAGS_EXTMOD := $(shell pkg-config --silence-errors --libs   sdl2)
ifneq ($(SDL_LDFLAGS_EXTMOD),)
CFLAGS_EXTMOD += $(SDL_CFLAGS_EXTMOD) -DMICROPY_SDL=1
LDFLAGS_EXTMOD += $(SDL_LDFLAGS_EXTMOD)
endif

RLOTTIE_CFLAGS_EXTMOD :=  $(shell pkg-config --silence-errors --cflags rlottie)
RLOTTIE_LDFLAGS_EXTMOD := $(shell pkg-config --silence-errors --libs   rlottie)
ifneq ($(RLOTTIE_LDFLAGS_EXTMOD),)
CFLAGS_EXTMOD += $(RLOTTIE_CFLAGS_EXTMOD) -DMICROPY_RLOTTIE=1
LDFLAGS_EXTMOD += $(RLOTTIE_LDFLAGS_EXTMOD)
endif

FREETYPE_CFLAGS_EXTMOD :=  $(shell pkg-config --silence-errors --cflags freetype2)
FREETYPE_LDFLAGS_EXTMOD := $(shell pkg-config --silence-errors --libs   freetype2)
ifneq ($(FREETYPE_LDFLAGS_EXTMOD),)
CFLAGS_EXTMOD += $(FREETYPE_CFLAGS_EXTMOD) -DMICROPY_FREETYPE=1
LDFLAGS_EXTMOD += $(FREETYPE_LDFLAGS_EXTMOD)
endif

FFMPEG_LIBS := libavformat libavcodec libswscale libavutil
FFMPEG_CFLAGS_EXTMOD :=  $(shell pkg-config --silence-errors --cflags $(FFMPEG_LIBS))
FFMPEG_LDFLAGS_EXTMOD := $(shell pkg-config --silence-errors --libs   $(FFMPEG_LIBS))
ifneq ($(FFMPEG_LDFLAGS_EXTMOD),)
CFLAGS_EXTMOD += $(FFMPEG_CFLAGS_EXTMOD) -DMICROPY_FFMPEG=1
LDFLAGS_EXTMOD += $(FFMPEG_LDFLAGS_EXTMOD)
endif
endif

################################################################################

# LVGL build rules


LVGL_BINDING_DIR := $(USERMOD_DIR)

LVGL_DIR = $(LVGL_BINDING_DIR)/lvgl
LVGL_GENERIC_DRV_DIR = $(LVGL_BINDING_DIR)/driver/generic
INC += -I$(LVGL_BINDING_DIR)
ALL_LVGL_SRC = $(shell find $(LVGL_DIR) -type f -name '*.h') $(LVGL_BINDING_DIR)/lv_conf.h
LVGL_PP = $(BUILD)/lvgl/lvgl.pp.c
LVGL_MPY = $(BUILD)/lvgl/lv_mpy.c
LVGL_MPY_METADATA = $(BUILD)/lvgl/lv_mpy.json
CFLAGS_EXTMOD += $(LV_CFLAGS) 

$(LVGL_MPY): $(ALL_LVGL_SRC) $(LVGL_BINDING_DIR)/gen/gen_mpy.py 
	$(ECHO) "LVGL-GEN $@"
	$(Q)mkdir -p $(dir $@)
	$(Q)$(CPP) $(CFLAGS_EXTMOD) -DPYCPARSER -x c -I $(LVGL_BINDING_DIR)/pycparser/utils/fake_libc_include $(INC) $(LVGL_DIR)/lvgl.h > $(LVGL_PP)
	$(Q)$(PYTHON) $(LVGL_BINDING_DIR)/gen/gen_mpy.py -M lvgl -MP lv -MD $(LVGL_MPY_METADATA) -E $(LVGL_PP) $(LVGL_DIR)/lvgl.h > $@

.PHONY: LVGL_MPY
LVGL_MPY: $(LVGL_MPY)

CFLAGS_EXTMOD += -Wno-unused-function
CFLAGS_EXTRA += -Wno-unused-function
SRC_THIRDPARTY_C += $(subst $(TOP)/,,$(shell find $(LVGL_DIR)/src $(LVGL_DIR)/examples $(LVGL_GENERIC_DRV_DIR) -type f -name "*.c"))
SRC_EXTMOD_C += $(LVGL_MPY)
