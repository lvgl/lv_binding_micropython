"""LVGL MicroPython bindings stub file.

This file provides type hints for LVGL MicroPython bindings to enable
IDE autocompletion and type checking. It is automatically generated
from the LVGL C headers.

Generated content:
- 0 widget classes
- 256 module functions
- 91 enum classes
- 27 integer constants
- 118 struct types
"""

from typing import Any, Callable, Optional, Union
from typing_extensions import Self

def lv_memzero(dst: None, len: int) -> None:
    ...

def lv_streq(s1: str, s2: str) -> bool:
    ...

def lv_sqr(x: int) -> int:
    """
    Calculate the square of an integer (input range is 0..32767).
    
    Args:
        x (int): input
    
    Returns:
        square
    
    
    C function: lv_sqr
    Source: src/misc/lv_math.h:118
    """
    ...

def lv_bidi_calculate_align(align: None, base_dir: None, txt: str) -> None:
    """
    For compatibility if LV_USE_BIDI = 0 Get the real text alignment from the a text
    alignment, base direction and a text.
    
    Args:
        align (None): For LV_TEXT_ALIGN_AUTO give LV_TEXT_ALIGN_LEFT else leave
                      unchanged, write back the calculated align here
        base_dir (None): Unused
        txt (str): Unused
    
    
    C function: lv_bidi_calculate_align
    Source: src/misc/lv_bidi.h:71
    """
    ...

def lv_style_get_prop_group(prop: int) -> int:
    """
    Tell the group of a property. If the a property from a group is set in a style the (1
    << group) bit of style->has_group is set. It allows early skipping the style if the
    property is not exists in the style at all.
    
    Args:
        prop (int): a style property
    
    Returns:
        the group [0..30] 30 means all the custom properties with index > 120
    
    
    C function: lv_style_get_prop_group
    Source: src/misc/lv_style.h:502
    """
    ...

def lv_style_prop_has_flag(prop: int, flag: int) -> bool:
    """
    Do not pass multiple flags to this function as backwards-compatibility is not
    guaranteed for that.
    
    Args:
        prop (int): Property ID
        flag (int): Flag
    
    Returns:
        true if the flag is set for this property
    
    
    C function: lv_style_prop_has_flag
    Source: src/misc/lv_style.h:588
    """
    ...

def lv_obj_style_get_selector_state(selector: int) -> int:
    ...

def lv_obj_style_get_selector_part(selector: int) -> int:
    ...

def lv_task_handler() -> int:
    ...

def lv_thread_init(user_data: None, name: str, prio: int, callback: Any, stack_size: int, thread: None) -> int:
    ...

def lv_thread_delete(thread: None) -> int:
    ...

def lv_mutex_init(mutex: None) -> int:
    ...

def lv_mutex_lock(mutex: None) -> int:
    ...

def lv_mutex_lock_isr(mutex: None) -> int:
    ...

def lv_mutex_unlock(mutex: None) -> int:
    ...

def lv_mutex_delete(mutex: None) -> int:
    ...

def lv_thread_sync_init(sync: None) -> int:
    ...

def lv_thread_sync_wait(sync: None) -> int:
    ...

def lv_thread_sync_signal(sync: None) -> int:
    ...

def lv_thread_sync_signal_isr(sync: None) -> int:
    ...

def lv_thread_sync_delete(sync: None) -> int:
    ...

def lv_lock() -> None:
    ...

def lv_lock_isr() -> int:
    ...

def lv_unlock() -> None:
    ...

def lv_text_is_break_char(letter: int) -> bool:
    """
    Test if char is break char or not (a text can broken here or not)
    
    Args:
        letter (int): a letter
    
    Returns:
        false: 'letter' is not break char
    
    
    C function: lv_text_is_break_char
    Source: src/misc/lv_text_private.h:90
    """
    ...

def lv_text_is_a_word(letter: int) -> bool:
    """
    Test if char is break char or not (a text can broken here or not)
    
    Args:
        letter (int): a letter
    
    Returns:
        false: 'letter' is not break char
    
    
    C function: lv_text_is_a_word
    Source: src/misc/lv_text_private.h:111
    """
    ...

def lv_text_is_marker(letter: int) -> bool:
    """
    Test if character can be treated as marker, and don't need to be rendered. Note, this
    is not a full list. Add your findings to the list.
    
    Args:
        letter (int): a letter
    
    Returns:
        true if so
    
    
    C function: lv_text_is_marker
    Source: src/misc/lv_text_private.h:166
    """
    ...

def lv_version_major() -> int:
    ...

def lv_version_minor() -> int:
    ...

def lv_version_patch() -> int:
    ...

def lv_version_info() -> str:
    ...

def mp_lv_init_gc() -> None:
    ...

def mp_lv_deinit_gc() -> None:
    ...

def lv_init() -> None:
    ...

def lv_deinit() -> None:
    ...

def lv_is_initialized() -> bool:
    ...

def lv_memcpy(dst: None, src: None, len: int) -> None:
    ...

def lv_memset(dst: None, v: int, len: int) -> None:
    ...

def lv_memmove(dst: None, src: None, len: int) -> None:
    ...

def lv_memcmp(p1: None, p2: None, len: int) -> int:
    ...

def lv_strlen(str: str) -> int:
    ...

def lv_strnlen(str: str, max_len: int) -> int:
    ...

def lv_strlcpy(dst: str, src: str, dst_size: int) -> int:
    ...

def lv_strncpy(dst: str, src: str, dest_size: int) -> str:
    ...

def lv_strcpy(dst: str, src: str) -> str:
    ...

def lv_strcmp(s1: str, s2: str) -> int:
    ...

def lv_strncmp(s1: str, s2: str, len: int) -> int:
    ...

def lv_strdup(src: str) -> str:
    ...

def lv_strndup(src: str, max_len: int) -> str:
    ...

def lv_strcat(dst: str, src: str) -> str:
    ...

def lv_strncat(dst: str, src: str, dest_size: int) -> str:
    ...

def lv_strchr(str: str, c: int) -> str:
    ...

def lv_mem_init() -> None:
    ...

def lv_mem_deinit() -> None:
    ...

def lv_mem_add_pool(mem: None, bytes: int) -> None:
    ...

def lv_mem_remove_pool(pool: None) -> None:
    ...

def lv_malloc(size: int) -> None:
    ...

def lv_calloc(num: int, size: int) -> None:
    ...

def lv_zalloc(size: int) -> None:
    ...

def lv_malloc_zeroed(size: int) -> None:
    ...

def lv_free(draw_buf: None) -> None:
    ...

def lv_realloc(data_p: None, new_size: int) -> None:
    ...

def lv_reallocf(data_p: None, new_size: int) -> None:
    ...

def lv_malloc_core(size: int) -> None:
    ...

def lv_free_core(draw_buf: None) -> None:
    ...

def lv_realloc_core(data_p: None, new_size: int) -> None:
    ...

def lv_mem_test_core() -> int:
    ...

def lv_mem_test() -> int:
    ...

def lv_tick_inc(ms: int) -> None:
    ...

def lv_tick_get() -> int:
    ...

def lv_tick_elaps(prev_tick: int) -> int:
    ...

def lv_delay_ms(ms: int) -> None:
    ...

def lv_tick_set_cb(cb: Any) -> None:
    ...

def lv_delay_set_cb(cb: Any) -> None:
    ...

def lv_timer_handler() -> int:
    """
    Call it periodically to handle lv_timers.
    
    Returns:
        time till it needs to be run next (in ms)
    
    
    C function: lv_timer_handler
    Source: src/misc/lv_timer.h:53
    """
    ...

def lv_timer_handler_run_in_period(prev_tick: int) -> int:
    """
    Call it in the super-loop of main() or threads. It will run lv_timer_handler() with a
    given period in ms. You can use it with sleep or delay in OS environment. This
    function is used to simplify the porting.
    
    Args:
        prev_tick (int): Parameter description not available.
    
    Returns:
        the time after which it must be called again
    
    
    C function: lv_timer_handler_run_in_period
    Source: src/misc/lv_timer.h:64
    """
    ...

def lv_timer_periodic_handler() -> None:
    """
    Call it in the super-loop of main() or threads. It will automatically call
    lv_timer_handler() at the right time. This function is used to simplify the porting.
    
    
    C function: lv_timer_periodic_handler
    Source: src/misc/lv_timer.h:70
    """
    ...

def lv_timer_handler_set_resume_cb(cb: Any, data: None) -> None:
    """
    Set the resume callback to the timer handler
    
    Args:
        cb (Any): the function to call when timer handler is resumed
        data (None): pointer to a resume data
    
    
    C function: lv_timer_handler_set_resume_cb
    Source: src/misc/lv_timer.h:77
    """
    ...

def lv_timer_create_basic() -> timer:
    """
    Create an "empty" timer. It needs to be initialized with at least `lv_timer_set_cb`
    and `lv_timer_set_period`
    
    Returns:
        pointer to the created timer
    
    
    C function: lv_timer_create_basic
    Source: src/misc/lv_timer.h:84
    """
    ...

def lv_timer_create(user_data: None, period: int, timer_xcb: Any) -> timer:
    """
    Create a new lv_timer
    
    Args:
        user_data (None): custom parameter
        period (int): call period in ms unit
        timer_xcb (Any): a callback to call periodically. (the 'x' in the argument name
                         indicates that it's not a fully generic function because it not
                         follows the `func_name(object, callback, ...)` convention)
    
    Returns:
        pointer to the new timer
    
    
    C function: lv_timer_create
    Source: src/misc/lv_timer.h:95
    """
    ...

def lv_timer_enable(en: bool) -> None:
    """
    Enable or disable the whole lv_timer handling
    
    Args:
        en (bool): true: lv_timer handling is running, false: lv_timer handling is
                   suspended
    
    
    C function: lv_timer_enable
    Source: src/misc/lv_timer.h:167
    """
    ...

def lv_timer_get_idle() -> int:
    """
    Get idle percentage
    
    Returns:
        the lv_timer idle in percentage
    
    
    C function: lv_timer_get_idle
    Source: src/misc/lv_timer.h:173
    """
    ...

def lv_timer_get_time_until_next() -> int:
    """
    Get the time remaining until the next timer will run
    
    Returns:
        the time remaining in ms
    
    
    C function: lv_timer_get_time_until_next
    Source: src/misc/lv_timer.h:179
    """
    ...

def lv_trigo_sin(angle: int) -> int:
    """
    Return with sinus of an angle
    
    Args:
        angle (int): Parameter description not available.
    
    Returns:
        sinus of 'angle'. sin(-90) = -32767, sin(90) = 32767
    
    
    C function: lv_trigo_sin
    Source: src/misc/lv_math.h:54
    """
    ...

def lv_trigo_cos(angle: int) -> int:
    ...

def lv_cubic_bezier(x: int, x1: int, y1: int, x2: int, y2: int) -> int:
    """
    Calculate the y value of cubic-bezier(x1, y1, x2, y2) function as specified x.
    
    Args:
        x (int): time in range of [0..LV_BEZIER_VAL_MAX]
        x1 (int): x of control point 1 in range of [0..LV_BEZIER_VAL_MAX]
        y1 (int): y of control point 1 in range of [0..LV_BEZIER_VAL_MAX]
        x2 (int): x of control point 2 in range of [0..LV_BEZIER_VAL_MAX]
        y2 (int): y of control point 2 in range of [0..LV_BEZIER_VAL_MAX]
    
    Returns:
        the value calculated
    
    
    C function: lv_cubic_bezier
    Source: src/misc/lv_math.h:69
    """
    ...

