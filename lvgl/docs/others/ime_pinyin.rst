.. _ime_pinyin:

==========
Pinyin IME
==========

Pinyin IME provides API to provide Chinese Pinyin input method (Chinese
input) for keyboard object, which supports 26 key and 9 key input modes.
You can think of ``lv_ime_pinyin`` as a Pinyin input method plug-in for
keyboard objects.

Normally, an environment where :ref:`lv_keyboard` can
run can also run ``lv_ime_pinyin``. There are two main influencing
factors: the size of the font file and the size of the dictionary.

.. _ime_pinyin_example:

Usage
-----

Enable :c:macro:`LV_USE_IME_PINYIN` in ``lv_conf.h``.

First use :cpp:expr:`lv_ime_pinyin_create(lv_screen_active())` to create a Pinyin
input method plug-in, then use
:cpp:expr:`lv_ime_pinyin_set_keyboard(pinyin_ime, kb)` to add the ``keyboard``
you created to the Pinyin input method plug-in. You can use
:cpp:expr:`lv_ime_pinyin_set_dict(pinyin_ime, your_dict)` to use a custom
dictionary (if you don't want to use the built-in dictionary at first,
you can disable :c:macro:`LV_IME_PINYIN_USE_DEFAULT_DICT` in ``lv_conf.h``,
which can save a lot of memory space).

The built-in thesaurus is customized based on the
**LV_FONT_SIMSUN_16_CJK** font library, which currently only has more
than ``1,000`` most common CJK radicals, so it is recommended to use
custom fonts and thesaurus.

In the process of using the Pinyin input method plug-in, you can change
the keyboard and dictionary at any time.

Custom dictionary
-----------------

If you don't want to use the built-in Pinyin dictionary, you can use the
custom dictionary. Or if you think that the built-in phonetic dictionary
consumes a lot of memory, you can also use a custom dictionary.

Customizing the dictionary is very simple.

First, set :c:macro:`LV_IME_PINYIN_USE_DEFAULT_DICT` to ``0`` in ``lv_conf.h``

Then, write a dictionary in the following format.


Dictionary format
~~~~~~~~~~~~~~~~~

The arrangement order of each pinyin syllable is very important. You
need to customize your own thesaurus according to the Hanyu Pinyin
syllable table. You can read
`here <https://baike.baidu.com/item/%E6%B1%89%E8%AF%AD%E6%8B%BC%E9%9F%B3%E9%9F%B3%E8%8A%82/9167981>`__
to learn about the Hanyu Pinyin syllables and the syllable table.

Then, write your own dictionary according to the following format:

.. code:: c

   lv_100ask_pinyin_dict_t your_pinyin_dict[] = {
               { "a", "啊阿呵吖" },
               { "ai", "埃挨哎唉哀皑蔼矮碍爱隘癌艾" },
               { "an", "按安暗岸俺案鞍氨胺厂广庵揞犴铵桉谙鹌埯黯" },
               { "ang", "昂肮盎仰" },
               { "ao", "凹敖熬翱袄傲奥懊澳" },
               { "ba", "芭捌叭吧笆八疤巴拔跋靶把坝霸罢爸扒耙" },
               { "bai", "白摆佰败拜柏百稗伯" },
               /* ...... */
               { "zuo", "昨左佐做作坐座撮琢柞"},
               {NULL, NULL}

**The last item** must end with ``{null, null}``, or it will not work
properly.

.. _ime_pinyin_apply_new_dictionary:

Apply new dictionary
~~~~~~~~~~~~~~~~~~~~

After writing a dictionary according to the above dictionary format, you
only need to call this function to set up and use your dictionary:

.. code:: c

       lv_obj_t * pinyin_ime = lv_100ask_pinyin_ime_create(lv_screen_active());
       lv_100ask_pinyin_ime_set_dict(pinyin_ime, your_pinyin_dict);

.. _ime_pinyin_modes:

Modes
-----

The lv_ime_pinyin have the following modes:

-  :cpp:enumerator:`LV_IME_PINYIN_MODE_K26`: Pinyin 26 key input mode
-  :cpp:enumerator:`LV_IME_PINYIN_MODE_K9`: Pinyin 9 key input mode
-  :cpp:enumerator:`LV_IME_PINYIN_MODE_K9_NUMBER`: Numeric keypad mode

The ``TEXT`` modes' layout contains buttons to change mode.

To set the mode manually, use :cpp:expr:`lv_ime_pinyin_set_mode(pinyin_ime, mode)`.
The default mode is :cpp:enumerator:`LV_IME_PINYIN_MODE_K26`.

.. _ime_pinyin_example:

Example
-------

.. include:: ../examples/others/ime/index.rst

.. _ime_pinyin_api:

API
---

