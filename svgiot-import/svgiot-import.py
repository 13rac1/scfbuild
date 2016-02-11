#!/usr/bin/env python3

"""
SVG in OpenType Importer
for SymbolaEmojiOne font
TODO: Make it work for any font
Copyright 2016 Brad Erickson (eosrei)

Overall functionality:
1. Get a list of all SVG files representing *single* unicode character emojis.
2. Match SVG name to GlyphID using cmap table, warning on missing glyphs; SVGiOT spec requires both. 
3. Apply transform to SVG XML to match font
4. Add Glyph ID to SVG XML
5. Create 'SVG ' table in font and export to output_font

NOTE: Firefox requires restart to reload an updated font.
"""

from distutils.version import StrictVersion
from fontTools import version
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.S_V_G_ import table_S_V_G_
import glob
from operator import itemgetter
import optparse
import os
import sys


VERSION = '0.1'

# Support for SVG tables was added to fontTools in version 2.5
min_fonttools_version = '2.5'
if StrictVersion(min_fonttools_version) > StrictVersion(version):
    print(
        "ERROR: The FontTools module version must be 2.5 or higher.", file=sys.stderr)
    sys.exit(1)


class NoCodePointsException(Exception):
    pass


class SVGiOTImport:

    def __init__(self, src_font, src_svg_path, dest_font):

        font = TTFont(src_font)
        codepoint_names = self.get_codepoint_names(font)
        svg_filepaths = self.get_svg_filepaths(src_svg_path)
        svg_list = []

        for file_path in svg_filepaths:
            (filename, _) = os.path.splitext(os.path.basename(file_path))
            # Convert unicode filename to decimal.
            codepoint = int(filename, 16)
            print("Current: " + filename)
            try:
                glyph_name = codepoint_names[codepoint]
            except KeyError:
                print("WARNING: No codepoint found for: {}".format(
                    file_path), file=sys.stderr)
                continue

            glyph_id = font.getGlyphID(glyph_name)

            svg = self.read_file(file_path)
            svg = self.svg_add_glyph_id(svg, glyph_id)
            svg = self.svg_add_xml_header(svg)

            svg_list.append([svg, glyph_id, glyph_id])

        svg_table = table_S_V_G_()
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

    def read_file(self, file_path):
        f = open(file_path, "rt")
        data = f.read()
        f.close()
        return data

    def svg_add_glyph_id(self, svg, id):
        # TODO: Don't assume the glyph id is missing.
        old = '<svg '
        new = '<svg id="glyph{}" '.format(id)

        return str.replace(svg, old, new)

    def svg_add_xml_head(self, svg):
        # TODO: Check if it's there first.
        svg = '<?xml version="1.0" encoding="UTF-8"?>' + svg


def main():
    parser = optparse.OptionParser(
        "usage: %prog src_font src_svg_directory dest_font")

    # TODO: Option - Remove all glyphs not matched with SVG.
    # TODO: Option - Apply transform all SVG files.

    (options, args) = parser.parse_args()

    if len(args) != 3:
        parser.error("Incorrect number of arguments")

    SVGiOTImport(args[0], args[1], args[2])


if __name__ == "__main__":
    main()
