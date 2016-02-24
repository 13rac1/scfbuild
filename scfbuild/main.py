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

'''\
SCFBuild - SVGinOT Color Font Builder
'''

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import yaml

from .builder import Builder


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('-o', '--output',
                        dest='output',
                        help='output font file')
    parser.add_argument('-g', '--glyph-svg-dir',
                        dest='glyph_svg_dir',
                        metavar='DIR',
                        help='directory of regular no-color SVG glyphs to add to the font')
    parser.add_argument('-s', '--color-svg-dir',
                        dest='color_svg_dir',
                        metavar='DIR',
                        help='directory of SVGinOT color SVG glyphs to add to the font.')
    parser.add_argument('--transform',
                        dest='transform',
                        help='add a transform to the <svg> tag of each color SVG. '
                        'Example "translate(0 -1638) scale(2.048)"')
    default_family = 'Untitled'
    parser.add_argument('--font-family',
                        dest='family',
                        default=default_family,
                        help='family name for the font. default: ' + default_family)
    default_subfamily = 'Regular'
    parser.add_argument('--font-subfamily',
                        dest='subfamily',
                        default=default_subfamily,
                        help='weight/style for the font. default: ' + default_subfamily)
    default_version = '1.0'
    parser.add_argument('--font-version',
                        dest='version',
                        default=default_version,
                        help='version number for the font. default: ' + default_version)
    parser.add_argument('-c', '--yaml-conf',
                        dest='yaml_conf',
                        help='yaml build configuration, overridden by command '
                        'line options.')
    parser.add_argument('-v', '--verbose',
                        dest='verbose',
                        action='store_true',
                        default=False,
                        help='print detailed debug information')

    # TODO: Options
    # -i --input - Input file instead of making a new one.
    # -t --type TTF/WOFF
    # --remove-unused
    # --version

    args = parser.parse_args()

    # Load the YAML config if it is available
    if args.yaml_conf:
        f = open(args.yaml_conf)
        conf = yaml.safe_load(f)
        f.close()
    else:
        conf = {}

    if 'table_name' not in conf:
        conf['table_name'] = {}

    # Command line options override YAML
    if args.output:
        conf['output_file'] = args.output
    if args.glyph_svg_dir:
        conf['glyph_svg_dir'] = args.glyph_svg_dir
    if args.color_svg_dir:
        conf['color_svg_dir'] = args.color_svg_dir
    if args.transform:
        conf['color_svg_transform'] = args.transform

    if args.verbose:
        conf['verbose'] = True

    # Be sure family name, subfamily, and version are set to something.
    if 'family' not in conf['table_name'] or args.family is not default_family:
        conf['table_name']['family'] = args.family
    if 'subfamily' not in conf['table_name'] or args.subfamily is not default_subfamily:
        conf['table_name']['weight'] = args.weight
    if 'version' not in conf['table_name'] or args.version is not default_version:
        conf['table_name']['version'] = args.version

    if 'output_file' not in conf:
        parser.error('--output is required.')
        return 1
    if 'glyph_svg_dir' not in conf:
        parser.error('--glyph-svg-dir is required. (currently)')
        return 1
    if 'color_svg_dir' not in conf:
        parser.error('--color-svg-dir is required. (currently)')
        return 1

    builder = Builder(conf)
    return builder.run()

if __name__ == '__main__':
    main()