def lv_bezier3(t: int, u0: int, u1: int, u2: int, u3: int) -> int:
    """
    Calculate a value of a Cubic Bezier function.
    
    Args:
        t (int): time in range of [0..LV_BEZIER_VAL_MAX]
        u0 (int): must be 0
        u1 (int): control value 1 values in range of [0..LV_BEZIER_VAL_MAX]
        u2 (int): control value 2 in range of [0..LV_BEZIER_VAL_MAX]
        u3 (int): must be LV_BEZIER_VAL_MAX
    
    Returns:
        the value calculated from the given parameters in range of
        [0..LV_BEZIER_VAL_MAX]
    
    
    C function: lv_bezier3
    Source: src/misc/lv_math.h:80
    """
    ...

def lv_atan2(x: int, y: int) -> int:
    """
    Calculate the atan2 of a vector.
    
    Args:
        x (int): Parameter description not available.
        y (int): Parameter description not available.
    
    Returns:
        the angle in degree calculated from the given parameters in range of [0..360]
    
    
    C function: lv_atan2
    Source: src/misc/lv_math.h:89
    """
    ...

def lv_sqrt(x: int, q: sqrt_res, mask: int) -> None:
    """
    Get the square root of a number
    
    Args:
        x (int): integer which square root should be calculated
        q (sqrt_res): store the result here. q->i: integer part, q->f: fractional part in
                      1/256 unit
        mask (int): optional to skip some iterations if the magnitude of the root is
                    known. Set to 0x8000 by default. If root < 16: mask = 0x80 If root <
                    256: mask = 0x800 Else: mask = 0x8000
    
    
    C function: lv_sqrt
    Source: src/misc/lv_math.h:103
    """
    ...

def lv_sqrt32(x: int) -> int:
    """
    Alternative (fast, approximate) implementation for getting the square root of an
    integer.
    
    Args:
        x (int): integer which square root should be calculated
    
    
    C function: lv_sqrt32
    Source: src/misc/lv_math.h:111
    """
    ...

def lv_pow(base: int, exp: int) -> int:
    """
    Calculate the integer exponents.
    
    Args:
        base (int): Parameter description not available.
        exp (int): Parameter description not available.
    
    Returns:
        base raised to the power exponent
    
    
    C function: lv_pow
    Source: src/misc/lv_math.h:129
    """
    ...

def lv_map(x: int, x1: int, y1: int, x2: int, y2: int) -> int:
    """
    Get the mapped of a number given an input and output range
    
    Args:
        x (int): integer which mapped value should be calculated
        x1 (int): Parameter description not available.
        y1 (int): Parameter description not available.
        x2 (int): Parameter description not available.
        y2 (int): Parameter description not available.
    
    Returns:
        the mapped number
    
    
    C function: lv_map
    Source: src/misc/lv_math.h:140
    """
    ...

def lv_rand_set_seed(ms: int) -> None:
    """
    Set the seed of the pseudo random number generator
    
    Args:
        ms (int): Parameter description not available.
    
    
    C function: lv_rand_set_seed
    Source: src/misc/lv_math.h:146
    """
    ...

def lv_rand(min: int, max: int) -> int:
    """
    Get a pseudo random number in the given range
    
    Args:
        min (int): the minimum value
        max (int): the maximum value
    
    Returns:
        return the random number. min <= return_value <= max
    
    
    C function: lv_rand
    Source: src/misc/lv_math.h:154
    """
    ...

def lv_async_call(user_data: None, async_xcb: Any) -> int:
    """
    Call an asynchronous function the next time lv_timer_handler() is run. This function
    is likely to return **before** the call actually happens!
    
    Args:
        user_data (None): custom parameter
        async_xcb (Any): a callback which is the task itself. (the 'x' in the argument
                         name indicates that it's not a fully generic function because it
                         not follows the `func_name(object, callback, ...)` convention)
    
    
    C function: lv_async_call
    Source: src/misc/lv_async.h:44
    """
    ...

def lv_async_call_cancel(user_data: None, async_xcb: Any) -> int:
    """
    Cancel an asynchronous function call
    
    Args:
        user_data (None): custom parameter
        async_xcb (Any): a callback which is the task itself.
    
    
    C function: lv_async_call_cancel
    Source: src/misc/lv_async.h:51
    """
    ...

def lv_anim_delete(var: None, exec_cb: Any) -> bool:
    """
    Delete animation(s) of a variable with a given animator function
    
    Args:
        var (None): pointer to variable
        exec_cb (Any): a function pointer which is animating 'var', or NULL to ignore it
                       and delete all the animations of 'var
    
    Returns:
        true: at least 1 animation is deleted, false: no animation is deleted
    
    
    C function: lv_anim_delete
    Source: src/misc/lv_anim.h:392
    """
    ...

def lv_anim_delete_all() -> None:
    """
    Delete all the animations
    
    
    C function: lv_anim_delete_all
    Source: src/misc/lv_anim.h:397
    """
    ...

def lv_anim_get(var: None, exec_cb: Any) -> anim:
    """
    Get the animation of a variable and its `exec_cb`.
    
    Args:
        var (None): pointer to variable
        exec_cb (Any): a function pointer which is animating 'var', or NULL to return
                       first matching 'var'
    
    Returns:
        pointer to the animation.
    
    
    C function: lv_anim_get
    Source: src/misc/lv_anim.h:405
    """
    ...

def lv_anim_get_timer() -> timer:
    """
    Get global animation refresher timer.
    
    Returns:
        pointer to the animation refresher timer.
    
    
    C function: lv_anim_get_timer
    Source: src/misc/lv_anim.h:411
    """
    ...

def lv_anim_count_running() -> int:
    """
    Get the number of currently running animations
    
    Returns:
        the number of running animations
    
    
    C function: lv_anim_count_running
    Source: src/misc/lv_anim.h:441
    """
    ...

def lv_anim_speed(prev_tick: int) -> int:
    """
    Store the speed as a special value which can be used as time in animations. It will
    be converted to time internally based on the start and end values. The return value
    can be used as a constant with multiple animations and let LVGL convert the speed to
    time based on the actual values. LIMITATION: the max time stored this way can be
    10,000 ms.
    
    Args:
        prev_tick (int): Parameter description not available.
    
    Returns:
        a special value which can be used as an animation time
    
    
    C function: lv_anim_speed
    Source: src/misc/lv_anim.h:453
    """
    ...

def lv_anim_speed_clamped(speed: int, min_time: int, max_time: int) -> int:
    """
    Store the speed as a special value which can be used as time in animations. It will
    be converted to time internally based on the start and end values. The return value
    can be used as a constant with multiple animations and let LVGL convert the speed to
    time based on the actual values.
    
    Args:
        speed (int): the speed of the animation in as unit / sec resolution in 0..10k
                     range
        min_time (int): the minimum time in 0..10k range
        max_time (int): the maximum time in 0..10k range
    
    Returns:
        a special value in where all three values are stored and can be used as an
        animation time
    
    
    C function: lv_anim_speed_clamped
    Source: src/misc/lv_anim.h:468
    """
    ...

def lv_anim_resolve_speed(speed: int, start: int, end: int) -> int:
    """
    Resolve the speed (created with `lv_anim_speed` or `lv_anim_speed_clamped`) to time
    based on start and end values.
    
    Args:
        speed (int): return values of `lv_anim_speed` or `lv_anim_speed_clamped`
        start (int): the start value of the animation
        end (int): the end value of the animation
    
    Returns:
        the time required to get from `start` to `end` with the given `speed` setting
    
    
    C function: lv_anim_resolve_speed
    Source: src/misc/lv_anim.h:478
    """
    ...

def lv_anim_speed_to_time(speed: int, start: int, end: int) -> int:
    """
    Calculate the time of an animation based on its speed, start and end values. It
    simpler than `lv_anim_speed` or `lv_anim_speed_clamped` as it converts speed, start,
    and end to a time immediately. As it's simpler there is no limit on the maximum time.
    
    Args:
        speed (int): the speed of the animation
        start (int): the start value
        end (int): the end value
    
    Returns:
        the time of the animation in milliseconds
    
    
    C function: lv_anim_speed_to_time
    Source: src/misc/lv_anim.h:490
    """
    ...

def lv_anim_refr_now() -> None:
    """
    Manually refresh the state of the animations. Useful to make the animations running
    in a blocking process where `lv_timer_handler` can't run for a while. Shouldn't be
    used directly because it is called in `lv_refr_now()`.
    
    
    C function: lv_anim_refr_now
    Source: src/misc/lv_anim.h:499
    """
    ...

def lv_anim_timeline_create() -> anim_timeline:
    """
    Create an animation timeline.
    
    Returns:
        pointer to the animation timeline.
    
    
    C function: lv_anim_timeline_create
    Source: src/misc/lv_anim_timeline.h:38
    """
    ...

def lv_pct(x: int) -> int:
    """
    Convert a percentage value to `int32_t`. Percentage values are stored in special
    range
    
    Args:
        x (int): the percentage (0..1000)
    
    Returns:
        a coordinate that stores the percentage
    
    
    C function: lv_pct
    Source: src/misc/lv_area.h:246
    """
    ...

def lv_pct_to_px(v: int, base: int) -> int:
    ...

def lv_color_format_get_bpp(cf: int) -> int:
    """
    Get the pixel size of a color format in bits, bpp
    
    Args:
        cf (int): a color format (`LV_COLOR_FORMAT_...`)
    
    Returns:
        the pixel size in bits
    
    
    C function: lv_color_format_get_bpp
    Source: src/misc/lv_color.h:246
    """
    ...

def lv_color_format_get_size(cf: int) -> int:
    """
    Get the pixel size of a color format in bytes
    
    Args:
        cf (int): a color format (`LV_COLOR_FORMAT_...`)
    
    Returns:
        the pixel size in bytes
    
    
    C function: lv_color_format_get_size
    Source: src/misc/lv_color.h:254
    """
    ...

def lv_color_format_has_alpha(src_cf: int) -> bool:
    """
    Check if a color format has alpha channel or not
    
    Args:
        src_cf (int): a color format (`LV_COLOR_FORMAT_...`)
    
    Returns:
        true: has alpha channel; false: doesn't have alpha channel
    
    
    C function: lv_color_format_has_alpha
    Source: src/misc/lv_color.h:261
    """
    ...

def lv_color_hex(c: int) -> color:
    """
    Create a color from 0x000000..0xffffff input
    
    Args:
        c (int): the hex input
    
    Returns:
        the color
    
    
    C function: lv_color_hex
    Source: src/misc/lv_color.h:299
    """
    ...

def lv_color_make(r: int, g: int, b: int) -> color:
    """
    Create an RGB888 color
    
    Args:
        r (int): the red channel (0..255)
        g (int): the green channel (0..255)
        b (int): the blue channel (0..255)
    
    Returns:
        the color
    
    
    C function: lv_color_make
    Source: src/misc/lv_color.h:308
    """
    ...

def lv_color32_make(r: int, g: int, b: int, a: int) -> color32:
    """
    Create an ARGB8888 color
    
    Args:
        r (int): the red channel (0..255)
        g (int): the green channel (0..255)
        b (int): the blue channel (0..255)
        a (int): the alpha channel (0..255)
    
    Returns:
        the color
    
    
    C function: lv_color32_make
    Source: src/misc/lv_color.h:318
    """
    ...

def lv_color_hex3(c: int) -> color:
    """
    Create a color from 0x000..0xfff input
    
    Args:
        c (int): the hex input (e.g. 0x123 will be 0x112233)
    
    Returns:
        the color
    
    
    C function: lv_color_hex3
    Source: src/misc/lv_color.h:325
    """
    ...

def lv_color_16_16_mix(c1: int, c2: int, mix: int) -> int:
    """
    Mix two RGB565 colors
    
    Args:
        c1 (int): the first color (typically the foreground color)
        c2 (int): the second color  (typically the background color)
        mix (int): 0..255, or LV_OPA_0/10/20...
    
    Returns:
        mix == 0: c2 mix == 255: c1 mix == 128: 0.5 x c1 + 0.5 x c2
    
    
    C function: lv_color_16_16_mix
    Source: src/misc/lv_color.h:350
    """
    ...

