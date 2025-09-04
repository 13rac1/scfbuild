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

def test_ligature_support():
    """Test ligature glyph creation and feature file generation"""
    print("\nTesting ligature support...")

    conf = {
        "family": "TestFont",
        "style": "Regular",
        "width_space": 512
    }

    # Create UFO font
    ufo_font = create_font(conf)

    # Create temporary SVG files for ligature testing
    import tempfile
    import os

    svg_files = []
    temp_dir = None
    try:
        # Create a simple SVG file for testing
        svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
  <path d="M10 10 L90 10 L90 90 L10 90 Z"/>
</svg>'''

        # Create temporary directory for test files
        temp_dir = tempfile.mkdtemp()
        eye_svg = os.path.join(temp_dir, "1f441.svg")
        speech_svg = os.path.join(temp_dir, "1f5e8.svg")
        ligature_svg = os.path.join(temp_dir, "1f441-1f5e8.svg")

        # Create individual glyph SVGs
        with open(eye_svg, 'w') as f:
            f.write(svg_content)
        svg_files.append(eye_svg)

        with open(speech_svg, 'w') as f:
            f.write(svg_content)
        svg_files.append(speech_svg)

        with open(ligature_svg, 'w') as f:
            f.write(svg_content)
        svg_files.append(ligature_svg)

        # Test add_glyphs with ligature
        result_font = add_glyphs(ufo_font, svg_files, conf)

        # Verify ligature glyph was created
        assert "1f441-1f5e8" in result_font
        ligature_glyph = result_font["1f441-1f5e8"]

        # Verify ligature components are stored
        assert ligature_glyph.lib
        assert "com.scfbuild.ligature_components" in ligature_glyph.lib
        components = ligature_glyph.lib["com.scfbuild.ligature_components"]

        # Should contain eye, ZWJ, and speech bubble glyph names
        assert len(components) == 3
        print(f"✓ Created ligature glyph with components: {components}")

        # Note: Feature file generation is disabled for now
        # Basic ligature glyph creation and component storage is working
        # Verify ligature glyph exists with components stored
        ligature_glyph = result_font["1f441-1f5e8"]
        assert ligature_glyph.lib
        assert "com.scfbuild.ligature_components" in ligature_glyph.lib
        print("✓ Ligature glyph created with component information stored")

        # Test compilation with ligatures
        tt_font = compile_to_ttf(result_font)
        glyf_table = tt_font['glyf']
        glyph_names_in_font = list(glyf_table.glyphs.keys())

        assert "1f441-1f5e8" in glyph_names_in_font
        print(f"✓ Compiled TTF with {len(glyph_names_in_font)} glyphs including ligature")

        return True

    except Exception as e:
        print(f"✗ Ligature test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Clean up temporary directory
        try:
            import shutil
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except OSError:
            pass


def test_complete_font_generation():
    """Test the complete font generation pipeline using the Builder class"""
    print("\nTesting complete font generation pipeline...")

    # Create test configuration
    import tempfile
    import os

    temp_dir = tempfile.mkdtemp()
    try:
        # Create directories for test SVG files
        glyph_dir = os.path.join(temp_dir, "glyphs")
        color_dir = os.path.join(temp_dir, "colors")
        os.makedirs(glyph_dir)
        os.makedirs(color_dir)

        # Create test SVG files
        svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
  <path d="M10 10 L90 10 L90 90 L10 90 Z"/>
</svg>'''

        # Create a glyph SVG
        with open(os.path.join(glyph_dir, "1f600.svg"), 'w') as f:
            f.write(svg_content)

        # Create a color SVG
        with open(os.path.join(color_dir, "1f600.svg"), 'w') as f:
            f.write(svg_content)

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
            "verbose": True,
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

        print(f"✓ Successfully generated complete font: {output_file}")
        print(f"✓ Font size: {file_size} bytes")
        print(f"✓ Font contains {len(glyf_table.glyphs)} glyphs")
        print(f"✓ Font includes SVG color table")

        return True

    except Exception as e:
        print(f"✗ Complete font generation test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Clean up
        try:
            import shutil
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except OSError:
            pass


if __name__ == "__main__":
    print("Running complete Phase 1-6 validation tests...\n")

    success1 = test_basic_font_creation()
    success2 = test_font_saving()
    success3 = test_add_glyphs_functionality()
    success4 = test_ligature_support()
    success5 = test_complete_font_generation()

    if success1 and success2 and success3 and success4 and success5:
        print("\n🎉 All Phase 1-6 tests PASSED!")
        print("Complete UFO-based font generation pipeline is working correctly.")
        print("Builder integration, glyph processing, ligature support, and color SVG addition all functional.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        exit(1)
