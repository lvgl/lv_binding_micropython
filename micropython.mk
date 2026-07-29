
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

WAYLAND_CFLAGS_USERMOD :=  $(shell pkg-config --silence-errors --cflags wayland-client wayland-cursor xkbcommon)
WAYLAND_LDFLAGS_USERMOD := $(shell pkg-config --silence-errors --libs   wayland-client wayland-cursor xkbcommon)
WAYLAND_SCANNER := $(shell pkg-config --silence-errors --variable=wayland_scanner wayland-scanner)
ifeq ($(WAYLAND_SCANNER),)
WAYLAND_SCANNER := $(shell command -v wayland-scanner)
endif
WAYLAND_PROTOCOLS_DIR := $(shell pkg-config --silence-errors --variable=pkgdatadir wayland-protocols)
ifneq ($(and $(WAYLAND_LDFLAGS_USERMOD),$(WAYLAND_SCANNER),$(WAYLAND_PROTOCOLS_DIR)),)
# lv_wl_xdg_shell.c needs generated xdg-shell client protocol glue that
# isn't shipped by wayland-protocols as source. Generate it eagerly (at
# Makefile-parse time, like the pkg-config detection above) into the
# build dir so it exists before any compilation starts -- a build *rule*
# for this would race lv_wl_xdg_shell.c's compile on a parallel first build,
# since nothing else orders one before the other.
LVGL_WAYLAND_PROTOCOLS_DIR := $(BUILD)/lvgl/wayland_protocols
LVGL_WAYLAND_XDG_SHELL_XML := $(WAYLAND_PROTOCOLS_DIR)/stable/xdg-shell/xdg-shell.xml
$(shell mkdir -p $(LVGL_WAYLAND_PROTOCOLS_DIR))
$(shell $(WAYLAND_SCANNER) client-header $(LVGL_WAYLAND_XDG_SHELL_XML) $(LVGL_WAYLAND_PROTOCOLS_DIR)/wayland_xdg_shell.h)
$(shell $(WAYLAND_SCANNER) private-code  $(LVGL_WAYLAND_XDG_SHELL_XML) $(LVGL_WAYLAND_PROTOCOLS_DIR)/wayland_xdg_shell.c)

CFLAGS_USERMOD += $(WAYLAND_CFLAGS_USERMOD) -DMICROPY_WAYLAND=1 -I$(LVGL_WAYLAND_PROTOCOLS_DIR) -I$(USERMOD_DIR)/lvgl
LDFLAGS_USERMOD += $(WAYLAND_LDFLAGS_USERMOD)
SRC_USERMOD_LIB_C += $(LVGL_WAYLAND_PROTOCOLS_DIR)/wayland_xdg_shell.c
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


LVGL_BINDING_DIR := $(abspath $(USERMOD_DIR))
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
CFLAGS_USERMOD += -DLV_CONF_PATH='"$(LV_CONF_PATH)"' -Wno-deprecated-declarations
# CFLAGS_USERMOD += -DLV_CONF_PATH=$(LV_CONF_PATH)


# CFLAGS DEBUG
$(info CFLAGS_USERMOD is $(CFLAGS_USERMOD))

$(LVGL_MPY): $(ALL_LVGL_SRC) $(LVGL_BINDING_DIR)/gen/gen_mpy.py $(LVGL_BINDING_DIR)/gen/lv_mpy_drivers.h
	$(ECHO) "LVGL-GEN $@"
	$(Q)mkdir -p $(dir $@)
	$(Q)$(CPP) -DPYCPARSER -x c \
		-I $(LVGL_BINDING_DIR)/stubs/include/freetype2 \
		-I $(LVGL_BINDING_DIR)/pycparser/utils/fake_libc_include \
		-I $(LVGL_BINDING_DIR)/stubs/include \
		-I $(LVGL_DIR) \
		$(CFLAGS_USERMOD) \
		$(LVGL_BINDING_DIR)/gen/lv_mpy_drivers.h > $(LVGL_PP)
	$(Q)$(PYTHON) $(LVGL_BINDING_DIR)/gen/gen_mpy.py -M lvgl -MP lv -MD $(LVGL_MPY_METADATA) -E $(LVGL_PP) $(LVGL_DIR)/lvgl.h $(LVGL_BINDING_DIR)/gen/lv_mpy_drivers.h > $@

.PHONY: LVGL_MPY
LVGL_MPY: $(LVGL_MPY)

CFLAGS_USERMOD += -Wno-unused-function
CFLAGS_EXTRA += -Wno-unused-function

# LVGL SRC
SRC_USERMOD_LIB_C += $(shell find $(LVGL_DIR)/src -type f -name "*.c")

# Binding-friendly wrappers for driver functions gen_mpy can't bind as-is
SRC_USERMOD_LIB_C += $(LVGL_BINDING_DIR)/gen/lv_mpy_drivers.c

# LVGL GENERIC DRIVER
SRC_USERMOD_LIB_C += $(shell find $(LVGL_GENERIC_DRV_DIR) -type f -name "*.c")

# LVGL EXAMPLES
ifeq ($(LV_BUILD_EXAMPLES), 1)
SRC_USERMOD_LIB_C += $(shell find $(LVGL_DIR)/examples -type f -name "*.c")
endif

SRC_USERMOD_C += $(LVGL_MPY)