def lv_color_hsv_to_rgb(h: int, s: int, v: int) -> color:
    """
    Convert a HSV color to RGB
    
    Args:
        h (int): hue [0..359]
        s (int): saturation [0..100]
        v (int): value [0..100]
    
    Returns:
        the given RGB color in RGB (with LV_COLOR_DEPTH depth)
    
    
    C function: lv_color_hsv_to_rgb
    Source: src/misc/lv_color.h:375
    """
    ...

def lv_color_rgb_to_hsv(r8: int, g8: int, b8: int) -> color_hsv:
    """
    Convert a 32-bit RGB color to HSV
    
    Args:
        r8 (int): 8-bit red
        g8 (int): 8-bit green
        b8 (int): 8-bit blue
    
    Returns:
        the given RGB color in HSV
    
    
    C function: lv_color_rgb_to_hsv
    Source: src/misc/lv_color.h:384
    """
    ...

def lv_color_white() -> color:
    """
    A helper for white color
    
    Returns:
        a white color
    
    
    C function: lv_color_white
    Source: src/misc/lv_color.h:399
    """
    ...

def lv_color_black() -> color:
    """
    A helper for black color
    
    Returns:
        a black color
    
    
    C function: lv_color_black
    Source: src/misc/lv_color.h:405
    """
    ...

def lv_color24_luminance(c: None) -> int:
    """
    Get the luminance of a color24: luminance = 0.3 R + 0.59 G + 0.11 B
    
    Args:
        c (None): a color
    
    Returns:
        the brightness [0..255]
    
    
    C function: lv_color24_luminance
    Source: src/misc/lv_color.h:430
    """
    ...

def lv_palette_main(p: int) -> color:
    """
    ******************** GLOBAL PROTOTYPES *********************/ /*Source:
    https://vuetifyjs.com/en/styles/colors/#material-colors*/
    
    Args:
        p (int): Parameter description not available.
    
    
    C function: lv_palette_main
    Source: src/misc/lv_palette.h:56
    """
    ...

def lv_palette_lighten(p: int, lvl: int) -> color:
    ...

def lv_palette_darken(p: int, lvl: int) -> color:
    ...

def lv_draw_buf_get_handlers() -> draw_buf_handlers:
    """
    Get the struct which holds the callbacks for draw buf management. Custom callback can
    be set on the returned value
    
    Returns:
        pointer to the struct of handlers
    
    
    C function: lv_draw_buf_get_handlers
    Source: src/draw/lv_draw_buf.h:131
    """
    ...

def lv_draw_buf_get_font_handlers() -> draw_buf_handlers:
    ...

def lv_draw_buf_get_image_handlers() -> draw_buf_handlers:
    ...

def lv_draw_buf_align(buf: None, color_format: int) -> None:
    """
    Align the address of a buffer. The buffer needs to be large enough for the real data
    after alignment
    
    Args:
        buf (None): the data to align
        color_format (int): the color format of the buffer
    
    Returns:
        the aligned buffer
    
    
    C function: lv_draw_buf_align
    Source: src/draw/lv_draw_buf.h:142
    """
    ...

def lv_draw_buf_width_to_stride(w: int, color_format: int) -> int:
    """
    Calculate the stride in bytes based on a width and color format
    
    Args:
        w (int): the width in pixels
        color_format (int): the color format
    
    Returns:
        the stride in bytes
    
    
    C function: lv_draw_buf_width_to_stride
    Source: src/draw/lv_draw_buf.h:176
    """
    ...

def lv_draw_buf_create(w: int, h: int, cf: int, stride: int) -> draw_buf:
    """
    Note: Eventually, lv_draw_buf_malloc/free will be kept as private. For now, we use
    `create` to distinguish with malloc. Create an draw buf by allocating struct for
    `lv_draw_buf_t` and allocating a buffer for it that meets specified requirements.
    
    Args:
        w (int): the buffer width in pixels
        h (int): the buffer height in pixels
        cf (int): the color format for image
        stride (int): the stride in bytes for image. Use 0 for automatic calculation
                      based on w, cf, and global stride alignment configuration.
    
    
    C function: lv_draw_buf_create
    Source: src/draw/lv_draw_buf.h:220
    """
    ...

def lv_utils_bsearch(key: None, base: None, n: int, size: int, cmp: Any) -> None:
    """
    Searches base[0] to base[n - 1] for an item that matches *key. argument (the search
    key) is less that it's second (a table entry), zero if equal, and positive if
    greater.
    
    Args:
        key (None): Pointer to item being searched for
        base (None): Pointer to first element to search
        n (int): Number of elements
        size (int): Size of each element
        cmp (Any): Pointer to comparison function (see unicode_list_compare() as a
                   comparison function example)
    
    Returns:
        a pointer to a matching item, or NULL if none exists.
    
    
    C function: lv_utils_bsearch
    Source: src/misc/lv_utils.h:49
    """
    ...

def lv_iter_create(instance: None, elem_size: int, context_size: int, next_cb: Any) -> iter:
    """
    Create an iterator based on an instance, and then the next element of the iterator
    can be obtained through lv_iter_next, In order to obtain the next operation in a
    unified and abstract way.
    
    Args:
        instance (None): The instance to be iterated
        elem_size (int): The size of the element to be iterated in bytes
        context_size (int): The size of the context to be passed to the next_cb in bytes
        next_cb (Any): The callback function to get the next element
    
    Returns:
        The iterator object
    
    
    C function: lv_iter_create
    Source: src/misc/lv_iter.h:44
    """
    ...

def lv_circle_buf_create(capacity: int, element_size: int) -> circle_buf:
    """
    Create a circle buffer
    
    Args:
        capacity (int): the maximum number of elements in the buffer
        element_size (int): the size of an element in bytes
    
    Returns:
        pointer to the created buffer
    
    
    C function: lv_circle_buf_create
    Source: src/misc/lv_circle_buf.h:40
    """
    ...

def lv_circle_buf_create_from_buf(buf: None, capacity: int, element_size: int) -> circle_buf:
    """
    Create a circle buffer from an existing buffer
    
    Args:
        buf (None): pointer to a buffer
        capacity (int): the maximum number of elements in the buffer
        element_size (int): the size of an element in bytes
    
    Returns:
        pointer to the created buffer
    
    
    C function: lv_circle_buf_create_from_buf
    Source: src/misc/lv_circle_buf.h:49
    """
    ...

def lv_image_cache_init(size: int) -> int:
    """
    Initialize image cache.
    
    Args:
        size (int): size of the cache in bytes.
    
    Returns:
        LV_RESULT_OK: initialization succeeded, LV_RESULT_INVALID: failed.
    
    
    C function: lv_image_cache_init
    Source: src/misc/cache/lv_image_cache.h:37
    """
    ...

def lv_image_cache_resize(new_size: int, evict_now: bool) -> None:
    """
    Resize image cache. If set to 0, the cache will be disabled.
    
    Args:
        new_size (int): new size of the cache in bytes.
        evict_now (bool): true: evict the images should be removed by the eviction
                          policy, false: wait for the next cache cleanup.
    
    
    C function: lv_image_cache_resize
    Source: src/misc/cache/lv_image_cache.h:45
    """
    ...

def lv_image_cache_drop(src: None) -> None:
    """
    Invalidate image cache. Use NULL to invalidate all images.
    
    Args:
        src (None): pointer to an image source.
    
    
    C function: lv_image_cache_drop
    Source: src/misc/cache/lv_image_cache.h:51
    """
    ...

def lv_image_cache_is_enabled() -> bool:
    """
    Return true if the image cache is enabled.
    
    Returns:
        true: enabled, false: disabled.
    
    
    C function: lv_image_cache_is_enabled
    Source: src/misc/cache/lv_image_cache.h:57
    """
    ...

def lv_image_cache_iter_create() -> iter:
    """
    Create an iterator to iterate over the image cache.
    
    Returns:
        an iterator to iterate over the image cache.
    
    
    C function: lv_image_cache_iter_create
    Source: src/misc/cache/lv_image_cache.h:63
    """
    ...

def lv_image_cache_dump() -> None:
    """
    Dump the content of the image cache in a human-readable format with cache order.
    
    
    C function: lv_image_cache_dump
    Source: src/misc/cache/lv_image_cache.h:68
    """
    ...

def lv_font_get_default() -> font:
    ...

def lv_text_get_width(txt: str, length: int, font: font, letter_space: int) -> int:
    """
    Give the length of a text with a given font
    
    Args:
        txt (str): a '\0' terminate string
        length (int): length of 'txt' in byte count and not characters (Á is 1 character
                      but 2 bytes in UTF-8)
        font (font): pointer to a font
        letter_space (int): letter space
    
    Returns:
        length of a char_num long text
    
    
    C function: lv_text_get_width
    Source: src/misc/lv_text.h:97
    """
    ...

def lv_text_get_width_with_flags(txt: str, length: int, font: font, letter_space: int, flags: int) -> int:
    """
    Give the length of a text with a given font with text flags
    
    Args:
        txt (str): a '\0' terminate string
        length (int): length of 'txt' in byte count and not characters (Á is 1 character
                      but 2 bytes in UTF-8)
        font (font): pointer to a font
        letter_space (int): letter space
        flags (int): settings for the text from ::lv_text_flag_t
    
    Returns:
        length of a char_num long text
    
    
    C function: lv_text_get_width_with_flags
    Source: src/misc/lv_text.h:109
    """
    ...

def lv_text_is_cmd(state: None, c: int) -> bool:
    """
    Check if c is command state
    
    Args:
        state (None): Parameter description not available.
        c (int): Parameter description not available.
    
    Returns:
        True if c is state
    
    
    C function: lv_text_is_cmd
    Source: src/misc/lv_text.h:118
    """
    ...

def lv_layout_register(user_data: None, cb: Any) -> int:
    ...

def lv_flex_init() -> None:
    ...

def lv_grid_init() -> None:
    ...

def lv_grid_fr(x: int) -> int:
    ...

def lv_style_register_prop(flag: int) -> int:
    """
    Register a new style property for custom usage lv_style_prop_t MY_PROP; static inline
    void lv_style_set_my_prop(lv_style_t * style, lv_color_t value) { lv_style_value_t v
    = {.color = value}; lv_style_set_prop(style, MY_PROP, v); } ... MY_PROP =
    lv_style_register_prop(); ... lv_style_set_my_prop(&style1,
    lv_palette_main(LV_PALETTE_RED));
    
    Args:
        flag (int): Parameter description not available.
    
    Returns:
        a new property ID, or LV_STYLE_PROP_INV if there are no more available.
        Example:
    
    
    C function: lv_style_register_prop
    Source: src/misc/lv_style.h:390
    """
    ...

def lv_style_get_num_custom_props() -> int:
    """
    Get the number of custom properties that have been registered thus far.
    
    
    C function: lv_style_get_num_custom_props
    Source: src/misc/lv_style.h:395
    """
    ...

def lv_style_prop_get_default(prop: int) -> style_value:
    """
    Get the default value of a property
    
    Args:
        prop (int): the ID of a property
    
    Returns:
        the default value
    
    
    C function: lv_style_prop_get_default
    Source: src/misc/lv_style.h:450
    """
    ...

def lv_style_prop_lookup_flags(prop: int) -> int:
    """
    Get the flags of a built-in or custom property.
    
    Args:
        prop (int): a style property
    
    Returns:
        the flags of the property
    
    
    C function: lv_style_prop_lookup_flags
    Source: src/misc/lv_style.h:516
    """
    ...

