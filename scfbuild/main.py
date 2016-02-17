#!/usr/bin/env python2
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

"""\
SCFBuild - SVGinOT Color Font Builder

Builds multicolor fonts following the SVG in OpenType specification.

usage: %prog [OPTIONS] glyph_svg_dir output_file

Arguments:
  glyph_svg_dir         source directory for the primary/fallback single color
                        SVG glyphs
  output_file           output TTF file
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import glob
import optparse
import os
import sys
import logging
from distutils.version import StrictVersion

import fontforge
import fontTools
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.S_V_G_ import table_S_V_G_

# Support for SVG tables was added to fontTools in version 2.5
if StrictVersion('2.5') > StrictVersion(fontTools.version):
    print("ERROR: The FontTools module version must be 2.5 or higher.",
          file=sys.stderr)
    sys.exit(1)


class NoCodePointsException(Exception):
    pass


def main():
    parser = optparse.OptionParser(__doc__)

    parser.add_option("-c", "--color-svg-dir", dest="color_svg_dir", metavar="DIR",
                      help="color SVG source directory")
    parser.add_option("--transform", dest="transform",
                      help="add a transform to the <svg> tag of each color SVG")

    # TODO: Options
    # -i --input
    # -t --type TTF/WOFF
    # --remove-unused
    # -v --verbose
    # -q --quiet
    # --version
    # --font-version
    # --weight
    # --name
    # --familyname
    # --fullname

    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.error("glyph_svg_dir and output_file both are required.")
        return 1

    return run(args[0], args[1], options)


def run(glyph_svg_dir, output_file, options=None):
    print(glyph_svg_dir + output_file)


def svg_add_glyphs(src_font, src_svg_path, dest_font, transform=None):

    font = TTFont(src_font)
    codepoint_names = get_codepoint_names(font)
    svg_filepaths = get_svg_filepaths(src_svg_path)
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

        svg = read_file(file_path)
        svg = svg_add_glyph_id(svg, glyph_id)
        svg = svg_add_xml_header(svg)
        if transform:
            svg = svg_add_transform(svg, transform)

        svg_list.append([svg, glyph_id, glyph_id])

    svg_table = table_S_V_G_()
    # The SVG table must be sorted by glyph_id
    svg_table.docList = sorted(svg_list, key=lambda table: table[1])
    svg_table.colorPalettes = None
    font['SVG '] = svg_table

    font.save(dest_font)


def get_svg_filepaths(src_svg_dir):
    svg_files = []
    # Match all four and five character files only
    # TODO: Handle multi-character Unicode modifiers (colors and flags)
    # using Font Ligatures
    for filename in glob.glob(os.path.join(src_svg_dir, '????.svg')):
        svg_files.append(filename)
    for filename in glob.glob(os.path.join(src_svg_dir, '?????.svg')):
        svg_files.append(filename)

    return svg_files


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


def read_file(file_path):
    f = open(file_path, "rt")
    data = f.read()
    f.close()
    return data


def svg_add_glyph_id(svg, id):
    # TODO: Don't assume the glyph id is missing.
    old = '<svg '
    new = '<svg id="glyph{}" '.format(id)

    return str.replace(svg, old, new)


def svg_add_xml_header(svg):
    xml_header = '<?xml version="1.0" encoding="UTF-8"?>'

    if xml_header not in svg:
        svg = xml_header + svg
    return svg


def svg_add_transform(svg, transform):
    old = '<svg '
    new = '<svg transform="{}" '.format(transform)

    return str.replace(svg, old, new)

if __name__ == '__main__':
    main()
