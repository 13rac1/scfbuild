# Font Verification Demo Project

## 🎯 Overview

Add a new CLI argument `--verify` to SCFBuild that generates an HTML verification file containing a visual demo of the generated font. This tool helps users verify that font generation worked correctly by providing side-by-side comparisons of original SVGs vs rendered font output.

## 📋 Requirements

### CLI Interface
```bash
scfbuild --glyph-svg-dir ./glyphs --color-svg-dir ./colors --output myfont.ttf --verify
scfbuild --glyph-svg-dir ./glyphs --color-svg-dir ./colors --output myfont.ttf --verify --all-glyphs
scfbuild --glyph-svg-dir ./glyphs --color-svg-dir ./colors --output myfont.ttf --verify demo.html
scfbuild --glyph-svg-dir ./glyphs --color-svg-dir ./colors --output myfont.ttf --verify demo.html --all-glyphs
```

### HTML Output Structure
The generated HTML file will contain:

1. **Header Section**
   - Font metadata (family, style, version, creation date)
   - Build statistics (total glyphs, processing time)
   - Instructions for verification

2. **Glyph Verification Table**
   - **Unicode ID**: The hex code point (e.g., `1F600`)
   - **B&W SVG**: Original black and white glyph SVG (inline or embedded)
   - **Color SVG**: Original color glyph SVG (inline or embedded)
   - **B&W PNG**: Rendered black and white glyph from font
   - **Color PNG**: Rendered color glyph from font
   - **Unicode Character**: Live character rendered by browser's font

3. **Navigation & Controls**
   - Pagination for large glyph sets
   - Search/filter functionality
   - Zoom controls for glyph inspection
   - Export options

## 🏗️ Technical Implementation

### Phase 1: Core Infrastructure

#### 1.1 CLI Argument Integration
```python
# In main.py, add to argument parser
parser.add_argument(
    '--verify',
    nargs='?',
    const='font-demo.html',
    metavar='OUTPUT_FILE',
    help='Generate HTML verification file (default: font-demo.html)'
)

parser.add_argument(
    '--all-glyphs',
    action='store_true',
    help='Include all glyphs in verification (default: first 100)'
)
```

#### 1.2 Font Analysis Module
```python
# New module: scfbuild/font_analyzer.py
class FontAnalyzer:
    def __init__(self, tt_font: TTFont, config: dict):
        self.font = tt_font
        self.config = config
        self.glyph_order = list(tt_font.getGlyphOrder())

    def get_glyph_info(self, glyph_name: str) -> dict:
        """Extract comprehensive glyph information"""
        return {
            'unicode': self._get_unicode_value(glyph_name),
            'svg_path': self._find_original_svg(glyph_name, 'bw'),
            'color_svg_path': self._find_original_svg(glyph_name, 'color'),
            'glyph_name': glyph_name,
            'width': self.font['hmtx'][glyph_name][0]
        }
```

#### 1.3 PNG Rendering Engine
```python
# New module: scfbuild/png_renderer.py
class PNGSVGRenderer:
    def __init__(self, font_path: str):
        self.font_path = font_path
        # Use fontTools + PIL/Pillow for rendering

    def render_glyph_png(self, unicode_char: str, size: int = 64,
                        color: bool = True) -> bytes:
        """Render glyph to PNG bytes"""
        # Implementation using fontTools drawing and PIL
        pass
```

### Phase 2: HTML Generation

#### 2.1 HTML Template System
```python
# New module: scfbuild/html_generator.py
class FontVerificationHTML:
    def __init__(self, font_path: str, analyzer: FontAnalyzer):
        self.font_path = font_path
        self.analyzer = analyzer

    def generate_html(self, output_path: str, max_glyphs: int = 100):
        """Generate complete HTML verification file"""
        glyphs = self.analyzer.get_glyphs()[:max_glyphs]

        html_content = self._generate_html_template()
        html_content += self._generate_glyph_table(glyphs)
        html_content += self._generate_footer()

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
```

#### 2.2 SVG Embedding Strategy
```python
def embed_svg(self, svg_path: str) -> str:
    """Embed SVG content inline or as data URI"""
    if os.path.exists(svg_path):
        with open(svg_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()
        # Sanitize and embed SVG content
        return f'<div class="svg-container">{svg_content}</div>'
    return '<div class="svg-missing">SVG not found</div>'
```

#### 2.3 PNG Generation Integration
```python
def generate_png_data_uri(self, unicode_char: str, color: bool) -> str:
    """Generate PNG as base64 data URI"""
    png_bytes = self.png_renderer.render_glyph_png(unicode_char, color=color)
    b64_data = base64.b64encode(png_bytes).decode('utf-8')
    return f'data:image/png;base64,{b64_data}'
```

### Phase 3: Advanced Features

