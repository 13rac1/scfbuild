# -*- coding: utf-8 -*-
'''
Utility functions using FontForge
'''

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

    # Forcing strings to stop TypeError: Bad type for argument due to
    # unicode_literals
    liga = str('liga')
    latn = str('latn')
    dflt = str('dflt')
    feature_script_lang = ((liga, ((latn, (dflt)),)),)
    # Set up ligatures
    font.addLookup('liga', 'gsub_ligature', (), feature_script_lang)
    font.addLookupSubtable('liga', 'liga')

    # Add required font characters
    glyph = font.createChar(0x0000, 'NULL')
    glyph.width = 250
    glyph = font.createChar(0x000d, 'CR')
    glyph.width = 250

    return font


def add_svg_glyphs(font, svg_filepaths):
    for filepath in svg_filepaths:
        (codepoint, filename) = util.codepoint_from_filepath(filepath)

        if codepoint is -1:
            glyph = font.createChar(-1, filename)

            liga = get_liga_tuple(filename)
            # TODO: Add/check for standard ZJW alternatives
            glyph.addPosSub('liga', liga)

        else:
            glyph = font.createChar(codepoint)

        glyph.importOutlines(filepath)
        glyph.width = 1000

    return font


def get_liga_tuple(filename):
    # TODO: Support SVGs named by Glyph name
    liga = []
    for codepoint_str in filename.split("-"):
        codepoint = int(codepoint_str, 16)

        liga.append(fontforge.nameFromUnicode(codepoint))

    return tuple(liga)
