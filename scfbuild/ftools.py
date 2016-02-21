# -*- coding: utf-8 -*-
"""
Utility functions using fontTools
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys

import fontTools as fonttools


from . import util


def get_codepoint_names(font):
    codepoints = {}
    for subtable in font['cmap'].tables:
        if subtable.isUnicode():
            for codepoint, name in subtable.cmap.items():
                # NOTE: May overwrite previous values
                codepoints[codepoint] = name
    if len(codepoints) is 0:
        raise NoCodePointsException(
            'No Unicode Code Points found in font.')

    return codepoints


def get_glyph_id(font, codepoint_names, filepath):
    (codepoint, filename) = util.codepoint_from_filepath(filepath)

    try:
        glyph_name = codepoint_names[codepoint]
    except KeyError:
        glyph_id = font.getGlyphID(filename)

        if glyph_id is -1:
            print("WARNING: No Unicode Code Point found for: {}".format(
                filename), file=sys.stderr)
        return glyph_id

    return font.getGlyphID(glyph_name)
