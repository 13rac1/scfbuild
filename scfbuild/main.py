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

"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse

from .builder import Builder


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("output", help="output font file")
    parser.add_argument("-g", "--glyph-dir", dest="glyph_svg_dir", metavar="DIR",
                        help="directory of regular no-color SVG glyphs to add to the font")
    parser.add_argument("-c", "--color-dir", dest="color_svg_dir", metavar="DIR",
                        help="directory of SVGinOT color SVG glyphs to add to the font.")
    parser.add_argument("--transform", dest="transform",
                        help="add a transform to the <svg> tag of each color SVG. "
                        "Example \"translate(0 -800) scale(1.2)\"")
    parser.add_argument("--familyname", dest="familyname", default="Untitled",
                        help="family name for the font. default: Untitled")
    parser.add_argument("--weight", dest="weight", default="Regular",
                        help="weight/syle for the font. default: Regular")
    parser.add_argument("--fullname", dest="fullname",
                        help="full name of the font. default: Family "
                        "Name + Weight(if not 'Regular')")
    parser.add_argument("--font-version", dest="version", default="1.0",
                        help="version number for the font. default: 1.0")

    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true",
                        default=False, help="print detailed debug information")

    # TODO: Options
    # -i --input - Input file instead of making a new one.
    # -t --type TTF/WOFF
    # --remove-unused
    # --version

    args = parser.parse_args()

    if not args.glyph_svg_dir:
        parser.error("--glyph-dir is required.")
        return 1
    if not args.color_svg_dir:
        parser.error("--color-dir is required.")
        return 1
    # TODO: Better Validation

    builder = Builder(args.glyph_svg_dir, args.output, args)
    return builder.run()

if __name__ == '__main__':
    main()