def lv_event_register_id() -> int:
    """
    Register a new, custom event ID. It can be used the same way as e.g.
    `LV_EVENT_CLICKED` to send custom events uint32_t LV_EVENT_MINE = 0; ... e =
    lv_event_register_id(); ... lv_obj_send_event(obj, LV_EVENT_MINE, &some_data);
    
    Returns:
        the new event id Example:
    
    
    C function: lv_event_register_id
    Source: src/misc/lv_event.h:218
    """
    ...

def lv_event_code_get_name(code: int) -> str:
    """
    Get the name of an event code.
    
    Args:
        code (int): the event code
    
    Returns:
        the name of the event code as a string
    
    
    C function: lv_event_code_get_name
    Source: src/misc/lv_event.h:225
    """
    ...

def lv_display_create(hor_res: int, ver_res: int) -> display:
    ...

def lv_display_get_default() -> display:
    ...

def lv_screen_active() -> obj:
    ...

def lv_layer_top() -> obj:
    ...

def lv_layer_sys() -> obj:
    ...

def lv_layer_bottom() -> obj:
    ...

def lv_dpx(x: int) -> int:
    ...

def lv_clamp_width(width: int, min_width: int, max_width: int, ref_width: int) -> int:
    """
    Clamp a width between min and max width. If the min/max width is in percentage value
    use the ref_width
    
    Args:
        width (int): width to clamp
        min_width (int): the minimal width
        max_width (int): the maximal width
        ref_width (int): the reference width used when min/max width is in percentage
    
    Returns:
        the clamped width
    
    
    C function: lv_clamp_width
    Source: src/core/lv_obj_pos.h:453
    """
    ...

def lv_clamp_height(width: int, min_width: int, max_width: int, ref_width: int) -> int:
    """
    Clamp a height between min and max height. If the min/max height is in percentage
    value use the ref_height
    
    Args:
        width (int): Parameter description not available.
        min_width (int): Parameter description not available.
        max_width (int): Parameter description not available.
        ref_width (int): Parameter description not available.
    
    Returns:
        the clamped height
    
    
    C function: lv_clamp_height
    Source: src/core/lv_obj_pos.h:463
    """
    ...

def lv_obj_enable_style_refresh(en: bool) -> None:
    """
    Enable or disable automatic style refreshing when a new style is added/removed
    to/from an object or any other style change happens.
    
    Args:
        en (bool): true: enable refreshing; false: disable refreshing
    
    
    C function: lv_obj_enable_style_refresh
    Source: src/core/lv_obj_style.h:118
    """
    ...

def lv_fs_get_drv(letter: int) -> fs_drv:
    """
    Give a pointer to a driver from its letter
    
    Args:
        letter (int): the driver-identifier letter
    
    Returns:
        pointer to a driver or NULL if not found
    
    
    C function: lv_fs_get_drv
    Source: src/misc/lv_fs.h:125
    """
    ...

def lv_fs_is_ready(letter: int) -> bool:
    """
    Test if a drive is ready or not. If the `ready` function was not initialized `true`
    will be returned.
    
    Args:
        letter (int): letter of the drive
    
    Returns:
        true: drive is ready; false: drive is not ready
    
    
    C function: lv_fs_is_ready
    Source: src/misc/lv_fs.h:133
    """
    ...

def lv_fs_get_letters(buf: str) -> str:
    """
    Fill a buffer with the letters of existing drivers
    
    Args:
        buf (str): buffer to store the letters ('\0' added after the last letter)
    
    Returns:
        the buffer
    
    
    C function: lv_fs_get_letters
    Source: src/misc/lv_fs.h:227
    """
    ...

def lv_fs_get_ext(fn: str) -> str:
    """
    Return with the extension of the filename
    
    Args:
        fn (str): string with a filename
    
    Returns:
        pointer to the beginning extension or empty string if no extension
    
    
    C function: lv_fs_get_ext
    Source: src/misc/lv_fs.h:234
    """
    ...

def lv_fs_up(buf: str) -> str:
    """
    Step up one level
    
    Args:
        buf (str): Parameter description not available.
    
    Returns:
        the truncated file name
    
    
    C function: lv_fs_up
    Source: src/misc/lv_fs.h:241
    """
    ...

def lv_fs_get_last(fn: str) -> str:
    """
    Get the last element of a path (e.g. U:/folder/file -> file)
    
    Args:
        fn (str): Parameter description not available.
    
    Returns:
        pointer to the beginning of the last element in the path
    
    
    C function: lv_fs_get_last
    Source: src/misc/lv_fs.h:248
    """
    ...

def lv_image_decoder_get_info(src: None, header: image_header) -> int:
    """
    Get information about an image. Try the created image decoder one by one. Once one is
    able to get info that info will be used.
    
    Args:
        src (None): the image source. Can be 1) File name: E.g. "S:folder/img1.png" (The
                    drivers needs to registered via `lv_fs_drv_register()`) 2) Variable:
                    Pointer to an `lv_image_dsc_t` variable 3) Symbol: E.g.
                    `LV_SYMBOL_OK`
        header (image_header): the image info will be stored here
    
    Returns:
        LV_RESULT_OK: success; LV_RESULT_INVALID: wasn't able to get info about the
        image
    
    
    C function: lv_image_decoder_get_info
    Source: src/draw/lv_image_decoder.h:102
    """
    ...

def lv_image_decoder_create() -> image_decoder:
    """
    Create a new image decoder
    
    Returns:
        pointer to the new image decoder
    
    
    C function: lv_image_decoder_create
    Source: src/draw/lv_image_decoder.h:139
    """
    ...

def lv_draw_init() -> None:
    """
    Used internally to initialize the drawing module
    
    
    C function: lv_draw_init
    Source: src/draw/lv_draw.h:133
    """
    ...

def lv_draw_deinit() -> None:
    """
    Deinitialize the drawing module
    
    
    C function: lv_draw_deinit
    Source: src/draw/lv_draw.h:138
    """
    ...

def lv_draw_create_unit(size: int) -> None:
    """
    Allocate a new draw unit with the given size and appends it to the list of draw units
    
    Args:
        size (int): the size to allocate. E.g. `sizeof(my_draw_unit_t)`, where the first
                    element of `my_draw_unit_t` is `lv_draw_unit_t`.
    
    
    C function: lv_draw_create_unit
    Source: src/draw/lv_draw.h:145
    """
    ...

def lv_draw_dispatch() -> None:
    """
    Try dispatching draw tasks to draw units
    
    
    C function: lv_draw_dispatch
    Source: src/draw/lv_draw.h:168
    """
    ...

def lv_draw_dispatch_wait_for_request() -> None:
    """
    Wait for a new dispatch request. It's blocking if `LV_USE_OS == 0` else it yields
    
    
    C function: lv_draw_dispatch_wait_for_request
    Source: src/draw/lv_draw.h:182
    """
    ...

def lv_draw_wait_for_finish() -> None:
    """
    Wait for draw finish in case of asynchronous task execution. If `LV_USE_OS == 0` it
    just return.
    
    
    C function: lv_draw_wait_for_finish
    Source: src/draw/lv_draw.h:188
    """
    ...

def lv_draw_dispatch_request() -> None:
    """
    When a draw unit finished a draw task it needs to request dispatching to let LVGL
    assign a new draw task to it
    
    
    C function: lv_draw_dispatch_request
    Source: src/draw/lv_draw.h:194
    """
    ...

def lv_draw_get_unit_count() -> int:
    """
    Get the total number of draw units.
    
    
    C function: lv_draw_get_unit_count
    Source: src/draw/lv_draw.h:199
    """
    ...

def lv_image_src_get_type(src: None) -> int:
    """
    Get the type of an image source
    
    Args:
        src (None): pointer to an image source: - pointer to an 'lv_image_t' variable
                    (image stored internally and compiled into the code) - a path to a
                    file (e.g. "S:/folder/image.bin") - or a symbol (e.g.
                    LV_SYMBOL_CLOSE)
    
    Returns:
        type of the image source LV_IMAGE_SRC_VARIABLE/FILE/SYMBOL/UNKNOWN
    
    
    C function: lv_image_src_get_type
    Source: src/draw/lv_draw_image.h:123
    """
    ...

def lv_draw_arc_get_area(x: int, y: int, radius: int, start_angle: int, end_angle: int, w: int, rounded: bool, area: area) -> None:
    """
    Get an area the should be invalidated when the arcs angle changed between start_angle
    and end_ange
    
    Args:
        x (int): the x coordinate of the center of the arc
        y (int): the y coordinate of the center of the arc
        radius (int): the radius of the arc
        start_angle (int): the start angle of the arc (0 deg on the bottom, 90 deg on the
                           right)
        end_angle (int): the end angle of the arc
        w (int): width of the arc
        rounded (bool): true: the arc is rounded
        area (area): store the area to invalidate here
    
    
    C function: lv_draw_arc_get_area
    Source: src/draw/lv_draw_arc.h:78
    """
    ...

def lv_group_create() -> group:
    """
    Create new Widget group.
    
    Returns:
        pointer to the new Widget group
    
    
    C function: lv_group_create
    Source: src/core/lv_group.h:60
    """
    ...

def lv_group_get_default() -> group:
    """
    Get default group.
    
    Returns:
        pointer to the default group
    
    
    C function: lv_group_get_default
    Source: src/core/lv_group.h:79
    """
    ...

def lv_group_get_count() -> int:
    """
    Get the number of groups.
    
    Returns:
        number of groups
    
    
    C function: lv_group_get_count
    Source: src/core/lv_group.h:231
    """
    ...

def lv_group_by_index(index: int) -> group:
    """
    Get a group by its index.
    
    Args:
        index (int): index of the group
    
    Returns:
        pointer to the group
    
    
    C function: lv_group_by_index
    Source: src/core/lv_group.h:238
    """
    ...

def lv_indev_create() -> indev:
    ...

def lv_indev_active() -> indev:
    ...

def lv_indev_get_active_obj() -> obj:
    ...

def lv_obj_null_on_delete(obj_ptr: None) -> None:
    """
    Utility to set an object reference to NULL when it gets deleted. The reference should
    be in a location that will not become invalid during the object's lifetime, i.e.
    static or allocated.
    
    Args:
        obj_ptr (None): a pointer to a pointer to an object
    
    
    C function: lv_obj_null_on_delete
    Source: src/core/lv_obj.h:384
    """
    ...

def lv_binfont_create(path: str) -> font:
    ...

def lv_binfont_create_from_buffer(buffer: None, size: int) -> font:
    ...

def lv_canvas_buf_size(w: int, h: int, bpp: int, stride: int) -> int:
    """
    Just a wrapper to `LV_CANVAS_BUF_SIZE` for bindings.
    
    Args:
        w (int): Parameter description not available.
        h (int): Parameter description not available.
        bpp (int): Parameter description not available.
        stride (int): Parameter description not available.
    
    
    C function: lv_canvas_buf_size
    Source: src/widgets/canvas/lv_canvas.h:177
    """
    ...

def lv_span_stack_init() -> None:
    """
    ******************** GLOBAL PROTOTYPES *********************/
    
    
    C function: lv_span_stack_init
    Source: src/widgets/span/lv_span.h:57
    """
    ...

def lv_span_stack_deinit() -> None:
    ...

def lv_imgfont_create(user_data: None, path_cb: Any, height: int) -> font:
    ...

def lv_bin_decoder_init() -> None:
    ...

def lv_fs_memfs_init() -> None:
    ...

def lv_lodepng_init() -> None:
    ...

def lv_lodepng_deinit() -> None:
    ...

def gd_open_gif_file(fname: str) -> Any:
    ...

def gd_open_gif_data(data: None) -> Any:
    ...

def lv_tjpgd_init() -> None:
    ...

