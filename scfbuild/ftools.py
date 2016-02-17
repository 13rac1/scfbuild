# -*- coding: utf-8 -*-
"""
Utility functions using fontTools
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys

import fontTools as fonttools
from distutils.version import StrictVersion

# Support for SVG tables was added to fontTools in version 2.5
if StrictVersion('2.5') > StrictVersion(fonttools.version):
    print("ERROR: The FontTools module version must be 2.5 or higher.",
          file=sys.stderr)
    sys.exit(1)


class NoCodePointsException(Exception):
    pass


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
