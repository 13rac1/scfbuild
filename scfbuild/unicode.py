# -*- coding: utf-8 -*-
# SCFBuild is released under the GNU General Public License v3.
# See LICENSE.txt in the project root directory.

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

# ZERO WIDTH JOINER (ZWJ)
ZWJ_INT = 0x200d
ZWJ = '\u200d'
# VARIATION SELECTOR-16 - Used as emoji variation selector.
VS16_INT = 0xfe0f
VS16 = '\ufe0f'

# A list of all ZWJ indexed by the no ZJW/EVS sequence.
# Details: http://unicode.org/emoji/charts/emoji-zwj-sequences.html
# Emoji variation selectors are included, ligatures should make them optional.
# Uses 'U' instead of 'u' to allow 8 digit unicode literals
ZWJ_SEQUENCES = {
    # Sequences for ‍kiss: 💏
    # kiss: woman, man
    "\U0001f469\u2764\U0001f48b\U0001f468": "\U0001f469\u200d\u2764\ufe0f\u200d\U0001f48b\u200d\U0001f468",
    # kiss: man, man
    "\U0001f468\u2764\U0001f48b\U0001f468": "\U0001f468\u200d\u2764\ufe0f\u200d\U0001f48b\u200d\U0001f468",
    # kiss: woman, woman
    "\U0001f469\u2764\U0001f48b\U0001f469": "\U0001f469\u200d\u2764\ufe0f\u200d\U0001f48b\u200d\U0001f469",
    # Sequences for couple with heart: 💑
    # couple with heart: woman, man
    "\U0001f469\u2764\U0001f468": "\U0001f469\u200d\u2764\ufe0f\u200d\U0001f468",
    # couple with heart: man, man
    "\U0001f468\u2764\U0001f468": "\U0001f468\u200d\u2764\ufe0f\u200d\U0001f468",
    # couple with heart: woman, woman
    "\U0001f469\u2764\U0001f469": "\U0001f469\u200d\u2764\ufe0f\u200d\U0001f469",
    # Sequences for family: ‍👪
    # family: man, woman, boy
    "\U0001f468\U0001f469\U0001f466": "\U0001f468\u200d\U0001f469\u200d\U0001f466",
    # family: man, woman, girl
    "\U0001f468\U0001f469\U0001f467": "\U0001f468\u200d\U0001f469\u200d\U0001f467",
    # family: man, woman, girl, boy
    "\U0001f468\U0001f469\U0001f467\U0001f466": "\U0001f468\u200d\U0001f469\u200d\U0001f467\u200d\U0001f466",
    # family: man, woman, boy, boy
    "\U0001f468\U0001f469\U0001f466\U0001f466": "\U0001f468\u200d\U0001f469\u200d\U0001f466\u200d\U0001f466",
    # family: man, woman, girl, girl
    "\U0001f468\U0001f469\U0001f467\U0001f467": "\U0001f468\u200d\U0001f469\u200d\U0001f467\u200d\U0001f467",
    # family: man, man, boy
    "\U0001f468\U0001f468\U0001f466": "\U0001f468\u200d\U0001f468\u200d\U0001f466",
    # family: man, man, girl
    "\U0001f468\U0001f468\U0001f467": "\U0001f468\u200d\U0001f468\u200d\U0001f467",
    # family: man, man, girl, boy
    "\U0001f468\U0001f468\U0001f467\U0001f466": "\U0001f468\u200d\U0001f468\u200d\U0001f467\u200d\U0001f466",
    # family: man, man, boy, boy
    "\U0001f468\U0001f468\U0001f466\U0001f466": "\U0001f468\u200d\U0001f468\u200d\U0001f466\u200d\U0001f466",
    # family: man, man, girl, girl
    "\U0001f468\U0001f468\U0001f467\U0001f467": "\U0001f468\u200d\U0001f468\u200d\U0001f467\u200d\U0001f467",
    # family: man, man, girl, girl
    "\U0001f469\U0001f469\U0001f466": "\U0001f469\u200d\U0001f469\u200d\U0001f466",
    # family: woman, woman, girl
    "\U0001f469\U0001f469\U0001f467": "\U0001f469\u200d\U0001f469\u200d\U0001f467",
    # family: woman, woman, girl, boy
    "\U0001f469\U0001f469\U0001f467\U0001f466": "\U0001f469\u200d\U0001f469\u200d\U0001f467\u200d\U0001f466",
    # family: woman, woman, boy, boy
    "\U0001f469\U0001f469\U0001f466\U0001f466": "\U0001f469\u200d\U0001f469\u200d\U0001f466\u200d\U0001f466",
    # family: woman, woman, girl, girl
    "\U0001f469\U0001f469\U0001f467\U0001f467": "\U0001f469\u200d\U0001f469\u200d\U0001f467\u200d\U0001f467",
    # eye, left speech bubble: 👁‍🗨
    "\U0001f441\U0001f5e8": "\U0001f441\u200d\U0001f5e8",
}