def lv_tjpgd_deinit() -> None:
    ...

def lv_draw_sw_i1_to_argb8888(buf_i1: None, buf_argb8888: None, width: int, height: int, buf_i1_stride: int, buf_argb8888_stride: int, index0_color: int, index1_color: int) -> None:
    """
    Converts an I1 buffer to ARGB8888 format.
    
    Args:
        buf_i1 (None): pointer to buffer with I1 formatted render
        buf_argb8888 (None): pointer to buffer for ARGB8888 render
        width (int): width in pixels of the area. must be a multiple of 8.
        height (int): height in pixels of the area
        buf_i1_stride (int): stride of i1 buffer in bytes
        buf_argb8888_stride (int): stride of argb8888 buffer in bytes
        index0_color (int): color of the 0 bits of i1 buf
        index1_color (int): color of the 1 bits of i1 buf
    
    
    C function: lv_draw_sw_i1_to_argb8888
    Source: src/draw/sw/lv_draw_sw_utils.h:44
    """
    ...

def lv_draw_sw_rgb565_swap(buf: None, buf_size_px: int) -> None:
    """
    Swap the upper and lower byte of an RGB565 buffer. Might be required if a 8bit
    parallel port or an SPI port send the bytes in the wrong order. The bytes will be
    swapped in place.
    
    Args:
        buf (None): pointer to buffer
        buf_size_px (int): number of pixels in the buffer
    
    
    C function: lv_draw_sw_rgb565_swap
    Source: src/draw/sw/lv_draw_sw_utils.h:54
    """
    ...

def lv_draw_sw_i1_invert(buf: None, buf_size_px: int) -> None:
    """
    Invert a draw buffer in the I1 color format. Conventionally, a bit is set to 1 during
    blending if the luminance is greater than 127. Depending on the display controller
    used, you might want to have different behavior. The inversion will be performed in
    place.
    
    Args:
        buf (None): pointer to the buffer to be inverted
        buf_size_px (int): Parameter description not available.
    
    
    C function: lv_draw_sw_i1_invert
    Source: src/draw/sw/lv_draw_sw_utils.h:64
    """
    ...

def lv_draw_sw_i1_convert_to_vtiled(buf: None, buf_size: int, width: int, height: int, out_buf: None, out_buf_size: int, bit_order_lsb: bool) -> None:
    """
    Convert a draw buffer in I1 color format from htiled (row-wise) to vtiled
    (column-wise) buffer layout. The conversion assumes that the buffer width and height
    is rounded to a multiple of 8.
    
    Args:
        buf (None): pointer to the buffer to be converted
        buf_size (int): size of the buffer in bytes
        width (int): width of the buffer
        height (int): height of the buffer
        out_buf (None): pointer to the output buffer
        out_buf_size (int): size of the output buffer in bytes
        bit_order_lsb (bool): bit order of the resulting vtiled buffer
    
    
    C function: lv_draw_sw_i1_convert_to_vtiled
    Source: src/draw/sw/lv_draw_sw_utils.h:79
    """
    ...

def lv_draw_sw_rotate(src: None, dest: None, src_width: int, src_height: int, src_stride: int, dest_stride: int, rotation: int, color_format: int) -> None:
    """
    Rotate a buffer into another buffer
    
    Args:
        src (None): the source buffer
        dest (None): the destination buffer
        src_width (int): source width in pixels
        src_height (int): source height in pixels
        src_stride (int): source stride in bytes (number of bytes in a row)
        dest_stride (int): destination stride in bytes (number of bytes in a row)
        rotation (int): LV_DISPLAY_ROTATION_0/90/180/270
        color_format (int): LV_COLOR_FORMAT_RGB565/RGB888/XRGB8888/ARGB8888
    
    
    C function: lv_draw_sw_rotate
    Source: src/draw/sw/lv_draw_sw_utils.h:94
    """
    ...

def lv_theme_default_get() -> theme:
    ...

def lv_theme_default_is_inited() -> bool:
    ...

def lv_theme_default_deinit() -> None:
    ...

def lv_os_get_idle_percent() -> int:
    ...

def lv_draw_sw_mask_init() -> None:
    """
    ******************** GLOBAL PROTOTYPES *********************/
    
    
    C function: lv_draw_sw_mask_init
    Source: src/draw/sw/lv_draw_sw_mask.h:71
    """
    ...

def lv_draw_sw_mask_deinit() -> None:
    ...

def lv_draw_sw_mask_apply(masks: Any, mask_buf: None, abs_x: int, abs_y: int, len: int) -> int:
    """
    Apply the added buffers on a line. Used internally by the library's drawing routines.
    
    Args:
        masks (Any): the masks list to apply, must be ended with NULL pointer in array.
        mask_buf (None): store the result mask here. Has to be `len` byte long. Should be
                         initialized with `0xFF`.
        abs_x (int): absolute X coordinate where the line to calculate start
        abs_y (int): absolute Y coordinate where the line to calculate start
        len (int): length of the line to calculate (in pixel count)
    
    Returns:
        One of these values:
        - `LV_DRAW_MASK_RES_FULL_TRANSP`: the whole line is transparent. `mask_buf`
        is not set to zero
        - `LV_DRAW_MASK_RES_FULL_COVER`: the whole line is fully visible. `mask_buf`
        is unchanged
        - `LV_DRAW_MASK_RES_CHANGED`: `mask_buf` has changed, it shows the desired
        opacity of each pixel in the given line
    
    
    C function: lv_draw_sw_mask_apply
    Source: src/draw/sw/lv_draw_sw_mask.h:89
    """
    ...

def lv_draw_sw_mask_free_param(draw_buf: None) -> None:
    """
    Free the data from the parameter. It's called inside `lv_draw_sw_mask_remove_id` and
    `lv_draw_sw_mask_remove_custom` Needs to be called only in special cases when the
    mask is not added by `lv_draw_mask_add` and not removed by `lv_draw_mask_remove_id`
    or `lv_draw_mask_remove_custom`
    
    Args:
        draw_buf (None): Parameter description not available.
    
    
    C function: lv_draw_sw_mask_free_param
    Source: src/draw/sw/lv_draw_sw_mask.h:103
    """
    ...

def lv_draw_sw_init() -> None:
    """
    Initialize the SW renderer. Called in internally. It creates as many SW renderers as
    defined in LV_DRAW_SW_DRAW_UNIT_CNT
    
    
    C function: lv_draw_sw_init
    Source: src/draw/sw/lv_draw_sw.h:45
    """
    ...

def lv_draw_sw_deinit() -> None:
    """
    Deinitialize the SW renderers
    
    
    C function: lv_draw_sw_deinit
    Source: src/draw/sw/lv_draw_sw.h:50
    """
    ...

def lv_draw_sw_unregister_blend_handler(src_cf: int) -> bool:
    """
    Unregister a custom blend handler for a color format.
    
    Args:
        src_cf (int): Parameter description not available.
    
    Returns:
        true if a handler was unregistered, false if no handler was registered
    
    
    C function: lv_draw_sw_unregister_blend_handler
    Source: src/draw/sw/lv_draw_sw.h:175
    """
    ...

def lv_draw_sw_get_blend_handler(dest_cf: int) -> Any:
    """
    Get the blend handler for a color format.
    
    Args:
        dest_cf (int): color format
    
    Returns:
        pointer to the blend handler or NULL if no handler is registered
    
    
    C function: lv_draw_sw_get_blend_handler
    Source: src/draw/sw/lv_draw_sw.h:182
    """
    ...

def lv_timer_core_init() -> None:
    """
    Init the lv_timer module
    
    
    C function: lv_timer_core_init
    Source: src/misc/lv_timer_private.h:66
    """
    ...

def lv_timer_core_deinit() -> None:
    """
    Deinit the lv_timer module
    
    
    C function: lv_timer_core_deinit
    Source: src/misc/lv_timer_private.h:71
    """
    ...

def lv_anim_core_init() -> None:
    """
    Init the animation module
    
    
    C function: lv_anim_core_init
    Source: src/misc/lv_anim_private.h:41
    """
    ...

def lv_anim_core_deinit() -> None:
    """
    Deinit the animation module
    
    
    C function: lv_anim_core_deinit
    Source: src/misc/lv_anim_private.h:46
    """
    ...

def lv_draw_buf_init_handlers() -> None:
    """
    Called internally to initialize the draw_buf_handlers in lv_global
    
    
    C function: lv_draw_buf_init_handlers
    Source: src/draw/lv_draw_buf_private.h:43
    """
    ...

def lv_cache_entry_get_size(node_size: int) -> int:
    """
    Get the size of a cache entry.
    
    Args:
        node_size (int): The size of the node in the cache.
    
    Returns:
        The size of the cache entry.
    
    
    C function: lv_cache_entry_get_size
    Source: src/misc/cache/lv_cache_entry.h:35
    """
    ...

def lv_cache_entry_get_entry(data: None, node_size: int) -> cache_entry:
    """
    Get the cache entry of a data. The data should be allocated by the cache instance.
    
    Args:
        data (None): The data to get the cache entry of.
        node_size (int): The size of the node in the cache.
    
    Returns:
        The pointer to the cache entry of the data.
    
    
    C function: lv_cache_entry_get_entry
    Source: src/misc/cache/lv_cache_entry.h:78
    """
    ...

def lv_cache_entry_alloc(node_size: int, cache: cache) -> cache_entry:
    """
    Allocate a cache entry.
    
    Args:
        node_size (int): The size of the node in the cache.
        cache (cache): The cache instance to allocate the cache entry from.
    
    Returns:
        The pointer to the allocated cache entry.
    
    
    C function: lv_cache_entry_alloc
    Source: src/misc/cache/lv_cache_entry.h:86
    """
    ...

def lv_image_header_cache_init(size: int) -> int:
    """
    Initialize image header cache.
    
    Args:
        size (int): Parameter description not available.
    
    Returns:
        LV_RESULT_OK: initialization succeeded, LV_RESULT_INVALID: failed.
    
    
    C function: lv_image_header_cache_init
    Source: src/misc/cache/lv_image_header_cache.h:37
    """
    ...

def lv_image_header_cache_resize(new_size: int, evict_now: bool) -> None:
    """
    Resize image header cache. If set to 0, the cache is disabled.
    
    Args:
        new_size (int): Parameter description not available.
        evict_now (bool): true: evict the image headers should be removed by the eviction
                          policy, false: wait for the next cache cleanup.
    
    
    C function: lv_image_header_cache_resize
    Source: src/misc/cache/lv_image_header_cache.h:45
    """
    ...

def lv_image_header_cache_drop(src: None) -> None:
    """
    Invalidate image header cache. Use NULL to invalidate all image headers. It's also
    automatically called when an image is invalidated.
    
    Args:
        src (None): pointer to an image source.
    
    
    C function: lv_image_header_cache_drop
    Source: src/misc/cache/lv_image_header_cache.h:52
    """
    ...

def lv_image_header_cache_is_enabled() -> bool:
    """
    Return true if the image header cache is enabled.
    
    Returns:
        true: enabled, false: disabled.
    
    
    C function: lv_image_header_cache_is_enabled
    Source: src/misc/cache/lv_image_header_cache.h:58
    """
    ...

def lv_image_header_cache_iter_create() -> iter:
    """
    Create an iterator to iterate over the image header cache.
    
    Returns:
        an iterator to iterate over the image header cache.
    
    
    C function: lv_image_header_cache_iter_create
    Source: src/misc/cache/lv_image_header_cache.h:64
    """
    ...

def lv_image_header_cache_dump() -> None:
    """
    Dump the content of the image header cache in a human-readable format with cache
    order.
    
    
    C function: lv_image_header_cache_dump
    Source: src/misc/cache/lv_image_header_cache.h:69
    """
    ...

