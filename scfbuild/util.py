# -*- coding: utf-8 -*-
# SCFBuild is released under the GNU General Public License v3.
# See LICENSE.txt in the project root directory.

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import glob
import os


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


def add_svg_glyph_id(svg, id):
    # TODO: Don't assume the glyph id is missing.
    old = '<svg '
    new = '<svg id="glyph{}" '.format(id)

    return svg.replace(old, new)


def add_svg_transform(svg, transform):
    old = '<svg '
    new = '<svg transform="{}" '.format(transform)

    return svg.replace(old, new)
