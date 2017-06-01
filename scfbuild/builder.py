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
from distutils.version import LooseVersion
import xml.etree.ElementTree as ET

import fontTools
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.S_V_G_ import table_S_V_G_
from fontTools.ttLib.tables._n_a_m_e import NameRecord, table__n_a_m_e

from . import fforge
from . import util
from .util import FONT_EM, SVG_TRANSFORM_SCALE
from .constants import name_record as NR

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Support for SVG tables was added to fontTools in version 2.5
if LooseVersion('2.5') > LooseVersion(fontTools.version):
    logger.exception("The FontTools module version must be 2.5 or higher.")
    sys.exit(1)
# todo: Check FontForge version


class NoCodePointsException(Exception):
    pass


class Builder(object):

    def __init__(self, conf=None):
        self.conf = conf
        self.uids_for_glyph_names = None

        if self.conf['verbose']:
            logging.getLogger().setLevel(logging.DEBUG)

    def run(self):
        logger.info("Creating a new font")
        ff_font = fforge.create_font(self.conf)

        # Find and add regular glyphs
        svg_filepaths = util.get_svg_filepaths(self.conf['glyph_svg_dir'])
        # TODO: Validate regular SVGs
        logger.info("Adding glyphs and ligatures")
        fforge.add_glyphs(ff_font, svg_filepaths, self.conf)

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

        # Set default namespace (avoids "ns0:svg")
        ET.register_namespace("", "http://www.w3.org/2000/svg")

        for filepath in svg_files:
            glyph_id = self.get_glyph_id(filepath)

            svg_tree = ET.parse(filepath)
            svg_root = svg_tree.getroot()
            # Add Glyph ID as SVG root id, required by SVGinOT spec.
            svg_root.set('id', "glyph{}".format(glyph_id))

            # Remove the viewBox/height/width attributes since they are
            # processed inconsistently by Gecko and Edge renderers.
            try:
                del svg_root.attrib['viewBox']
            except KeyError:
                pass

            try:
                del svg_root.attrib['height']
            except KeyError:
                pass

            try:
                del svg_root.attrib['width']
            except KeyError:
                pass

            # Add the transform to size the SVG to the FONT_EM
            svg_transform = self.create_color_transform(filepath)
            logger.debug("Set SVG transform: {}".format(svg_transform))

            svg_transform_attrib = {"transform": svg_transform}
            # Create a new group tag to apply the transform to
            new_svg_group = ET.Element('g', svg_transform_attrib)
            # Copy all SVG root children to the new group
            for child in svg_root:
                new_svg_group.append(child)

            # Backup the root attribs, clear the children, and apply attribs
            svg_root_attrib = svg_root.items()
            svg_root.clear()
            for name, value in svg_root_attrib:
                svg_root.set(name, value)

            # Append the new group.
            svg_root.append(new_svg_group)

            data = ET.tostring(svg_root, encoding='UTF-8')
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
        Get a dict of glyph names in the font indexed by unicode IDs
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

    def create_color_transform(self, filepath):
        """
        Generate the transform for the color SVG.
        """
        svg_transform = ""
        if 'color_transform' in self.conf:
            svg_transform = "{} ".format(self.conf['color_transform'])
        svg_height, _ = util.get_dimensions(filepath)

        # Find the scale multiplier based on current height verses intended
        # height (aka font EM). Whatever the SVG is, it needs to be scaled to
        # fit within the FONT_EM.
        scale = FONT_EM / svg_height

        # No need to adjust, but called out for clarity.
        translate_x = 0
        # SVG(y Down) vs Glyph/TTF(y Up) y-coordinate differences.
        # Simple answer is -FONT_EM but that does not account for descent.
        # Y=0 is on the baseline without a descent adjustment.
        # Default font descent: -2/10*2048 = -409.6
        translate_y = - (FONT_EM - FONT_EM * .2)

        svg_transform += "translate({},{}) scale({})".format(translate_x,
                                                             translate_y,
                                                             scale)

        return svg_transform

    def add_name_table(self):
        # FontForge doesn't support all font fields, so we use FontTools.
        self.name_table = table__n_a_m_e()
        self.name_table.names = []

        tn = self.conf['table_name']

        # Set the values that will always exist.
        self.add_name_records(tn['family'], NR.FAMILY)
        self.add_name_records(tn['subfamily'], NR.SUBFAMILY)

        fullname = ''
        if 'full_name' in tn:
            fullname = tn['full_name']
        else:
            fullname = "{} {}".format(tn['family'], tn['subfamily'])
        self.add_name_records(fullname, NR.FULL_NAME)

        # Add the build date to the version
        now = time.strftime('%Y%m%d')
        version = "{} {}".format(tn['version'], now)
        self.add_name_records(version, NR.VERSION)

        # Add the build date to the unique id
        unique_id = ''
        if 'unique_id' in tn:
            unique_id = "{} {}".format(tn['unique_id'], now)
        else:
            unique_id = now
        self.add_name_records(unique_id, NR.UNIQUE_ID)

        # Set the values that don't always exist
        for key, name_id in (
                ('copyright', NR.COPYRIGHT),
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
