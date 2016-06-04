# -*- coding: utf-8 -*-
# SCFBuild is released under the GNU General Public License v3.
# See LICENSE.txt in the project root directory.

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import glob
import os
import logging
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

FONT_EM = 2048
DEFAULT_GLYPH_WIDTH = 512
# The SVGs are scaled to 1000x1000 by the Gecko renderer, but need to be scaled
# by 2.048 to fit the 2048 FONT_EM
SVG_TRANSFORM_SCALE = 2.048


def codepoint_from_filepath(filepath):
    (filename, _) = os.path.splitext(os.path.basename(filepath))

    if '-' in filename:
        return (-1, filename)

    # Convert unicode filename to decimal.
    codepoint = int(filename, 16)

    return (codepoint, filename)


def get_svg_filepaths(svg_dir):
    return [filename for filename in glob.glob(os.path.join(svg_dir, '*.svg'))]


def read_file(file_path):
    f = open(file_path, "rt")
    data = f.read()
    f.close()
    return data


def add_svg_glyph_id(svg, glyph_id):
    # Todo: Don't assume the glyph id is missing.
    # Todo: Do this with a XML parser
    old = '<svg '
    new = '<svg id="glyph{}" '.format(glyph_id)

    return svg.replace(old, new)


def add_svg_transform(svg, transform):
    old = '<svg '
    new = '<svg transform="{}" '.format(transform)

    return svg.replace(old, new)


def get_dimensions(svg_filepath):
    """
    Load and parse the SVG XML. Return the height and width
    """
    tree = ET.parse(svg_filepath)
    root = tree.getroot()

    # Try to get the height/width attribs
    try:
        height = float(root.attrib['height'])
        width = float(root.attrib['width'])
    except KeyError:
        # Try to get the viewBox. Format: 0 0 200 200
        # Todo: Can fail with key error
        dims = root.attrib['viewBox'].split(' ')
        height = float(dims[2])
        width = float(dims[3])

    logger.debug("Found SVG width/height (%.2f/%.2f)", width, height)
    return (height, width)


def get_glyph_width(filepath):
    """
    Given the filepath of a SVG, find the glyph width.
    """
    svg_height, svg_width = get_dimensions(filepath)
    glyph_ratio = svg_width / svg_height
    return int(FONT_EM * glyph_ratio)
