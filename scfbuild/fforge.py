# -*- coding: utf-8 -*-
'''
Utility functions using FontForge
'''

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import logging

import fontforge

from . import util
from .unicode import ZWJ_INT, VS16_INT, ZWJ_SEQUENCES

logger = logging.getLogger(__name__)


def create_font():
    """
    Create font with some default options
    """

    font = fontforge.font()
    font.encoding = 'UnicodeFull'
    font.version = '1.0'
    font.weight = 'Regular'
    font.fontname = 'MyFont'
    font.familyname = 'MyFont'
    font.fullname = 'MyFont'
    font.em = 1000

    # TODO: Make ligatures optional
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
    glyph.width = 0
    glyph = font.createChar(0x000d, 'CR')
    glyph.width = 250
    glyph = font.createChar(ZWJ_INT)
    glyph.width = 0
    glyph = font.createChar(VS16_INT)
    glyph.width = 0

    return font


def add_glyphs(font, svg_filepaths):
    """
    Loop through all files and create regular or ligature glyphs for each.
    """
    for filepath in svg_filepaths:
        (codepoint, filename) = util.codepoint_from_filepath(filepath)

        # If code point is -1, then the final name is not a simple unicode id
        # so make a glyph for use with ligatures
        if codepoint is -1:
            # Example: 1f441-1f5e8.svg

            # Create a gylph without a defined code point
            glyph = font.createChar(-1, filename)
            logger.debug("Creating ligature glyph %s", filename)

            # Creates a list of Unicode IDs from a string of hyphen separated
            # Unicode IDs.
            u_ids = [int(id, 16) for id in filename.split("-")]
            # Example: (0x1f441, 0x1f5e8)

            u_str = ''.join(map(unichr, u_ids))
            # Example: "U\0001f441U\0001f5e8"

            # Replace sequences with correct ZWJ/VS16 versions as needed
            try:
                u_str = ZWJ_SEQUENCES[u_str]
                u_ids = map(ord, u_str)
            except KeyError:
                pass

            # Create a tuple of glyph names
            liga_glyphs = tuple(map(fontforge.nameFromUnicode, u_ids))
            # Add the new ligature to the glyph
            glyph.addPosSub('liga', liga_glyphs)
            logger.debug("Adding substitution %s", liga_glyphs)

            if VS16_INT in u_ids:
                # Create a list of IDs without the emoji variation selector.
                u_ids = [id for id in u_ids if id != VS16_INT]
                liga_glyphs = tuple(map(fontforge.nameFromUnicode, u_ids))
                glyph.addPosSub('liga', liga_glyphs)
                logger.debug("Adding substitution %s", liga_glyphs)

        else:
            # Normal single character glyph
            # Example: 1f914.svg
            glyph = font.createChar(codepoint)
            logger.debug("Creating glyph at 0x%x for %s", codepoint, filepath)

        glyph.importOutlines(filepath)
        # Set the width of the glyph, assuming everything is the same for now.
        glyph.width = 1000

    return font
