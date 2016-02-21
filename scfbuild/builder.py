# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import glob
import logging
import os
import sys
import tempfile

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.S_V_G_ import table_S_V_G_

from . import fforge
from . import ftools
from . import util

logger = logging.getLogger('smfbuilder.Builder')


class Builder(object):

    def run(self, glyph_svg_dir, output_file, options=None):

        ff_font = fforge.create_font()
        # Find and add regular glyphs
        svg_filepaths = self.get_svg_filepaths(glyph_svg_dir)
        fforge.add_glyphs(ff_font, svg_filepaths)

        tmp_dir = tempfile.mkdtemp()
        tmp_file = os.path.join(tmp_dir, "tmp.ttf")

        # TODO: Validate ligature tables to avoid warning during generate
        # "Lookup subtable contains unused glyph one making the whole subtable invalid"
        ff_font.generate(tmp_file)

        self.add_color_svg(
            tmp_file, options.color_svg_dir, output_file, options.transform)

        os.remove(tmp_file)
        os.rmdir(tmp_dir)

        # 0 for success
        return 0

    def add_color_svg(self, src_font, src_svg_path, dest_font, transform=None):

        font = TTFont(src_font)
        codepoint_names = ftools.get_codepoint_names(font)
        svg_filepaths = self.get_svg_filepaths(src_svg_path)
        svg_list = []

        for filepath in svg_filepaths:
            glyph_id = ftools.get_glyph_id(font, codepoint_names, filepath)

            data = self.read_file(filepath)
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

    def get_svg_filepaths(self, svg_dir):
        svg_files = []
        for filename in glob.glob(os.path.join(svg_dir, '*.svg')):
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

        return svg.replace(old, new)

    def add_transform(self, svg, transform):
        old = '<svg '
        new = '<svg transform="{}" '.format(transform)

        return svg.replace(old, new)