#### 3.1 Interactive Features
```javascript
// Basic interactivity for glyph inspection
function showGlyphDetails(glyphId) {
    // Zoom, comparison, details modal
}

function filterGlyphs(searchTerm) {
    // Search/filter table rows
}
```

#### 3.2 Responsive Design
```css
.glyph-table {
    width: 100%;
    border-collapse: collapse;
}

.glyph-cell {
    padding: 10px;
    text-align: center;
    border: 1px solid #ddd;
}

.svg-preview {
    max-width: 64px;
    max-height: 64px;
}

@media (max-width: 768px) {
    .glyph-table { font-size: 12px; }
    .svg-preview { max-width: 32px; }
}
```

## 📦 Dependencies & Requirements

### New Dependencies
```toml
# Add to pyproject.toml
[project.dependencies]
Pillow>=10.0.0  # For PNG rendering
reportlab>=4.0.0  # Alternative font rendering
cairocffi>=1.6.0  # Vector graphics rendering
```

### System Requirements
- Python 3.9+ (for modern font rendering APIs)
- Font rendering backend (Pillow/cairo)
- Sufficient disk space for PNG generation

## 🧪 Testing Strategy

### Unit Tests
```python
def test_font_analyzer_glyph_info():
    """Test glyph information extraction"""

def test_png_renderer_output():
    """Test PNG generation quality"""

def test_html_generation_structure():
    """Test HTML structure and validity"""
```

### Integration Tests
```python
def test_full_verification_workflow():
    """Test complete CLI workflow with sample data"""

def test_large_font_verification():
    """Test with fonts containing 1000+ glyphs"""
```

### Visual Regression Tests
```python
def test_rendering_consistency():
    """Ensure rendered PNGs match expected output"""
```

## 🎨 HTML Design Specification

### Color Scheme
- Clean, professional appearance
- High contrast for accessibility
- Consistent with SCFBuild branding

### Layout Structure
```
┌─ Header ──────────────────────────────┐
│ Font: MyFont Regular v1.0            │
│ Generated: 2024-01-15 14:30:00      │
│ Total Glyphs: 1,234                 │
└─────────────────────────────────────┘

┌─ Controls ───────────────────────────┐
│ [Search] [All] [100] [Zoom: 1x 2x]  │
└─────────────────────────────────────┘

┌─ Glyph Table ────────────────────────┐
│ Unicode │ B&W SVG │ Color SVG │ ... │
├─────────┼─────────┼───────────┼─────┤
│ 1F600   │ [😀]    │ [🌈😀]   │ ... │
└─────────┴─────────┴───────────┴─────┘
```

## 📊 Performance Considerations

### Memory Management
- Stream PNG generation to avoid loading all images into memory
- Use lazy loading for large glyph sets
- Implement pagination for HTML table

### Build Time Impact
- PNG rendering: ~50-200ms per glyph
- HTML generation: ~10ms per glyph
- Total overhead: ~5-10% for typical font sizes

### Optimization Strategies
- Parallel PNG rendering using multiprocessing
- Caching of rendered PNGs
- Progressive HTML generation

## 🔧 Implementation Plan

### Sprint 1: Core Infrastructure (Week 1-2)
- [ ] CLI argument integration
- [ ] Font analyzer module
- [ ] Basic HTML template
- [ ] Unit tests for core functionality

### Sprint 2: Rendering Engine (Week 3-4)
- [ ] PNG renderer implementation
- [ ] SVG embedding system
- [ ] HTML table generation
- [ ] Integration tests

### Sprint 3: Advanced Features (Week 5-6)
- [ ] Interactive features
- [ ] Responsive design
- [ ] Performance optimizations
- [ ] Comprehensive documentation

### Sprint 4: Polish & Documentation (Week 7-8)
- [ ] Visual design improvements
- [ ] Accessibility features
- [ ] User documentation
- [ ] Final testing and bug fixes

## 📈 Success Metrics

- **Functionality**: 100% glyph coverage in verification
- **Performance**: <2 seconds for 100 glyph demo
- **Compatibility**: Works in all modern browsers
- **Usability**: Clear, intuitive interface
- **Reliability**: 99% success rate for valid fonts

## 🎯 Usage Examples

### Basic Verification
```bash
scfbuild --glyph-svg-dir ./glyphs --output emoji.ttf --verify
# Generates: emoji-demo.html
```

### Full Font Verification
```bash
scfbuild --glyph-svg-dir ./glyphs --output emoji.ttf --verify full-demo.html --all-glyphs
# Generates: full-demo.html with all glyphs
```

### Custom Output Location
```bash
scfbuild --glyph-svg-dir ./glyphs --output emoji.ttf --verify ./docs/verification.html
```

This verification tool will significantly improve the SCFBuild user experience by providing immediate visual feedback on font generation quality and helping identify any issues with the conversion process.
