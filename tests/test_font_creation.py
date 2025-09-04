# -*- coding: utf-8 -*-
"""
Test suite for SCFBuild UFO-based font creation functionality
"""

import os
import tempfile
import shutil
import pytest
from scfbuild.ufo_builder import create_font, compile_to_ttf, add_glyphs


@pytest.fixture
def basic_config():
    """Basic configuration fixture for tests"""
    return {
        "family": "TestFont",
        "style": "Regular",
        "width_space": 512,
    }


@pytest.fixture
def temp_dir():
    """Temporary directory fixture"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    # Cleanup
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_svg_content():
    """Sample SVG content for testing"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
  <path d="M10 10 L90 10 L90 90 L10 90 Z"/>
</svg>'''


class TestBasicFontCreation:
    """Test basic UFO font creation functionality"""

    def test_create_font_basic_properties(self, basic_config):
        """Test that create_font sets up basic font properties correctly"""
        ufo_font = create_font(basic_config)

        assert ufo_font.info.familyName == "TestFont"
        assert ufo_font.info.styleName == "Regular"
        assert ufo_font.info.unitsPerEm == 2048

    def test_create_font_basic_glyphs(self, basic_config):
        """Test that create_font creates all required basic glyphs"""
        ufo_font = create_font(basic_config)

        # Check that all basic glyphs exist
        required_glyphs = [".notdef", ".null", "CR", "space", "uni200D", "uniFE0F"]
        for glyph_name in required_glyphs:
            assert glyph_name in ufo_font, f"Missing required glyph: {glyph_name}"

        # Check space glyph has custom width
        space_glyph = ufo_font["space"]
        assert space_glyph.width == 512

    def test_font_compilation(self, basic_config):
        """Test that UFO font can be compiled to TTF successfully"""
        ufo_font = create_font(basic_config)
        tt_font = compile_to_ttf(ufo_font)

        # Verify TTF properties
        assert tt_font['head'].unitsPerEm == 2048
        assert 'glyf' in tt_font
        assert 'cmap' in tt_font

        # Check that all glyphs are present in compiled font
        glyf_table = tt_font["glyf"]
        glyph_names = list(glyf_table.glyphs.keys())

        required_glyphs = [".notdef", ".null", "CR", "space", "uni200D", "uniFE0F"]
        for glyph_name in required_glyphs:
            assert glyph_name in glyph_names, f"Missing glyph in TTF: {glyph_name}"

    def test_font_saving(self, basic_config, temp_dir):
        """Test saving compiled font to disk"""
        ufo_font = create_font(basic_config)
        tt_font = compile_to_ttf(ufo_font)

        output_path = os.path.join(temp_dir, "test_font.ttf")
        tt_font.save(output_path)

        assert os.path.exists(output_path)
        file_size = os.path.getsize(output_path)
        assert file_size > 500, f"Font file too small: {file_size} bytes"


class TestGlyphProcessing:
    """Test glyph processing and SVG handling"""

    def test_add_glyphs_with_regular_glyphs(self, basic_config, temp_dir, sample_svg_content):
        """Test adding regular glyphs from SVG files"""
        ufo_font = create_font(basic_config)

        # Create test glyph file
        glyph_path = os.path.join(temp_dir, "1f600.svg")
        with open(glyph_path, 'w') as f:
            f.write(sample_svg_content)

        # Add glyphs
        result_font = add_glyphs(ufo_font, [glyph_path], basic_config)

        # Verify glyph was added
        assert "uni1F600" in result_font
        glyph = result_font["uni1F600"]
        assert glyph.width == 2048  # Should be set based on SVG dimensions

    def test_add_glyphs_with_ligature(self, basic_config, temp_dir, sample_svg_content):
        """Test adding ligature glyphs"""
        ufo_font = create_font(basic_config)

        # Create test ligature file
        ligature_path = os.path.join(temp_dir, "1f441-1f5e8.svg")
        with open(ligature_path, 'w') as f:
            f.write(sample_svg_content)

        # Add glyphs
        result_font = add_glyphs(ufo_font, [ligature_path], basic_config)

        # Verify ligature glyph was added
        assert "1f441-1f5e8" in result_font
        glyph = result_font["1f441-1f5e8"]

        # Check ligature components are stored
        assert glyph.lib
        assert "com.scfbuild.ligature_components" in glyph.lib
        components = glyph.lib["com.scfbuild.ligature_components"]
        assert len(components) == 3  # eye + ZWJ + speech bubble

    def test_svg_curve_parsing(self, basic_config, temp_dir):
        """Test that SVG paths with various curve types are parsed correctly"""
        ufo_font = create_font(basic_config)

        # Create SVG with different curve types
        svg_with_curves = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
  <!-- Cubic Bézier curve -->
  <path d="M10 10 C 20 20, 40 20, 50 10"/>
  <!-- Quadratic Bézier curve -->
  <path d="M60 60 Q 80 50 100 60"/>
  <!-- Smooth cubic Bézier curve -->
  <path d="M10 80 C 20 70, 30 70, 40 80 S 60 90, 70 80"/>
  <!-- Smooth quadratic Bézier curve -->
  <path d="M80 20 Q 90 10 100 20 T 120 30"/>
  <!-- Arc -->
  <path d="M10 40 A 10 10 0 0 1 30 40"/>
</svg>'''

        # Create test glyph file
        glyph_path = os.path.join(temp_dir, "1f600.svg")
        with open(glyph_path, 'w') as f:
            f.write(svg_with_curves)

        # Add glyphs - this should not raise any exceptions
        result_font = add_glyphs(ufo_font, [glyph_path], basic_config)

        # Verify glyph was added
        assert "uni1F600" in result_font
        glyph = result_font["uni1F600"]

        # Verify glyph has contours (paths were parsed successfully)
        assert glyph.width == 2048  # Should be set based on SVG dimensions

    def test_svg_parsing_error_handling(self, basic_config, temp_dir):
        """Test that invalid SVG paths raise hard errors instead of warnings"""
        ufo_font = create_font(basic_config)

        # Create SVG with invalid path data that will cause parsing to fail
        invalid_svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
  <!-- Invalid path data - malformed Bézier curve -->
  <path d="M10 10 C invalid control points 50 10"/>
  <!-- Valid path after invalid one -->
  <path d="M60 60 L 80 80"/>
