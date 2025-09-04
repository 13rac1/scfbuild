# -*- coding: utf-8 -*-
"""
Test script for basic UFO font creation functionality
"""

import os
import tempfile
import logging
from scfbuild.ufo_builder import create_font, compile_to_ttf, add_glyphs

# Set up logging
logging.basicConfig(level=logging.DEBUG)


def test_basic_font_creation():
    """Test basic font creation and compilation"""
    print("Testing basic UFO font creation...")

    # Create a test configuration
    conf = {
        "family": "TestFont",
        "style": "Regular",
        "width_space": 512,  # Custom space width
    }

    try:
        # Create the font
        print("Creating UFO font...")
        ufo_font = create_font(conf)

        # Verify basic properties
        assert ufo_font.info.familyName == "TestFont"
        assert ufo_font.info.styleName == "Regular"
        assert ufo_font.info.unitsPerEm == 2048

        # Verify basic glyphs exist
        assert ".notdef" in ufo_font
        assert ".null" in ufo_font
        assert "CR" in ufo_font
        assert "space" in ufo_font
        assert "uni200D" in ufo_font  # ZWJ
        assert "uniFE0F" in ufo_font  # VS16

        # Verify space glyph has custom width
        space_glyph = ufo_font["space"]
        assert space_glyph.width == 512

        print(f"✓ Created font with {len(ufo_font)} glyphs")
        print(f"✓ Font family: {ufo_font.info.familyName}")
        print(f"✓ Font style: {ufo_font.info.styleName}")
        print(f"✓ Units per em: {ufo_font.info.unitsPerEm}")

        # Test compilation to TTF
        print("\nCompiling to TTF...")
        tt_font = compile_to_ttf(ufo_font)

        # Verify TTF properties
        assert tt_font["head"].unitsPerEm == 2048
        assert "glyf" in tt_font  # Should have glyph table
        assert "cmap" in tt_font  # Should have character map

        # Check that basic glyphs are in the TTF glyf table
        glyf_table = tt_font["glyf"]
        glyph_names_in_font = list(glyf_table.glyphs.keys())

        assert ".notdef" in glyph_names_in_font
        assert ".null" in glyph_names_in_font
        assert "CR" in glyph_names_in_font
        assert "space" in glyph_names_in_font
        assert "uni200D" in glyph_names_in_font
        assert "uniFE0F" in glyph_names_in_font

        print(f"✓ Compiled TTF with {len(glyph_names_in_font)} glyphs in glyf table")

        # Check cmap for Unicode-mapped glyphs (space, CR, null should be there)
        unicode_glyphs = set()
        for table in tt_font["cmap"].tables:
            if table.isUnicode():
                unicode_glyphs.update(table.cmap.values())

        # Space and CR should be in cmap since they have Unicode values
        assert "space" in unicode_glyphs
        print(f"✓ Found {len(unicode_glyphs)} Unicode-mapped glyphs in cmap")
        print("✓ Basic font creation test PASSED!")

        return True

    except Exception as e:
        print(f"✗ Test FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_font_saving():
    """Test saving the compiled font to disk"""
    print("\nTesting font saving...")

    conf = {"family": "SaveTest", "style": "Regular"}
    ufo_font = create_font(conf)
    tt_font = compile_to_ttf(ufo_font)

    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix=".ttf", delete=False) as tmp_file:
        tmp_path = tmp_file.name

    try:
        tt_font.save(tmp_path)
        file_size = os.path.getsize(tmp_path)
        print(f"✓ Saved font to {tmp_path} ({file_size} bytes)")
        assert file_size > 500  # Should be a reasonable size for a basic font
        print("✓ Font saving test PASSED!")
        return True
    except Exception as e:
        print(f"✗ Font saving test FAILED: {e}")
        return False
    finally:
        # Clean up
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except OSError:
            pass


def test_add_glyphs_functionality():
    """Test the add_glyphs function with mock SVG files"""
    print("\nTesting add_glyphs functionality...")

    # Create test configuration
    conf = {
        "family": "TestFont",
        "style": "Regular",
        "width_space": 512
    }

    # Create UFO font
    ufo_font = create_font(conf)

    # Create temporary SVG files for testing
    import tempfile
    import os

    svg_files = []
    try:
        # Create a simple SVG file for testing (regular glyph: grinning face emoji)
        svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
  <path d="M10 10 L90 10 L90 90 L10 90 Z"/>
</svg>'''

        # Create properly named SVG files
        temp_dir = tempfile.mkdtemp()
        regular_svg = os.path.join(temp_dir, "1f600.svg")
        ligature_svg = os.path.join(temp_dir, "1f441-1f5e8.svg")

        with open(regular_svg, 'w') as f:
            f.write(svg_content)
        svg_files.append(regular_svg)

        with open(ligature_svg, 'w') as f:
            f.write(svg_content)
        svg_files.append(ligature_svg)

        # Test add_glyphs function
        result_font = add_glyphs(ufo_font, svg_files, conf)

        # Verify glyphs were added
        assert len(result_font) > 6  # Should have more than just the basic glyphs
        print(f"✓ Added glyphs to font, now has {len(result_font)} total glyphs")

        # Test compilation with added glyphs
        tt_font = compile_to_ttf(result_font)
        glyf_table = tt_font['glyf']
        glyph_names_in_font = list(glyf_table.glyphs.keys())
        print(f"✓ Compiled TTF with {len(glyph_names_in_font)} glyphs")

        return True

    except Exception as e:
        print(f"✗ add_glyphs test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Clean up temporary directory
        try:
            import shutil
            if 'temp_dir' in locals() and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except OSError:
            pass


if __name__ == "__main__":
    print("Running Phase 1 and Phase 3 validation tests...\n")

    success1 = test_basic_font_creation()
    success2 = test_font_saving()
    success3 = test_add_glyphs_functionality()

    if success1 and success2 and success3:
        print("\n🎉 All Phase 1 and Phase 3 tests PASSED!")
        print("Basic UFO font creation and glyph processing are working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        exit(1)