def lv_draw_sw_mask_cleanup() -> None:
    """
    Called by LVGL the rendering of a screen is ready to clean up the temporal (cache)
    data of the masks
    
    
    C function: lv_draw_sw_mask_cleanup
    Source: src/draw/sw/lv_draw_sw_mask_private.h:145
    """
    ...

def lv_layout_init() -> None:
    ...

def lv_layout_deinit() -> None:
    ...

def lv_text_get_next_line(txt: str, len: int, font: font, letter_space: int, max_width: int, used_width: None, flag: int) -> int:
    """
    Get the next line of text. Check line length and break chars too.
    
    Args:
        txt (str): a '\0' terminated string
        len (int): length of 'txt' in bytes
        font (font): pointer to a font
        letter_space (int): letter space
        max_width (int): max width of the text (break the lines to fit this size). Set
                         COORD_MAX to avoid line breaks
        used_width (None): When used_width != NULL, save the width of this line if flag
                           == LV_TEXT_FLAG_NONE, otherwise save -1.
        flag (int): settings for the text from 'txt_flag_type' enum
    
    Returns:
        the index of the first char of the new line (in byte index not letter index.
        With UTF-8 they are different)
    
    
    C function: lv_text_get_next_line
    Source: src/misc/lv_text_private.h:45
    """
    ...

def lv_text_ins(txt_buf: str, pos: int, ins_txt: str) -> None:
    """
    Insert a string into another
    
    Args:
        txt_buf (str): the original text (must be big enough for the result text and NULL
                       terminated)
        pos (int): position to insert (0: before the original text, 1: after the first
                   char etc.)
        ins_txt (str): text to insert, must be '\0' terminated
    
    
    C function: lv_text_ins
    Source: src/misc/lv_text_private.h:54
    """
    ...

def lv_text_cut(txt: str, pos: int, len: int) -> None:
    """
    Delete a part of a string
    
    Args:
        txt (str): string to modify, must be '\0' terminated and should point to a heap
                   or stack frame, not read-only memory.
        pos (int): position where to start the deleting (0: before the first char, 1:
                   after the first char etc.)
        len (int): number of characters to delete
    
    
    C function: lv_text_cut
    Source: src/misc/lv_text_private.h:63
    """
    ...

def lv_text_encoded_letter_next_2(txt: str, letter: None, letter_next: None, ofs: None) -> None:
    """
    Decode two encoded character from a string.
    
    Args:
        txt (str): pointer to '\0' terminated string
        letter (None): the first decoded Unicode character or 0 on invalid data code
        letter_next (None): the second decoded Unicode character or 0 on invalid data
                            code
        ofs (None): start index in 'txt' where to start. After the call it will point to
                    the next encoded char in 'txt'. NULL to use txt[0] as index
    
    
    C function: lv_text_encoded_letter_next_2
    Source: src/misc/lv_text_private.h:83
    """
    ...

def lv_image_decoder_init(image_cache_size: int, image_header_count: int) -> None:
    """
    Initialize the image decoder module
    
    Args:
        image_cache_size (int): Image cache size in bytes. 0 to disable cache.
        image_header_count (int): Number of header cache entries. 0 to disable header
                                  cache.
    
    
    C function: lv_image_decoder_init
    Source: src/draw/lv_image_decoder_private.h:129
    """
    ...

def lv_image_decoder_deinit() -> None:
    """
    Deinitialize the image decoder module
    
    
    C function: lv_image_decoder_deinit
    Source: src/draw/lv_image_decoder_private.h:134
    """
    ...

def lv_refr_init() -> None:
    """
    Initialize the screen refresh subsystem
    
    
    C function: lv_refr_init
    Source: src/core/lv_refr_private.h:34
    """
    ...

def lv_refr_deinit() -> None:
    """
    Deinitialize the screen refresh subsystem
    
    
    C function: lv_refr_deinit
    Source: src/core/lv_refr_private.h:39
    """
    ...

def lv_refr_get_disp_refreshing() -> display:
    """
    Get the display which is being refreshed
    
    Returns:
        the display being refreshed
    
    
    C function: lv_refr_get_disp_refreshing
    Source: src/core/lv_refr_private.h:53
    """
    ...

def lv_obj_style_init() -> None:
    """
    Initialize the object related style manager module. Called by LVGL in `lv_init()`
    
    
    C function: lv_obj_style_init
    Source: src/core/lv_obj_style_private.h:52
    """
    ...

def lv_obj_style_deinit() -> None:
    """
    Deinitialize the object related style manager module. Called by LVGL in `lv_deinit()`
    
    
    C function: lv_obj_style_deinit
    Source: src/core/lv_obj_style_private.h:58
    """
    ...

def lv_group_init() -> None:
    """
    Init the group module
    
    
    C function: lv_group_init
    Source: src/core/lv_group_private.h:59
    """
    ...

def lv_group_deinit() -> None:
    """
    Deinit the group module
    
    
    C function: lv_group_deinit
    Source: src/core/lv_group_private.h:65
    """
    ...

def lv_fs_init() -> None:
    """
    Initialize the File system interface
    
    
    C function: lv_fs_init
    Source: src/misc/lv_fs_private.h:48
    """
    ...

def lv_fs_deinit() -> None:
    """
    Deinitialize the File system interface
    
    
    C function: lv_fs_deinit
    Source: src/misc/lv_fs_private.h:53
    """
    ...

def lv_event_mark_deleted(draw_buf: None) -> None:
    """
    Nested events can be called and one of them might belong to an object that is being
    deleted. Mark this object's `event_temp_data` deleted to know that its
    `lv_obj_send_event` should return `LV_RESULT_INVALID`
    
    Args:
        draw_buf (None): Parameter description not available.
    
    
    C function: lv_event_mark_deleted
    Source: src/misc/lv_event_private.h:63
    """
    ...

def lv_os_init() -> None:
    ...

class LV_LOG_LEVEL:
    TRACE: int
    INFO: int
    WARN: int
    ERROR: int
    USER: int
    NONE: int

class LV_COORD:
    MAX: int
    MIN: int

class LV_OPA:
    TRANSP: int
    _0: int
    _10: int
    _20: int
    _30: int
    _40: int
    _50: int
    _60: int
    _70: int
    _80: int
    _90: int
    _100: int
    COVER: int

class LV_TREE_WALK:
    PRE_ORDER: int
    POST_ORDER: int

class LV_STR_SYMBOL:
    BULLET: int
    AUDIO: int
    VIDEO: int
    LIST: int
    OK: int
    CLOSE: int
    POWER: int
    SETTINGS: int
    HOME: int
    DOWNLOAD: int
    DRIVE: int
    REFRESH: int
    MUTE: int
    VOLUME_MID: int
    VOLUME_MAX: int
    IMAGE: int
    TINT: int
    PREV: int
    PLAY: int
    PAUSE: int
    STOP: int
    NEXT: int
    EJECT: int
    LEFT: int
    RIGHT: int
    PLUS: int
    MINUS: int
    EYE_OPEN: int
    EYE_CLOSE: int
    WARNING: int
    SHUFFLE: int
    UP: int
    DOWN: int
    LOOP: int
    DIRECTORY: int
    UPLOAD: int
    CALL: int
    CUT: int
    COPY: int
    SAVE: int
    BARS: int
    ENVELOPE: int
    CHARGE: int
    PASTE: int
    BELL: int
    KEYBOARD: int
    GPS: int
    FILE: int
    WIFI: int
    BATTERY_FULL: int
    BATTERY_3: int
    BATTERY_2: int
    BATTERY_1: int
    BATTERY_EMPTY: int
    USB: int
    BLUETOOTH: int
    TRASH: int
    EDIT: int
    BACKSPACE: int
    SD_CARD: int
    NEW_LINE: int
    DUMMY: int

class LV_STYLE:
    PROP_INV: int
    WIDTH: int
    HEIGHT: int
    LENGTH: int
    MIN_WIDTH: int
    MAX_WIDTH: int
    MIN_HEIGHT: int
    MAX_HEIGHT: int
    X: int
    Y: int
    ALIGN: int
    RADIUS: int
    RADIAL_OFFSET: int
    PAD_RADIAL: int
    PAD_TOP: int
    PAD_BOTTOM: int
    PAD_LEFT: int
    PAD_RIGHT: int
    PAD_ROW: int
    PAD_COLUMN: int
    LAYOUT: int
    MARGIN_TOP: int
    MARGIN_BOTTOM: int
    MARGIN_LEFT: int
    MARGIN_RIGHT: int
    BG_COLOR: int
    BG_OPA: int
    BG_GRAD_DIR: int
    BG_MAIN_STOP: int
    BG_GRAD_STOP: int
    BG_GRAD_COLOR: int
    BG_MAIN_OPA: int
    BG_GRAD_OPA: int
    BG_GRAD: int
    BASE_DIR: int
    BG_IMAGE_SRC: int
    BG_IMAGE_OPA: int
    BG_IMAGE_RECOLOR: int
    BG_IMAGE_RECOLOR_OPA: int
    BG_IMAGE_TILED: int
    CLIP_CORNER: int
    BORDER_WIDTH: int
    BORDER_COLOR: int
    BORDER_OPA: int
    BORDER_SIDE: int
    BORDER_POST: int
    OUTLINE_WIDTH: int
    OUTLINE_COLOR: int
    OUTLINE_OPA: int
    OUTLINE_PAD: int
    SHADOW_WIDTH: int
    SHADOW_COLOR: int
    SHADOW_OPA: int
    SHADOW_OFFSET_X: int
    SHADOW_OFFSET_Y: int
    SHADOW_SPREAD: int
    IMAGE_OPA: int
    IMAGE_RECOLOR: int
    IMAGE_RECOLOR_OPA: int
    LINE_WIDTH: int
    LINE_DASH_WIDTH: int
    LINE_DASH_GAP: int
    LINE_ROUNDED: int
    LINE_COLOR: int
    LINE_OPA: int
    ARC_WIDTH: int
    ARC_ROUNDED: int
    ARC_COLOR: int
    ARC_OPA: int
    ARC_IMAGE_SRC: int
    TEXT_COLOR: int
    TEXT_OPA: int
    TEXT_FONT: int
    TEXT_LETTER_SPACE: int
    TEXT_LINE_SPACE: int
    TEXT_DECOR: int
    TEXT_ALIGN: int
    OPA: int
    OPA_LAYERED: int
    COLOR_FILTER_DSC: int
    COLOR_FILTER_OPA: int
    ANIM: int
    ANIM_DURATION: int
    TRANSITION: int
    BLEND_MODE: int
    TRANSFORM_WIDTH: int
    TRANSFORM_HEIGHT: int
    TRANSLATE_X: int
    TRANSLATE_Y: int
    TRANSFORM_SCALE_X: int
    TRANSFORM_SCALE_Y: int
    TRANSFORM_ROTATION: int
    TRANSFORM_PIVOT_X: int
    TRANSFORM_PIVOT_Y: int
    TRANSFORM_SKEW_X: int
    TRANSFORM_SKEW_Y: int
    BITMAP_MASK_SRC: int
    ROTARY_SENSITIVITY: int
    TRANSLATE_RADIAL: int
    FLEX_FLOW: int
    FLEX_MAIN_PLACE: int
    FLEX_CROSS_PLACE: int
    FLEX_TRACK_PLACE: int
    FLEX_GROW: int
    GRID_COLUMN_ALIGN: int
    GRID_ROW_ALIGN: int
    GRID_ROW_DSC_ARRAY: int
    GRID_COLUMN_DSC_ARRAY: int
    GRID_CELL_COLUMN_POS: int
    GRID_CELL_COLUMN_SPAN: int
    GRID_CELL_X_ALIGN: int
    GRID_CELL_ROW_POS: int
    GRID_CELL_ROW_SPAN: int
    GRID_CELL_Y_ALIGN: int
    LAST_BUILT_IN_PROP: int
    NUM_BUILT_IN_PROPS: int
    PROP_ANY: int
    PROP_CONST: int

