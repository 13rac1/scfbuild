#!/usr/bin/env python3

"""
SVG in OpenType Importer
for SymbolaEmojiOne font
TODO: Make it work for any font
Copyright 2016 Brad Erickson (eosrei)

Overall functionality:
1. Get a list of all SVG files representing *single* unicode character emojis.
2. Match SVG name to GlyphID using cmap table, warning on missing glyphs; SVGiOT spec requires both. 
3. Export available character glyphs from the input_font for each SVG. 
4. Apply transform to SVG XML to match font
5. Add Glyph ID to SVG XML
6. Create 'SVG ' table in font and export to output_font 
 
"""

import os
import optparse
import glob

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.S_V_G_ import table_S_V_G_
from os.path import basename


def main(src_font, src_svg_dir, dest_font):
    
    svg_files = get_svg_filenames(src_svg_dir)   
    # TODO: File exists error checking.
    
    font = TTFont(src_font)
    # TODO: Drop extra tables
        
    #glyph_order = font.getGlyphOrder()
    #for glyphID in range(len(glyph_order)):
    #    print(font.getGlyphName(glyphID))

    svg = '<?xml version="1.0" encoding="UTF-8"?><svg id="glyph2392" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" enable-background="new 0 0 64 64"><circle fill="#ffdd67" cx="32" cy="32" r="30"/><g fill="#664e27"><circle cx="20.5" cy="25.592" r="4.5"/><circle cx="43.5" cy="25.592" r="4.5"/><path d="m52.891 34.5c-.686 4.537-3.387 8.824-7.248 11.754-1.934 1.463-4.166 2.555-6.498 3.244-2.344.701-4.73.99-7.172 1-4.705.027-9.746-1.283-13.621-4.24-3.863-2.928-6.564-7.221-7.242-11.76 2.256 3.938 5.359 7.107 8.975 9.135 3.627 2.049 7.705 2.865 11.941 2.867 4.131.004 8.287-.814 11.891-2.863 3.616-2.028 6.72-5.201 8.974-9.139"/></g></svg>'
    
    table_svg = table_S_V_G_()
    table_svg.docList = []
    table_svg.colorPalettes = None
    table_svg.docList.append([svg,2392,2392])
    font['SVG '] = table_svg
    
    font.save(dest_font)

def get_svg_filenames(src_svg_dir):
    svg_files = []
    # Match all four and five character files only
    # TODO: Handle multi-character Unicode modifiers (colors and flags)
    for filename in glob.glob(src_svg_dir + '/????.svg'):        
        svg_files.append(filename)
    for filename in glob.glob(src_svg_dir + '/?????.svg'):        
        svg_files.append(filename)
        
    return svg_files

if __name__ == "__main__":
    parser = optparse.OptionParser("usage: %prog src_font src_svg_directory dest_font")
    
    (options, args) = parser.parse_args()
    
    if len(args) != 3:
        parser.error("Incorrect number of arguments")
    
    main(args[0], args[1], args[2])

