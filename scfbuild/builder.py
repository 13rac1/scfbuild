# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import glob
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

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Support for SVG tables was added to fontTools in version 2.5
if StrictVersion('2.5') > StrictVersion(fontTools.version):
    logger.exception("The FontTools module version must be 2.5 or higher.")
    sys.exit(1)


class NoCodePointsException(Exception):
    pass


class Builder(object):

    def __init__(self, glyph_svg_dir, output_file, options=None):
        self.glyph_svg_dir = glyph_svg_dir
        self.output_file = output_file
        self.options = options

    def run(self):

        logger.info("Creating a new font")
        ff_font = fforge.create_font()

        # Find and add regular glyphs
        svg_filepaths = self.get_svg_filepaths(self.glyph_svg_dir)
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

        logger.info("Adding SVGinOT SVG files")
        font = TTFont(tmp_file)
        self.add_color_svg(font)
        logger.info("Saving output file: %s", self.output_file)
        font.save(self.output_file)

        # Cleaning Up
        os.remove(tmp_file)
        os.rmdir(tmp_dir)

        logger.info("Done!")
        # 0 for success
        return 0

    def add_color_svg(self, font):
        # Get the name
        codepoint_names = self.get_codepoint_names(font)
        svg_files = self.get_svg_filepaths(self.options.color_svg_dir)
        svg_list = []

        for filepath in svg_files:
            glyph_id = self.get_glyph_id(font, codepoint_names, filepath)

            data = self.read_file(filepath)
            data = self.add_glyph_id(data, glyph_id)
            if self.options.transform:
                data = self.add_transform(data, self.options.transform)

            svg_list.append([data, glyph_id, glyph_id])

        svg_table = table_S_V_G_()
        # The SVG table must be sorted by glyph_id
        svg_table.docList = sorted(svg_list, key=lambda table: table[1])
        svg_table.colorPalettes = None
        font['SVG '] = svg_table

    def get_codepoint_names(self, font):
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

    def get_glyph_id(self, font, codepoint_names, filepath):
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

    def get_svg_filepaths(self, svg_dir):
        return [filename for filename in glob.glob(os.path.join(svg_dir, '*.svg'))]

    def read_file(self, file_path):
        f = open(file_path, "rt")
        data = f.read()
        f.close()
        return data

    def add_glyph_id(self, svg, id):
        # TODO: Don't assume the glyph id is missing.
        old = '<svg '
        new = '<svg id="glyph{}" '.format(id)

        return svg.replace(old, new)

    def add_transform(self, svg, transform):
        old = '<svg '
        new = '<svg transform="{}" '.format(transform)

        return svg.replace(old, new)
