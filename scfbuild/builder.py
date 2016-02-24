# -*- coding: utf-8 -*-

#    SCFBuild - SVGinOT Color Font Builder
#    Copyright (C) 2016 Brad Erickson
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import os
import sys
import tempfile
from distutils.version import StrictVersion

import fontTools
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.S_V_G_ import table_S_V_G_

from . import fforge
from . import util

__version__ = "1.0.0"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Support for SVG tables was added to fontTools in version 2.5
if StrictVersion('2.5') > StrictVersion(fontTools.version):
    logger.exception("The FontTools module version must be 2.5 or higher.")
    sys.exit(1)


class NoCodePointsException(Exception):
    pass


class Builder(object):

    def __init__(self, conf=None):
        self.conf = conf
        self.uids_for_glyph_names = None

        if self.conf['verbose']:
            logging.getLogger().setLevel(logging.DEBUG)

    def run(self):
        # TODO: Remove FontForge dependency?
        logger.info("Creating a new font")
        ff_font = fforge.create_font(self.conf)

        # Find and add regular glyphs
        svg_filepaths = util.get_svg_filepaths(self.conf['glyph_svg_dir'])
        # TODO: Validate regular SVGs
        logger.info("Adding glyphs and ligatures")
        fforge.add_glyphs(ff_font, svg_filepaths)

        tmp_dir = tempfile.mkdtemp()
        tmp_file = os.path.join(tmp_dir, "tmp.ttf")
        logger.debug("Using temp file: %s", tmp_file)

        # TODO: Validate ligature tables to avoid warning during generate
        # "Lookup subtable contains unused glyph NAME making the whole subtable invalid"
        logger.info("Generating intermediate font file")
        ff_font.generate(tmp_file)
        del ff_font

        logger.info("Reading intermediate font file")
        font = TTFont(tmp_file)
        logger.info("Adding SVGinOT SVG files")
        # TODO: Validate color SVGs
        self.add_color_svg(font)
        logger.info("Saving output file: %s", self.conf['output_file'])
        font.save(self.conf['output_file'])

        # Cleaning Up
        os.remove(tmp_file)
        os.rmdir(tmp_dir)

        logger.info("Done!")
        # 0 for success
        return 0

    def add_color_svg(self, font):
        svg_files = util.get_svg_filepaths(self.conf['color_svg_dir'])
        svg_list = []

        for filepath in svg_files:
            glyph_id = self.get_glyph_id(font, filepath)

            data = util.read_file(filepath)
            data = util.add_svg_glyph_id(data, glyph_id)
            if self.conf['color_svg_transform']:
                data = util.add_svg_transform(
                    data, self.conf['color_svg_transform'])

            logger.debug("Glyph ID: %d Adding SVG: %s", glyph_id, filepath)
            svg_list.append([data, glyph_id, glyph_id])

        svg_table = table_S_V_G_()
        # The SVG table must be sorted by glyph_id
        svg_table.docList = sorted(svg_list, key=lambda table: table[1])
        svg_table.colorPalettes = None
        font['SVG '] = svg_table

    def get_glyph_id(self, font, filepath):
        """
        Find a Glyph ID for the filename in filepath
        """
        if self.uids_for_glyph_names is None:
            self.uids_for_glyph_names = self.get_uids_for_glyph_names(font)

        (codepoint, filename) = util.codepoint_from_filepath(filepath)

        # Check for a regular glyph first
        try:
            glyph_name = self.uids_for_glyph_names[codepoint]
        except KeyError:
            # If that doesn't work check for a Ligature Glyph
            glyph_id = font.getGlyphID(filename)

            if glyph_id is -1:
                logger.warning("No Glyph ID found for: %s (Note: A regular "
                               "glyph is required for each color glyph)", filepath)

            logger.debug("Found Ligature Glyph: %s", filename)
            return glyph_id

        logger.debug("Found regular Glyph: %s", glyph_name)
        return font.getGlyphID(glyph_name)

    def get_uids_for_glyph_names(self, font):
        """
        Get a dict glyph names in the font indexed by unicode IDs
        """
        codepoints = {}
        for subtable in font['cmap'].tables:
            if subtable.isUnicode():
                for codepoint, name in subtable.cmap.items():
                    # NOTE: May overwrite previous values
                    codepoints[codepoint] = name
        if len(codepoints) is 0:
            raise NoCodePointsException(
                'No Unicode IDs/CodePoints found in font.')

        return codepoints
