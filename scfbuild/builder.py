# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import glob
import logging
import os
import sys

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.S_V_G_ import table_S_V_G_

from . import fforge
from . import ftools

logger = logging.getLogger('smfbuilder.Builder')


class Builder(object):

    def run(self, glyph_svg_dir, output_file, options=None):
        ff_font = fforge.create_font()
        # Find regular glyphs
        # Add regular glyphs
        # Save to tmp file
        # Open tmp file
        # Add SVGinOT glyphs
        # Save as output file.

    def add_color_svg(self, src_font, src_svg_path, dest_font, transform=None):

        font = TTFont(src_font)
        codepoint_names = ftools.get_codepoint_names(font)
        svg_filepaths = self.get_svg_filepaths(src_svg_path)
        svg_list = []

        for file_path in svg_filepaths:
            (filename, _) = os.path.splitext(os.path.basename(file_path))
            # Convert unicode filename to decimal.
            codepoint = int(filename, 16)
            try:
                glyph_name = codepoint_names[codepoint]
            except KeyError:
                print("WARNING: No Unicode Code Point found for: {}".format(
                    file_path), file=sys.stderr)
                continue

            glyph_id = font.getGlyphID(glyph_name)

            data = self.read_file(file_path)
            data = self.add_glyph_id(data, glyph_id)
            data = self.add_xml_header(data)
            if transform:
                data = self.add_transform(data, transform)

            svg_list.append([data, glyph_id, glyph_id])

        svg_table = table_S_V_G_()
        # The SVG table must be sorted by glyph_id
        svg_table.docList = sorted(svg_list, key=lambda table: table[1])
        svg_table.colorPalettes = None
        font['SVG '] = svg_table

        font.save(dest_font)

    def get_svg_filepaths(self, src_svg_dir):
        svg_files = []
        # Match all four and five character files only
        # TODO: Handle multi-character Unicode modifiers (colors and flags)
        # using Font Ligatures
        for filename in glob.glob(os.path.join(src_svg_dir, '????.svg')):
            svg_files.append(filename)
        for filename in glob.glob(os.path.join(src_svg_dir, '?????.svg')):
            svg_files.append(filename)

        return svg_files

    def read_file(self, file_path):
        f = open(file_path, "rt")
        data = f.read()
        f.close()
        return data

    def add_xml_header(self, svg):
        xml_header = '<?xml version="1.0" encoding="UTF-8"?>'

        if xml_header not in svg:
            svg = xml_header + svg
        return svg

    def add_glyph_id(self, svg, id):
        # TODO: Don't assume the glyph id is missing.
        old = '<svg '
        new = '<svg id="glyph{}" '.format(id)

        return str.replace(svg, old, new)

    def add_transform(self, svg, transform):
        old = '<svg '
        new = '<svg transform="{}" '.format(transform)

        return str.replace(svg, old, new)