class LV_STATE:
    DEFAULT: int
    CHECKED: int
    FOCUSED: int
    FOCUS_KEY: int
    EDITED: int
    HOVERED: int
    PRESSED: int
    SCROLLED: int
    DISABLED: int
    USER_1: int
    USER_2: int
    USER_3: int
    USER_4: int
    ANY: int

class LV_PART:
    MAIN: int
    SCROLLBAR: int
    INDICATOR: int
    KNOB: int
    SELECTED: int
    ITEMS: int
    CURSOR: int
    CUSTOM_FIRST: int
    ANY: int

class LV_PART_TEXTAREA:
    PLACEHOLDER: int

class LV_RESULT:
    INVALID: int
    OK: int

class LV_RB_COLOR:
    RED: int
    BLACK: int

class LV_ALIGN:
    DEFAULT: int
    TOP_LEFT: int
    TOP_MID: int
    TOP_RIGHT: int
    BOTTOM_LEFT: int
    BOTTOM_MID: int
    BOTTOM_RIGHT: int
    LEFT_MID: int
    RIGHT_MID: int
    CENTER: int
    OUT_TOP_LEFT: int
    OUT_TOP_MID: int
    OUT_TOP_RIGHT: int
    OUT_BOTTOM_LEFT: int
    OUT_BOTTOM_MID: int
    OUT_BOTTOM_RIGHT: int
    OUT_LEFT_TOP: int
    OUT_LEFT_MID: int
    OUT_LEFT_BOTTOM: int
    OUT_RIGHT_TOP: int
    OUT_RIGHT_MID: int
    OUT_RIGHT_BOTTOM: int

class LV_DIR:
    NONE: int
    LEFT: int
    RIGHT: int
    TOP: int
    BOTTOM: int
    HOR: int
    VER: int
    ALL: int

class LV_COLOR_FORMAT:
    UNKNOWN: int
    RAW: int
    RAW_ALPHA: int
    L8: int
    I1: int
    I2: int
    I4: int
    I8: int
    A8: int
    RGB565: int
    ARGB8565: int
    RGB565A8: int
    AL88: int
    RGB888: int
    ARGB8888: int
    XRGB8888: int
    A1: int
    A2: int
    A4: int
    ARGB1555: int
    ARGB4444: int
    ARGB2222: int
    YUV_START: int
    I420: int
    I422: int
    I444: int
    I400: int
    NV21: int
    NV12: int
    YUY2: int
    UYVY: int
    YUV_END: int
    PROPRIETARY_START: int
    NEMA_TSC_START: int
    NEMA_TSC4: int
    NEMA_TSC6: int
    NEMA_TSC6A: int
    NEMA_TSC6AP: int
    NEMA_TSC12: int
    NEMA_TSC12A: int
    NEMA_TSC_END: int
    NATIVE: int
    NATIVE_WITH_ALPHA: int

class LV_PALETTE:
    RED: int
    PINK: int
    PURPLE: int
    DEEP_PURPLE: int
    INDIGO: int
    BLUE: int
    LIGHT_BLUE: int
    CYAN: int
    TEAL: int
    GREEN: int
    LIGHT_GREEN: int
    LIME: int
    YELLOW: int
    AMBER: int
    ORANGE: int
    DEEP_ORANGE: int
    BROWN: int
    BLUE_GREY: int
    GREY: int
    LAST: int
    NONE: int

class LV_IMAGE_FLAGS:
    PREMULTIPLIED: int
    COMPRESSED: int
    ALLOCATED: int
    MODIFIABLE: int
    CUSTOM_DRAW: int
    USER1: int
    USER2: int
    USER3: int
    USER4: int
    USER5: int
    USER6: int
    USER7: int
    USER8: int

class LV_IMAGE_COMPRESS:
    NONE: int
    RLE: int
    LZ4: int

class LV_FONT_GLYPH_FORMAT:
    NONE: int
    A1: int
    A2: int
    A3: int
    A4: int
    A8: int
    A1_ALIGNED: int
    A2_ALIGNED: int
    A4_ALIGNED: int
    A8_ALIGNED: int
    IMAGE: int
    VECTOR: int
    SVG: int
    CUSTOM: int

class LV_FONT_SUBPX:
    NONE: int
    HOR: int
    VER: int
    BOTH: int

class LV_FONT_KERNING:
    NORMAL: int
    NONE: int

class LV_TEXT_FLAG:
    NONE: int
    EXPAND: int
    FIT: int
    BREAK_ALL: int
    RECOLOR: int

class LV_TEXT_ALIGN:
    AUTO: int
    LEFT: int
    CENTER: int
    RIGHT: int

class LV_TEXT_CMD_STATE:
    WAIT: int
    PAR: int
    IN: int

class LV_BASE_DIR:
    LTR: int
    RTL: int
    AUTO: int
    NEUTRAL: int
    WEAK: int

class LV_GRAD_DIR:
    NONE: int
    VER: int
    HOR: int
    LINEAR: int
    RADIAL: int
    CONICAL: int

class LV_GRAD_EXTEND:
    PAD: int
    REPEAT: int
    REFLECT: int

class LV_LAYOUT:
    NONE: int
    FLEX: int
    GRID: int
    LAST: int

class LV_FLEX_ALIGN:
    START: int
    END: int
    CENTER: int
    SPACE_EVENLY: int
    SPACE_AROUND: int
    SPACE_BETWEEN: int

class LV_FLEX_FLOW:
    ROW: int
    COLUMN: int
    ROW_WRAP: int
    ROW_REVERSE: int
    ROW_WRAP_REVERSE: int
    COLUMN_WRAP: int
    COLUMN_REVERSE: int
    COLUMN_WRAP_REVERSE: int

class LV_GRID_ALIGN:
    START: int
    CENTER: int
    END: int
    STRETCH: int
    SPACE_EVENLY: int
    SPACE_AROUND: int
    SPACE_BETWEEN: int

class LV_BLEND_MODE:
    NORMAL: int
    ADDITIVE: int
    SUBTRACTIVE: int
    MULTIPLY: int
    DIFFERENCE: int

class LV_TEXT_DECOR:
    NONE: int
    UNDERLINE: int
    STRIKETHROUGH: int

class LV_BORDER_SIDE:
    NONE: int
    BOTTOM: int
    TOP: int
    LEFT: int
    RIGHT: int
    FULL: int
    INTERNAL: int

class LV_STYLE_RES:
    NOT_FOUND: int
    FOUND: int

class LV_EVENT:
    ALL: int
    PRESSED: int
    PRESSING: int
    PRESS_LOST: int
    SHORT_CLICKED: int
    SINGLE_CLICKED: int
    DOUBLE_CLICKED: int
    TRIPLE_CLICKED: int
    LONG_PRESSED: int
    LONG_PRESSED_REPEAT: int
    CLICKED: int
    RELEASED: int
    SCROLL_BEGIN: int
    SCROLL_THROW_BEGIN: int
    SCROLL_END: int
    SCROLL: int
    GESTURE: int
    KEY: int
    ROTARY: int
    FOCUSED: int
    DEFOCUSED: int
    LEAVE: int
    HIT_TEST: int
    INDEV_RESET: int
    HOVER_OVER: int
    HOVER_LEAVE: int
    COVER_CHECK: int
    REFR_EXT_DRAW_SIZE: int
    DRAW_MAIN_BEGIN: int
    DRAW_MAIN: int
    DRAW_MAIN_END: int
    DRAW_POST_BEGIN: int
    DRAW_POST: int
    DRAW_POST_END: int
    DRAW_TASK_ADDED: int
    VALUE_CHANGED: int
    INSERT: int
    REFRESH: int
    READY: int
    CANCEL: int
    CREATE: int
    DELETE: int
    CHILD_CHANGED: int
    CHILD_CREATED: int
    CHILD_DELETED: int
    SCREEN_UNLOAD_START: int
    SCREEN_LOAD_START: int
    SCREEN_LOADED: int
    SCREEN_UNLOADED: int
    SIZE_CHANGED: int
    STYLE_CHANGED: int
    LAYOUT_CHANGED: int
    GET_SELF_SIZE: int
    INVALIDATE_AREA: int
    RESOLUTION_CHANGED: int
    COLOR_FORMAT_CHANGED: int
    REFR_REQUEST: int
    REFR_START: int
    REFR_READY: int
    RENDER_START: int
    RENDER_READY: int
    FLUSH_START: int
    FLUSH_FINISH: int
    FLUSH_WAIT_START: int
    FLUSH_WAIT_FINISH: int
    VSYNC: int
    LAST: int
    PREPROCESS: int
    MARKED_DELETING: int

class LV_DISPLAY_ROTATION:
    _0: int
    _90: int
    _180: int
    _270: int

class LV_DISPLAY_RENDER_MODE:
    PARTIAL: int
    DIRECT: int
    FULL: int

class LV_SCR_LOAD_ANIM:
    NONE: int
    OVER_LEFT: int
    OVER_RIGHT: int
    OVER_TOP: int
    OVER_BOTTOM: int
    MOVE_LEFT: int
    MOVE_RIGHT: int
    MOVE_TOP: int
    MOVE_BOTTOM: int
    FADE_IN: int
    FADE_ON: int
    FADE_OUT: int
    OUT_LEFT: int
    OUT_RIGHT: int
    OUT_TOP: int
    OUT_BOTTOM: int

class LV_OBJ_TREE_WALK:
    NEXT: int
    SKIP_CHILDREN: int
    END: int

class LV_OBJ_POINT_TRANSFORM_FLAG:
    NONE: int
    RECURSIVE: int
    INVERSE: int
    INVERSE_RECURSIVE: int

class LV_SCROLLBAR_MODE:
    OFF: int
    ON: int
    ACTIVE: int
    AUTO: int

class LV_SCROLL_SNAP:
    NONE: int
    START: int
    END: int
    CENTER: int

class LV_STYLE_STATE_CMP:
    SAME: int
    DIFF_REDRAW: int
    DIFF_DRAW_PAD: int
    DIFF_LAYOUT: int

class LV_FS_RES:
    OK: int
    HW_ERR: int
    FS_ERR: int
    NOT_EX: int
    FULL: int
    LOCKED: int
    DENIED: int
    BUSY: int
    TOUT: int
    NOT_IMP: int
    OUT_OF_MEM: int
    INV_PARAM: int
    UNKNOWN: int

class LV_FS_MODE:
    WR: int
    RD: int

class LV_FS_SEEK:
    SET: int
    CUR: int
    END: int

class LV_IMAGE_SRC:
    VARIABLE: int
    FILE: int
    SYMBOL: int
    UNKNOWN: int

class LV_DRAW_TASK_TYPE:
    NONE: int
    FILL: int
    BORDER: int
    BOX_SHADOW: int
    LETTER: int
    LABEL: int
    IMAGE: int
    LAYER: int
    LINE: int
    ARC: int
    TRIANGLE: int
    MASK_RECTANGLE: int
    MASK_BITMAP: int
    VECTOR: int

class LV_DRAW_TASK_STATE:
    WAITING: int
    QUEUED: int
    IN_PROGRESS: int
    READY: int

class LV_LAYER_TYPE:
    NONE: int
    SIMPLE: int
    TRANSFORM: int

class LV_OBJ_CLASS_EDITABLE:
    INHERIT: int
    TRUE: int
    FALSE: int

class LV_OBJ_CLASS_GROUP_DEF:
    INHERIT: int
    TRUE: int
    FALSE: int

class LV_OBJ_CLASS_THEME_INHERITABLE:
    FALSE: int
    TRUE: int

