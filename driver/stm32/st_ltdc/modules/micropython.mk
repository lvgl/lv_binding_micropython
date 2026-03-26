################################################################################

ST_LTDC_MOD_DIR := $(USERMOD_DIR)
MOD_ROOT_DIR := ${TOP_DIR}/user_modules/lv_binding_micropython
CFLAGS_USERMOD += -I$(MOD_ROOT_DIR)/lvgl/src -I$(MOD_ROOT_DIR)/lvgl/src/display -I$(MOD_ROOT_DIR)/lvgl/src/core -I$(MOD_ROOT_DIR)/driver/include
CFLAGS_USERMOD += -I$(ST_LTDC_MOD_DIR)
SRC_ST_LTDC_C := $(shell find $(ST_LTDC_MOD_DIR) -type f -name "*.c")
SRC_USERMOD_C += $(SRC_ST_LTDC_C)

BSP_LTDC_MOD_DIR := $(USERMOD_DIR)/../../$(BOARD)
SRC_BSP_LTDC_C := $(shell find $(BSP_LTDC_MOD_DIR) -type f -name "*.c")
SRC_USERMOD_C += $(SRC_BSP_LTDC_C)
$(shell printf 'BOARD = "%s"\nVERSION = "%s"\n' "$(BOARD)" "$(BOARD_VARIANT)" > $(USERMOD_DIR)/../board_config.py)
$(info user_modules=st_ltdc, $(BOARD) $(BOARD_VARIANT))