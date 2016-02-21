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

import optparse

from .builder import Builder


def main():
    parser = optparse.OptionParser(__doc__)

    parser.add_option("-c", "--color-svg-dir", dest="color_svg_dir",
                      metavar="DIR", help="color SVG source directory")
    parser.add_option("--transform", dest="transform",
                      help="add a transform to the <svg> tag of each color SVG. \
                      Example \"translate(0 -800) scale(1.2)\"")

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

    builder = Builder(args[0], args[1], options)
    return builder.run()

if __name__ == '__main__':
    main()
