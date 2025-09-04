# Project: Remove FontForge Dependency

## Overview
Replace the system dependency on FontForge with pip-installable `ufo2ft` library for better portability and maintainability.

## Current FontForge Usage Analysis

**Location**: `scfbuild/fforge.py`
**Key operations**:
- Font creation: `fontforge.font()`
- Glyph creation and manipulation
- SVG outline import: `glyph.importOutlines(filepath)`
- Font generation: `font.generate(tmp_file)`
- Ligature support
- Glyph transformations

## Replacement Strategy

**Chosen solution**: Use `ufo2ft` with UFO font objects
- **Pros**: Direct programmatic control, pip-installable, active maintenance, can eliminate intermediate file I/O
- **Cons**: Requires refactoring of font creation logic

### Key Optimizations Discovered

**✅ Intermediate TTF file can be skipped**: `ufo2ft.compileTTF()` returns an in-memory `TTFont` object directly, allowing us to add color SVGs without file I/O.

**⚠️ Color SVGs need post-compilation**: UFO format supports image references but not direct SVG table storage. Color SVGs must be added to the compiled TTF using fontTools, similar to current approach.

### Technical Details

- **UFO Image Support**: Glyphs have an `image` attribute with `fileName` and `color` properties, but this is for background images, not color font SVGs
- **Compilation Flow**: `ufo2ft.compileTTF(ufo)` → `TTFont` object (in-memory) → add SVG table → save final font
- **No File I/O**: The entire process can work with in-memory objects, eliminating the temporary TTF file

## Implementation Tasks

### Phase 1: Setup and Infrastructure
- [x] Create new module `scfbuild/ufo_builder.py` to replace `fforge.py`
- [x] Install required dependencies: `ufoLib2`, `ufo2ft`
- [x] Set up test environment to validate font generation
- [x] Create basic UFO font creation utilities

### Phase 2: Core Font Creation
- [ ] Implement `create_font()` equivalent using UFO objects
- [ ] Add basic glyph creation (.notdef, .null, CR, space, ZWJ, VS16)
- [ ] Implement Unicode encoding setup (equivalent to `font.encoding = 'UnicodeFull'`)
- [ ] Set up font EM size (`font.em = FONT_EM`)

### Phase 3: Glyph Processing
- [ ] Implement `add_glyphs()` function for regular glyphs
- [ ] Convert SVG import from FontForge to UFO format
- [ ] Handle glyph width calculations and transformations
- [ ] Implement glyph operations (removeOverlap, simplify, addExtrema)

### Phase 4: Ligature Support
- [ ] Implement ligature glyph creation without codepoints
- [ ] Add ligature lookup table setup
- [ ] Handle ZWJ/VS16 sequences correctly
- [ ] Ensure ligature glyph naming compatibility

### Phase 5: Font Compilation
- [ ] Replace `font.generate()` with `ufo2ft.compileTTF()`
- [ ] **Eliminate intermediate file I/O** - work with in-memory TTFont objects
- [ ] Ensure glyph order preservation
- [ ] Validate font compilation output

### Phase 6: Integration and Testing
- [ ] Update `builder.py` to use new UFO-based font creation
- [ ] Modify build pipeline to work with in-memory TTFont objects
- [ ] **Keep existing color SVG addition logic** - add SVGs to compiled font object
- [ ] Test font generation with sample inputs
- [ ] Validate generated fonts in font viewers/editors

### Phase 7: Cleanup and Documentation
- [ ] Remove FontForge dependency from README
- [ ] Update installation instructions
- [ ] Remove `fforge.py` module
- [ ] Update version requirements in pyproject.toml
- [ ] Add migration notes for users

## Dependencies to Add

```toml
[project]
dependencies = [
    "fonttools>=4.40.0",
    "ufoLib2>=0.16.0",
    "ufo2ft>=2.25.0",
    "PyYAML>=5.1",
    "fontmake>=3.0.0",  # Optional: for reference/comparison
]
```

## Testing Strategy

1. **Unit Tests**: Test individual components (glyph creation, ligatures, compilation)
2. **Integration Tests**: Full font build pipeline with sample SVGs
3. **Comparison Tests**: Generate fonts with both FontForge and UFO approaches
4. **Validation Tests**: Ensure generated fonts work in target applications

## Risk Mitigation

- **Fallback Plan**: Keep FontForge version working alongside new implementation
- **Incremental Migration**: Replace components one at a time
- **Compatibility Layer**: Maintain same API where possible
- **Performance Testing**: Ensure UFO approach meets performance requirements

## Success Criteria

- [ ] FontForge removed from dependencies
- [ ] All existing functionality preserved
- [ ] Font generation produces identical results
- [ ] **Eliminated intermediate file I/O** - faster build process
- [ ] Improved installation experience (no system packages)
- [ ] Better cross-platform compatibility
- [ ] Easier CI/CD setup

## Timeline Estimate

- Phase 1-2: 1-2 weeks (Setup and basic font creation)
- Phase 3-4: 2-3 weeks (Glyph processing and ligatures)
- Phase 5-6: **1 week** (Compilation and integration - simplified by in-memory processing)
- Phase 7: 0.5 week (Cleanup and documentation)

**Total: 4.5-6.5 weeks** (potentially faster due to eliminated I/O operations)

## Alternative Approaches (if needed)

1. **fontmake wrapper**: Use fontmake command-line instead of direct API
2. **Hybrid approach**: Keep FontForge for complex operations, use UFO for simple ones
3. **Incremental replacement**: Replace only non-critical FontForge features first

## Resources

- [ufo2ft Documentation](https://github.com/googlefonts/ufo2ft)
- [UFO Font Format Spec](https://unifiedfontobject.org/)
- [FontTools Documentation](https://fonttools.readthedocs.io/)
- [Current FontForge usage in fforge.py](./scfbuild/fforge.py)
