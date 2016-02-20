# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os


def codepoint_from_filepath(filepath):
    (filename, _) = os.path.splitext(os.path.basename(filepath))

    if '-' in filename:
        return (-1, filename)

    # Convert unicode filename to decimal.
    codepoint = int(filename, 16)

    return (codepoint, filename)
