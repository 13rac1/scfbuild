# -*- coding: utf-8 -*-
"""
Utility functions using FontForge
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import fontforge

from . import util


def create_font():

    font = fontforge.font()
    font.encoding = 'UnicodeFull'
    font.version = '1.0'
    font.weight = 'Regular'
    font.fontname = 'MyFont'
    font.familyname = 'MyFont'
    font.fullname = 'MyFont'
    font.em = 1000

    # Add required font characters
    icon = font.createChar(0x0000, 'NULL')
    icon.width = 250
    icon = font.createChar(0x000d, 'CR')
    icon.width = 250
    icon = font.createChar(0x0020, 'space')
    icon.width = 250

    return font


def add_svg_glyphs(font, svg_filepaths):
    for filepath in svg_filepaths:
        codepoint = util.codepoint_from_filepath(filepath)
        glyph = font.createChar(codepoint)
        glyph.importOutlines(filepath)

    return font
