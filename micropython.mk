
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
LVGL_JSON = $(BUILD)/lvgl/lvgl_api.json
CFLAGS_USERMOD += $(LV_CFLAGS)

# MAKE SURE LV_CONF_PATH is a STRING
CFLAGS_USERMOD += -DLV_CONF_PATH='"$(LV_CONF_PATH)"'
# CFLAGS_USERMOD += -DLV_CONF_PATH=$(LV_CONF_PATH)


# CFLAGS DEBUG
$(info CFLAGS_USERMOD is $(CFLAGS_USERMOD))

# Generate LVGL API JSON for enhanced binding generation
$(LVGL_JSON): $(ALL_LVGL_SRC)
	$(ECHO) "LVGL-JSON $@"
	$(Q)mkdir -p $(dir $@)
	$(Q)if [ -f "$(LVGL_DIR)/scripts/gen_json/gen_json.py" ]; then \
		$(PYTHON) $(LVGL_DIR)/scripts/gen_json/gen_json.py \
			--output-path $@ \
			--lvgl-config $(LV_CONF_PATH); \
	else \
		echo '{}' > $@; \
		echo "Warning: LVGL JSON generator not found, using empty JSON"; \
	fi

$(LVGL_MPY): $(ALL_LVGL_SRC) $(LVGL_BINDING_DIR)/gen/gen_mpy.py $(LVGL_JSON)
	$(ECHO) "LVGL-GEN $@"
	$(Q)mkdir -p $(dir $@)
	$(Q)$(CPP) $(CFLAGS_USERMOD) -DPYCPARSER -x c -I $(LVGL_BINDING_DIR)/pycparser/utils/fake_libc_include $(INC) $(LVGL_DIR)/lvgl.h > $(LVGL_PP)
	$(Q)$(PYTHON) $(LVGL_BINDING_DIR)/gen/gen_mpy.py -M lvgl -MP lv -MD $(LVGL_MPY_METADATA) -J $(LVGL_JSON) -E $(LVGL_PP) $(LVGL_DIR)/lvgl.h > $@

# Python stub file generation and packaging
LVGL_STUBS_TEMPLATE_DIR = $(LVGL_BINDING_DIR)/stubs
LVGL_STUBS_BUILD_DIR = $(BUILD)/lvgl/stubs-package
LVGL_STUBS_DIR = $(LVGL_STUBS_BUILD_DIR)/lvgl_stubs
LVGL_STUBS_FILE = $(LVGL_STUBS_DIR)/lvgl.pyi
LVGL_STUBS_WHEEL = $(LVGL_STUBS_BUILD_DIR)/dist/lvgl_stubs-*.whl

# Copy stubs template and generate stub file
$(LVGL_STUBS_FILE): $(LVGL_MPY_METADATA) $(LVGL_BINDING_DIR)/gen/gen_stubs.py $(LVGL_STUBS_TEMPLATE_DIR)
	$(ECHO) "LVGL-STUBS $@"
	$(Q)mkdir -p $(LVGL_STUBS_BUILD_DIR)
	$(Q)cp -r $(LVGL_STUBS_TEMPLATE_DIR)/* $(LVGL_STUBS_BUILD_DIR)/
	$(Q)# Extract LVGL version and create __version__.py
	$(Q)LVGL_MAJOR=$$(grep "LVGL_VERSION_MAJOR" $(LVGL_DIR)/lv_version.h | grep -o '[0-9]\+'); \
	LVGL_MINOR=$$(grep "LVGL_VERSION_MINOR" $(LVGL_DIR)/lv_version.h | grep -o '[0-9]\+'); \
	LVGL_PATCH=$$(grep "LVGL_VERSION_PATCH" $(LVGL_DIR)/lv_version.h | grep -o '[0-9]\+'); \
	LVGL_VERSION="$${LVGL_MAJOR}.$${LVGL_MINOR}.$${LVGL_PATCH}"; \
	echo "Setting LVGL stubs version to: $${LVGL_VERSION}"; \
	echo "__version__ = \"$${LVGL_VERSION}\"" > $(LVGL_STUBS_DIR)/__version__.py
	$(Q)$(PYTHON) $(LVGL_BINDING_DIR)/gen/gen_stubs.py \
		--metadata $(LVGL_MPY_METADATA) \
		--stubs-dir $(LVGL_STUBS_DIR) \
		--lvgl-dir $(LVGL_DIR) \
		--module-name lvgl \
		--validate

# Build the wheel package
$(LVGL_STUBS_WHEEL): $(LVGL_STUBS_FILE)
	$(ECHO) "LVGL-WHEEL $@"
	$(Q)cd $(LVGL_STUBS_BUILD_DIR) && $(PYTHON) -m build --wheel
	$(Q)touch $@

.PHONY: LVGL_MPY LVGL_STUBS LVGL_STUBS_WHEEL
LVGL_MPY: $(LVGL_MPY)

# Generate Python stub files with documentation (slow - parses 200+ header files)
LVGL_STUBS: $(LVGL_STUBS_FILE)
	@echo "Generated LVGL Python stub files in $(LVGL_STUBS_DIR)/"

# Generate Python stub files and build distributable wheel package
LVGL_STUBS_WHEEL: $(LVGL_STUBS_WHEEL)
	@echo "Built LVGL Python stubs wheel package in $(LVGL_STUBS_BUILD_DIR)/dist/"

CFLAGS_USERMOD += -Wno-unused-function
CFLAGS_EXTRA += -Wno-unused-function
SRC_USERMOD_LIB_C += $(subst $(TOP)/,,$(shell find $(LVGL_DIR)/src $(LVGL_DIR)/examples $(LVGL_GENERIC_DRV_DIR) -type f -name "*.c"))
SRC_USERMOD_C += $(LVGL_MPY)