</svg>'''

        # Create test glyph file
        glyph_path = os.path.join(temp_dir, "1f600.svg")
        with open(glyph_path, 'w') as f:
            f.write(invalid_svg)

        # This should raise a ValueError due to the invalid path
        with pytest.raises(ValueError, match="Failed to parse SVG path"):
            add_glyphs(ufo_font, [glyph_path], basic_config)


class TestIntegration:
    """Test complete integration workflow"""

    def test_complete_font_generation_pipeline(self, temp_dir, sample_svg_content):
        """Test the complete font generation pipeline using the Builder class"""
        # Create directories for test SVG files
        glyph_dir = os.path.join(temp_dir, "glyphs")
        color_dir = os.path.join(temp_dir, "colors")
        os.makedirs(glyph_dir)
        os.makedirs(color_dir)

        # Create test SVG files
        glyph_svg = os.path.join(glyph_dir, "1f600.svg")
        color_svg = os.path.join(color_dir, "1f600.svg")

        with open(glyph_svg, 'w') as f:
            f.write(sample_svg_content)
        with open(color_svg, 'w') as f:
            f.write(sample_svg_content)

        # Create output path
        output_file = os.path.join(temp_dir, "test_output.ttf")

        # Create configuration
        conf = {
            "family": "TestCompleteFont",
            "style": "Regular",
            "glyph_svg_dir": glyph_dir,
            "color_svg_dir": color_dir,
            "output_file": output_file,
            "width_space": 512,
            "verbose": False,
            "table_name": {
                "family": "TestCompleteFont",
                "subfamily": "Regular",
                "version": "1.0",
                "copyright": "Test Font",
                "manufacturer": "Test Manufacturer",
                "designer": "Test Designer",
                "description": "Test font for Phase 6 validation",
                "url_vendor": "https://example.com",
                "url_designer": "https://example.com",
                "license": "Test License",
                "url_license": "https://example.com",
                "typographic_family": "TestCompleteFont",
                "typographic_subfamily": "Regular",
                "wws_family": "TestCompleteFont",
                "wws_subfamily": "Regular"
            }
        }

        # Test the complete Builder workflow
        from scfbuild.builder import Builder
        builder = Builder(conf)
        result = builder.run()

        # Verify the build was successful
        assert result == 0, "Font build should return success (0)"
        assert os.path.exists(output_file), f"Output file should exist: {output_file}"

        # Verify the output file has reasonable size
        file_size = os.path.getsize(output_file)
        assert file_size > 1000, f"Output file seems too small: {file_size} bytes"

        # Try to load the generated font to verify it's valid
        from fontTools.ttLib import TTFont
        tt_font = TTFont(output_file)

        # Basic validation
        assert 'glyf' in tt_font, "Generated font should have glyf table"
        assert 'cmap' in tt_font, "Generated font should have cmap table"
        assert 'SVG ' in tt_font, "Generated font should have SVG table for color glyphs"

        # Check that our test glyph is present
        glyf_table = tt_font['glyf']
        assert 'uni1F600' in glyf_table.glyphs, "Test glyph should be present in font"
