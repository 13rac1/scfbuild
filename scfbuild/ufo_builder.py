# -*- coding: utf-8 -*-
# SCFBuild is released under the GNU General Public License v3.
# See LICENSE.txt in the project root directory.
"""
UFO-based font creation utilities to replace FontForge dependency
"""

import logging
from ufoLib2 import Font as UFOFont
from ufoLib2.objects import Glyph as UFOGlyph
from ufo2ft import compileTTF

from .util import FONT_EM, DEFAULT_GLYPH_WIDTH
from .unicode import ZWJ_INT, VS16_INT

logger = logging.getLogger(__name__)


def create_font(conf):
    """
    Create a UFO font with some default options, equivalent to fforge.create_font()
    """
    # Create a new UFO font
    font = UFOFont()

    # Set font info
    font.info.familyName = conf.get("family", "SCFBuild Font")
    font.info.styleName = conf.get("style", "Regular")

    # Set units per em (equivalent to font.em = FONT_EM)
    font.info.unitsPerEm = FONT_EM

    # Note: UFO fonts automatically create a "public.default" layer

    # Create basic glyphs required by OpenType specification
    _create_basic_glyphs(font, conf)

    # Set up ligature lookups
    _setup_ligature_lookups(font)

    logger.debug(
        "Created UFO font with family: %s, style: %s",
        font.info.familyName,
        font.info.styleName,
    )

    return font


def _create_basic_glyphs(font, conf):
    """
    Create basic glyphs required by the font (.notdef, .null, CR, space, ZWJ, VS16)
    """
    # Create .notdef glyph
    notdef_glyph = UFOGlyph(name=".notdef")
    notdef_glyph.width = 0
    font[".notdef"] = notdef_glyph

    # Create .null glyph
    null_glyph = UFOGlyph(name=".null")
    null_glyph.width = DEFAULT_GLYPH_WIDTH
    null_glyph.unicodes = [0x0]
    font[".null"] = null_glyph

    # Create CR glyph
    cr_glyph = UFOGlyph(name="CR")
    cr_glyph.width = DEFAULT_GLYPH_WIDTH
    cr_glyph.unicodes = [0xD]
    font["CR"] = cr_glyph

    # Create space glyph
    space_glyph = UFOGlyph(name="space")
    try:
        space_glyph.width = conf["width_space"]
    except KeyError:
        space_glyph.width = DEFAULT_GLYPH_WIDTH
    space_glyph.unicodes = [0x20]
    font["space"] = space_glyph
    logger.debug("Space character width: %d", space_glyph.width)

    # Create ZWJ glyph
    zwj_glyph = UFOGlyph(name="uni200D")
    zwj_glyph.width = 0
    zwj_glyph.unicodes = [ZWJ_INT]
    font["uni200D"] = zwj_glyph

    # Create VS16 glyph
    vs16_glyph = UFOGlyph(name="uniFE0F")
    vs16_glyph.width = 0
    vs16_glyph.unicodes = [VS16_INT]
    font["uniFE0F"] = vs16_glyph


def _setup_ligature_lookups(font):
    """
    Set up ligature lookup tables equivalent to FontForge setup
    """
    # TODO: Implement ligature setup using UFO's feature file approach
    # This will be handled in Phase 4 when we implement full ligature support
    pass


def compile_to_ttf(ufo_font):
    """
    Compile UFO font to TTF using ufo2ft
    Returns an in-memory TTFont object (no intermediate file I/O)
    """
    logger.info("Compiling UFO font to TTF")
    tt_font = compileTTF(ufo_font)
    logger.info("Font compilation complete")
    return tt_font


def add_glyphs(font, svg_filepaths, conf):
    """
    Add glyphs from SVG filepaths to the UFO font.
    This is a placeholder for Phase 3 implementation.
    """
    logger.warning("add_glyphs() not yet implemented - Phase 3 task")
    # TODO: Implement in Phase 3
    # This will handle:
    # - SVG import to UFO glyph outlines
    # - Glyph transformations
    # - Ligature glyph creation
    # - Glyph width calculations
    pass
