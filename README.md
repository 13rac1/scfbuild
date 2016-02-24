# SVGinOT Color Font Builder

*Create color fonts from SVGs on the command line*

`scfbuild` creates *SVG in OpenType* color fonts directly from a set of source
SVG files greatly simplifying the process of creating a custom color font.

Regular color and standard character [glyph][1] are named by [Unicode][2] code
point (e.g. `1f60e.svg`). [Ligatures][3] are named by code points separated
by a hyphen `-` (e.g.`1f441-1f5e8.svg`). Note: Color glyphs cannot exist alone,
they must replace existing standard glyphs.

The generated fonts work in all operating systems, but will *currently* only
show color glyphs in Mozilla Firefox and Thunderbird. This is not a limitation
of the generated fonts, but of the operating systems and applications. Only the
*SVG in OpenType* color font format is supported. The Apple, Google, and
Microsoft color font formats are not supported.

[1]: https://en.wikipedia.org/wiki/Glyph
[2]: https://en.wikipedia.org/wiki/Unicode
[3]: https://en.wikipedia.org/wiki/Typographic_ligature

## What is SVGinOT?
*SVG in Open Type* is a standard by Adobe and Mozilla for color OpenType
and Open Font Format fonts. It allows font creators to embed complete SVG files
within a font enabling full color and even animations. There are more details in
the [SVGinOT proposal][4] and the [OpenType SVG table specifications][5].

SVGinOT Demos (Firefox only):

* https://www.adobe.com/devnet-apps/type/svgopentype.html
* https://hacks.mozilla.org/2014/10/svg-colors-in-opentype-fonts/

[4]: https://www.w3.org/2013/10/SVG_in_OpenType/
[5]: https://www.microsoft.com/typography/otspec/svg.htm

## Usage - Linux

Required Python libraries:

* FontTools 2.5+
* FontForge

Run: `bin/scfbuild`

```sh
$ bin/scfbuild -h
usage: scfbuild [-h] [-g DIR] [-c DIR] [--transform TRANSFORM]
                [--familyname FAMILYNAME] [--weight WEIGHT]
                [--fullname FULLNAME] [--font-version VERSION] [-v]
                output

SCFBuild - SVGinOT Color Font Builder

positional arguments:
  output                output font file

optional arguments:
  -h, --help            show this help message and exit
  -g DIR, --glyph-dir DIR
                        directory of regular no-color SVG glyphs to add to the
                        font
  -c DIR, --color-dir DIR
                        directory of SVGinOT color SVG glyphs to add to the
                        font.
  --transform TRANSFORM
                        add a transform to the <svg> tag of each color SVG.
                        Example "translate(0 -800) scale(1.2)"
  --familyname FAMILYNAME
                        family name for the font. default: Untitled
  --weight WEIGHT       weight/syle for the font. default: Regular
  --fullname FULLNAME   full name of the font. default: Family Name +
                        Weight(if not 'Regular')
  --font-version VERSION
                        version number for the font. default: 1.0
  -v, --verbose         print detailed debug information
```

## Examples

* EmojiOne Color SVGinOT - SCFBuild was written to create this font.
* Simpler examples coming soon!

## Other Tools
`scfbuild` softens the learning curve for font creation, but cannot replace more
advanced tools. Here are some starting points if you need more features:

* http://fontforge.github.io/en-US/
* https://github.com/adobe-type-tools/afdko
* https://birdfont.org/

## License

SCFBuild is released under the GNU General Public License v3.
See LICENSE.txt in the project root directory.