class LV_KEY:
    UP: int
    DOWN: int
    RIGHT: int
    LEFT: int
    ESC: int
    DEL: int
    BACKSPACE: int
    ENTER: int
    NEXT: int
    PREV: int
    HOME: int
    END: int

class LV_GROUP_REFOCUS_POLICY:
    NEXT: int
    PREV: int

class LV_INDEV_TYPE:
    NONE: int
    POINTER: int
    KEYPAD: int
    BUTTON: int
    ENCODER: int

class LV_INDEV_STATE:
    RELEASED: int
    PRESSED: int

class LV_INDEV_MODE:
    NONE: int
    TIMER: int
    EVENT: int

class LV_INDEV_GESTURE:
    NONE: int
    PINCH: int
    SWIPE: int
    ROTATE: int
    TWO_FINGERS_SWIPE: int
    SCROLL: int
    CNT: int

class LV_COVER_RES:
    COVER: int
    NOT_COVER: int
    MASKED: int

class LV_OBJ_FLAG:
    HIDDEN: int
    CLICKABLE: int
    CLICK_FOCUSABLE: int
    CHECKABLE: int
    SCROLLABLE: int
    SCROLL_ELASTIC: int
    SCROLL_MOMENTUM: int
    SCROLL_ONE: int
    SCROLL_CHAIN_HOR: int
    SCROLL_CHAIN_VER: int
    SCROLL_CHAIN: int
    SCROLL_ON_FOCUS: int
    SCROLL_WITH_ARROW: int
    SNAPPABLE: int
    PRESS_LOCK: int
    EVENT_BUBBLE: int
    GESTURE_BUBBLE: int
    ADV_HITTEST: int
    IGNORE_LAYOUT: int
    FLOATING: int
    SEND_DRAW_TASK_EVENTS: int
    OVERFLOW_VISIBLE: int
    FLEX_IN_NEW_TRACK: int
    LAYOUT_1: int
    LAYOUT_2: int
    WIDGET_1: int
    WIDGET_2: int
    USER_1: int
    USER_2: int
    USER_3: int
    USER_4: int

class LV_FONT_FMT_TXT_CMAP:
    FORMAT0_FULL: int
    SPARSE_FULL: int
    FORMAT0_TINY: int
    SPARSE_TINY: int

class LV_FONT_FMT:
    TXT_PLAIN: int
    TXT_COMPRESSED: int
    TXT_COMPRESSED_NO_PREFILTER: int
    PLAIN_ALIGNED: int

class LV_IMAGE_ALIGN:
    DEFAULT: int
    TOP_LEFT: int
    TOP_MID: int
    TOP_RIGHT: int
    BOTTOM_LEFT: int
    BOTTOM_MID: int
    BOTTOM_RIGHT: int
    LEFT_MID: int
    RIGHT_MID: int
    CENTER: int
    AUTO_TRANSFORM: int
    STRETCH: int
    TILE: int

class LV_ANIM_IMAGE_PART:
    MAIN: int

class LV_ARC_MODE:
    NORMAL: int
    SYMMETRICAL: int
    REVERSE: int

class LV_LABEL_LONG_MODE:
    WRAP: int
    DOTS: int
    SCROLL: int
    SCROLL_CIRCULAR: int
    CLIP: int

class LV_BAR_MODE:
    NORMAL: int
    SYMMETRICAL: int
    RANGE: int

class LV_BAR_ORIENTATION:
    AUTO: int
    HORIZONTAL: int
    VERTICAL: int

class LV_BUTTONMATRIX_CTRL:
    NONE: int
    WIDTH_1: int
    WIDTH_2: int
    WIDTH_3: int
    WIDTH_4: int
    WIDTH_5: int
    WIDTH_6: int
    WIDTH_7: int
    WIDTH_8: int
    WIDTH_9: int
    WIDTH_10: int
    WIDTH_11: int
    WIDTH_12: int
    WIDTH_13: int
    WIDTH_14: int
    WIDTH_15: int
    HIDDEN: int
    NO_REPEAT: int
    DISABLED: int
    CHECKABLE: int
    CHECKED: int
    CLICK_TRIG: int
    POPOVER: int
    RECOLOR: int
    RESERVED_1: int
    RESERVED_2: int
    CUSTOM_1: int
    CUSTOM_2: int

class LV_CHART_TYPE:
    NONE: int
    LINE: int
    BAR: int
    SCATTER: int

class LV_CHART_UPDATE_MODE:
    SHIFT: int
    CIRCULAR: int

class LV_CHART_AXIS:
    PRIMARY_Y: int
    SECONDARY_Y: int
    PRIMARY_X: int
    SECONDARY_X: int
    LAST: int

class LV_IMAGEBUTTON_STATE:
    RELEASED: int
    PRESSED: int
    DISABLED: int
    CHECKED_RELEASED: int
    CHECKED_PRESSED: int
    CHECKED_DISABLED: int
    NUM: int

class LV_KEYBOARD_MODE:
    TEXT_LOWER: int
    TEXT_UPPER: int
    SPECIAL: int
    NUMBER: int
    USER_1: int
    USER_2: int
    USER_3: int
    USER_4: int

class LV_MENU_HEADER:
    TOP_FIXED: int
    TOP_UNFIXED: int
    BOTTOM_FIXED: int

class LV_MENU_ROOT_BACK_BUTTON:
    DISABLED: int
    ENABLED: int

class LV_ROLLER_MODE:
    NORMAL: int
    INFINITE: int

class LV_SCALE_MODE:
    HORIZONTAL_TOP: int
    HORIZONTAL_BOTTOM: int
    VERTICAL_LEFT: int
    VERTICAL_RIGHT: int
    ROUND_INNER: int
    ROUND_OUTER: int
    LAST: int

class LV_SLIDER_MODE:
    NORMAL: int
    SYMMETRICAL: int
    RANGE: int

class LV_SLIDER_ORIENTATION:
    AUTO: int
    HORIZONTAL: int
    VERTICAL: int

class LV_SPAN_OVERFLOW:
    CLIP: int
    ELLIPSIS: int
    LAST: int

class LV_SPAN_MODE:
    FIXED: int
    EXPAND: int
    BREAK: int
    LAST: int

class LV_SWITCH_ORIENTATION:
    AUTO: int
    HORIZONTAL: int
    VERTICAL: int

class LV_TABLE_CELL_CTRL:
    NONE: int
    MERGE_RIGHT: int
    TEXT_CROP: int
    CUSTOM_1: int
    CUSTOM_2: int
    CUSTOM_3: int
    CUSTOM_4: int

class LV_SUBJECT_TYPE:
    INVALID: int
    NONE: int
    INT: int
    POINTER: int
    COLOR: int
    GROUP: int
    STRING: int

class LV_THREAD_PRIO:
    LOWEST: int
    LOW: int
    MID: int
    HIGH: int
    HIGHEST: int

class LV_DRAW_SW_MASK_RES:
    TRANSP: int
    FULL_COVER: int
    CHANGED: int
    UNKNOWN: int

class LV_DRAW_SW_MASK_TYPE:
    LINE: int
    ANGLE: int
    RADIUS: int
    FADE: int
    MAP: int

class LV_DRAW_SW_MASK_LINE_SIDE:
    LEFT: int
    RIGHT: int
    TOP: int
    BOTTOM: int

class LV_CACHE_RESERVE_COND:
    OK: int
    TOO_LARGE: int
    NEED_VICTIM: int
    ERROR: int

# Integer constants
LV_DPI_DEF: int
LV_DRAW_BUF_STRIDE_ALIGN: int
LV_DRAW_BUF_ALIGN: int
LV_ANIM_REPEAT_INFINITE: int
LV_ANIM_PLAYTIME_INFINITE: int
LV_SIZE_CONTENT: int
LV_COLOR_DEPTH: int
LV_IMAGE_HEADER_MAGIC: int
LV_STRIDE_AUTO: int
LV_GRID_CONTENT: int
LV_GRID_TEMPLATE_LAST: int
LV_SCALE_NONE: int
LV_RADIUS_CIRCLE: int
LV_LABEL_DOT_NUM: int
LV_LABEL_POS_LAST: int
LV_LABEL_TEXT_SELECTION_OFF: int
LV_BUTTONMATRIX_BUTTON_NONE: int
LV_CHART_POINT_NONE: int
LV_DROPDOWN_POS_LAST: int
LV_SCALE_TOTAL_TICK_COUNT_DEFAULT: int
LV_SCALE_MAJOR_TICK_EVERY_DEFAULT: int
LV_SCALE_LABEL_ENABLED_DEFAULT: int
LV_SCALE_LABEL_ROTATE_MATCH_TICKS: int
LV_SCALE_LABEL_ROTATE_KEEP_UPRIGHT: int
LV_SCALE_ROTATION_ANGLE_MASK: int
LV_TEXTAREA_CURSOR_LAST: int
LV_TABLE_CELL_NONE: int

# Struct types
class C_Pointer:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_color_filter_dsc_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_color_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_tree_class_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_tree_node_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_font_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_font_glyph_dsc_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_font_glyph_dsc_gid_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_cache_entry_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_buf_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_image_header_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_buf_handlers_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_area_t:
    def __init__(self, *args, **kwargs) -> None: ...

class _lv_mp_int_wrapper:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_obj_class_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_obj_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_obj_spec_attr_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_group_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_ll_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_event_list_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_array_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_point_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_obj_style_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_style_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_event_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_cache_class_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_cache_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_cache_ops_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_iter_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_mem_monitor_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_timer_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_anim_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_anim_parameter_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_anim_bezier3_para_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_anim_timeline_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_rb_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_rb_node_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_point_precise_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_color32_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_color16_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_image_dsc_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_circle_buf_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_grad_dsc_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_grad_stop_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_style_transition_dsc_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_event_dsc_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_display_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_layer_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_task_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_unit_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_theme_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_fs_drv_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_fs_file_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_fs_file_cache_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_fs_path_ex_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_fs_dir_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_image_decoder_dsc_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_image_decoder_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_image_dsc_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_dsc_base_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_image_sup_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_image_decoder_args_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_rect_dsc_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_fill_dsc_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_border_dsc_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_box_shadow_dsc_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_letter_dsc_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_label_dsc_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_label_hint_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_glyph_dsc_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_line_dsc_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_arc_dsc_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_indev_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_indev_data_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_indev_pointer_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_indev_keypad_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_scale_section_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_span_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_subject_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_subject_value_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_observer_t:
    def __init__(self, *args, **kwargs) -> None: ...

class gd_GIF:
    def __init__(self, *args, **kwargs) -> None: ...

class gd_GCE:
    def __init__(self, *args, **kwargs) -> None: ...

class gd_Palette:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_triangle_dsc_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_sw_mask_line_param_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_sw_mask_common_dsc_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_sw_mask_line_param_cfg_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_sw_mask_angle_param_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_sw_mask_angle_param_cfg_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_sw_mask_radius_param_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_sw_mask_radius_param_cfg_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_sw_mask_radius_circle_dsc_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_sw_mask_fade_param_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_sw_mask_fade_param_cfg_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_sw_mask_map_param_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_sw_mask_map_param_cfg_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_sw_custom_blend_handler_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_sw_blend_dsc_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_mask_rect_dsc_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_color_hsv_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_matrix_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_style_value_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_calendar_date_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_chart_series_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_chart_cursor_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_span_coords_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_obj_style_transition_dsc_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_hit_test_info_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_image_cache_data_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_cache_slot_size_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_sqrt_res_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_global_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_layout_dsc_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_timer_state_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_anim_state_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_tick_state_t:
    def __init__(self, *args, **kwargs) -> None: ...

class lv_draw_global_info_t:
    def __init__(self, *args, **kwargs) -> None: ...
