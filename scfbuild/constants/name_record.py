# -*- coding: utf-8 -*-
# SCFBuild is released under the GNU General Public License v3.
# See LICENSE.txt in the project root directory.
"""
Constants for the Name Records

More details: https://www.microsoft.com/typography/otspec/name.htm
"""

# TODO: Fill out the rest?

# Platform IDs, Platform-specific encoding IDs and Language IDs
PLATFORM_UNICODE = 0
PLATFORM_MAC = 1
PLATFORM_WIN = 3

# Unicode platform-specific encoding IDs (platform ID = 0)
UC_ENC_UNICODE1 = 0
UC_ENC_UNICODE11 = 1
UC_ENC_UNICODE2_BMP = 3
UC_ENC_UNICODE2_FULL = 4

UC_LANG_NA = 0x0

# Windows platform-specific encoding IDs (platform ID = 3)
WIN_ENC_SYMBOL = 0
WIN_ENC_UNICODE = 1

# Windows Language IDs (platform ID = 3)
WIN_LANG_EN = 0x409

# Macintosh platform-specific encoding IDs (platform ID = 1)
MAC_ENC_ROMAN = 0

# Macintosh language IDs (platform ID = 1)
MAC_LANG_EN = 0x0

# Name IDs
COPYRIGHT = 0
FAMILY = 1
SUBFAMILY = 2
UNIQUE_ID = 3
FULL_NAME = 4
VERSION = 5
PS_NAME = 6
TRADEMARK = 7
MANUFACTURER = 8
DESIGNER = 9
DESCRIPTION = 10
URL_VENDOR = 11
URL_DESIGNER = 12
LICENSE = 13
URL_LICENSE = 14
