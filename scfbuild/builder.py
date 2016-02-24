# -*- coding: utf-8 -*-

# SCFBuild is released under the GNU General Public License v3.
# See LICENSE.txt in the project root directory.

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import os
import sys
import tempfile
import time
from distutils.version import StrictVersion

import fontTools
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.S_V_G_ import table_S_V_G_
from fontTools.ttLib.tables._n_a_m_e import NameRecord, table__n_a_m_e

from . import fforge
from . import util
from .constants import name_record as NR

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Support for SVG tables was added to fontTools in version 2.5
if StrictVersion('2.5') > StrictVersion(fontTools.version):
    logger.exception("The FontTools module version must be 2.5 or higher.")
    sys.exit(1)


class NoCodePointsException(Exception):
    pass


class Builder(object):

    def __init__(self, conf=None):
        self.conf = conf
        self.uids_for_glyph_names = None

        if self.conf['verbose']:
            logging.getLogger().setLevel(logging.DEBUG)

    def run(self):
        # TODO: Remove FontForge dependency?
        logger.info("Creating a new font")
        ff_font = fforge.create_font(self.conf)

        # Find and add regular glyphs
        svg_filepaths = util.get_svg_filepaths(self.conf['glyph_svg_dir'])
        # TODO: Validate regular SVGs
        logger.info("Adding glyphs and ligatures")
        fforge.add_glyphs(ff_font, svg_filepaths)

        tmp_dir = tempfile.mkdtemp()
        tmp_file = os.path.join(tmp_dir, "tmp.ttf")
        logger.debug("Using temp file: %s", tmp_file)

        # TODO: Validate ligature tables to avoid warning during generate
        # "Lookup subtable contains unused glyph NAME making the whole subtable invalid"
        logger.info("Generating intermediate font file")
        ff_font.generate(tmp_file)
        del ff_font

        logger.info("Reading intermediate font file")
        self.font = TTFont(tmp_file)
        logger.info("Adding SVGinOT SVG files")
        # TODO: Validate color SVGs
        self.add_color_svg()
        self.add_name_table()
        logger.info("Saving output file: %s", self.conf['output_file'])
        self.font.save(self.conf['output_file'])

        # Cleaning Up
        os.remove(tmp_file)
        os.rmdir(tmp_dir)

        logger.info("Done!")
        # 0 for success
        return 0

    def add_color_svg(self):
        svg_files = util.get_svg_filepaths(self.conf['color_svg_dir'])
        svg_list = []

        for filepath in svg_files:
            glyph_id = self.get_glyph_id(filepath)

            data = util.read_file(filepath)
            data = util.add_svg_glyph_id(data, glyph_id)
            if self.conf['color_svg_transform']:
                data = util.add_svg_transform(
                    data, self.conf['color_svg_transform'])

            logger.debug("Glyph ID: %d Adding SVG: %s", glyph_id, filepath)
            svg_list.append([data, glyph_id, glyph_id])

        svg_table = table_S_V_G_()
        # The SVG table must be sorted by glyph_id
        svg_table.docList = sorted(svg_list, key=lambda table: table[1])
        svg_table.colorPalettes = None
        self.font['SVG '] = svg_table

    def get_glyph_id(self, filepath):
        """
        Find a Glyph ID for the filename in filepath
        """
        if self.uids_for_glyph_names is None:
            self.uids_for_glyph_names = self.get_uids_for_glyph_names()

        (codepoint, filename) = util.codepoint_from_filepath(filepath)

        # Check for a regular glyph first
        try:
            glyph_name = self.uids_for_glyph_names[codepoint]
        except KeyError:
            # If that doesn't work check for a Ligature Glyph
            glyph_id = self.font.getGlyphID(filename)

            if glyph_id is -1:
                logger.warning("No Glyph ID found for: %s (Note: A regular "
                               "glyph is required for each color glyph)", filepath)

            logger.debug("Found Ligature Glyph: %s", filename)
            return glyph_id

        logger.debug("Found regular Glyph: %s", glyph_name)
        return self.font.getGlyphID(glyph_name)

    def get_uids_for_glyph_names(self):
        """
        Get a dict glyph names in the font indexed by unicode IDs
        """
        codepoints = {}
        for subtable in self.font['cmap'].tables:
            if subtable.isUnicode():
                for codepoint, name in subtable.cmap.items():
                    # NOTE: May overwrite previous values
                    codepoints[codepoint] = name
        if len(codepoints) is 0:
            raise NoCodePointsException(
                'No Unicode IDs/CodePoints found in font.')

        return codepoints

    def add_name_table(self):
        # FontForge doesn't support all font fields, so we use FontTools.
        self.name_table = table__n_a_m_e()
        self.name_table.names = []

        tn = self.conf['table_name']

        # Set the values that will always exist.
        self.add_name_records(tn['family'], NR.FAMILY)
        self.add_name_records(tn['subfamily'], NR.SUBFAMILY)

        version = "{} {}".format(tn['version'], time.strftime('%Y%m%d'))
        self.add_name_records(version, NR.VERSION)

        fullname = "{} {}".format(tn['family'], tn['subfamily'])
        self.add_name_records(fullname, NR.FULL_NAME)

        # Set the values that don't always exist
        for key, name_id in (
                ('copyright', NR.COPYRIGHT),
                ('unique_id', NR.UNIQUE_ID),
                ('postscript_name', NR.PS_NAME),
                ('trademark', NR.TRADEMARK),
                ('manufacturer', NR.MANUFACTURER),
                ('designer', NR.DESIGNER),
                ('description', NR.DESCRIPTION),
                ('url_vendor', NR.URL_VENDOR),
                ('url_designer', NR.URL_DESIGNER),
                ('license', NR.LICENSE),
                ('url_license', NR.URL_LICENSE)):
            if key in tn:
                self.add_name_records(tn[key], name_id)

        self.font['name'] = self.name_table

    def add_name_records(self, text, name_id):
        # <namerecord nameID="0" platformID="0" platEncID="0" langID="0x0">
        self._add_name_record(text, name_id,
                              NR.PLATFORM_UNICODE,
                              NR.UC_ENC_UNICODE1,
                              NR.UC_LANG_NA)

        # <namerecord nameID="0" platformID="1" platEncID="0" langID="0x0" unicode="True">
        self._add_name_record(text, name_id,
                              NR.PLATFORM_MAC,
                              NR.MAC_ENC_ROMAN,
                              NR.MAC_LANG_EN)

        # <namerecord nameID="0" platformID="3" platEncID="1" langID="0x409">
        self._add_name_record(text, name_id,
                              NR.PLATFORM_WIN,
                              NR.WIN_ENC_UNICODE,
                              NR.WIN_LANG_EN)

    def _add_name_record(self, text, name_id, platform_id, plat_enc_id, lang_id):
        # TODO: The installed version of fontTools doesn't have
        # table__n_a_m_e.setName().
        record = NameRecord()
        # PyYAML creates strings, force to Unicode
        record.string = unicode(text)
        record.nameID = name_id
        record.platformID = platform_id
        record.platEncID = plat_enc_id
        record.langID = lang_id
        self.name_table.names.append(record)
