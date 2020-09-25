# SVGinOT Color Font Builder

*Create color fonts from SVGs on the command line*

`scfbuild` creates *SVG in OpenType* color fonts directly from a set of source
SVG files greatly simplifying the process of creating a custom color font.

Regular color and standard character [glyphs][glyph] are named by
[Unicode][unicode] code point (e.g. `1f60e.svg`). [Ligatures][ligature] are
named by code points separated by a hyphen `-` (e.g.`1f441-1f5e8.svg`). Note:
Color glyphs cannot exist alone, they must replace existing standard glyphs.

The generated fonts work in all operating systems, but will *currently* only
show color glyphs in supported applications. This is not a limitation of the
generated fonts, but of the operating systems and applications. The primary
offender at this time is Chromium, therefore Chrome/NewEdge. [Why doesn't it
work on Chrome?][why-not-chrome]

Only the *SVG in OpenType* color font format is supported. The Apple, Google,
and Microsoft color font formats are not supported at this time.

[glyph]: https://en.wikipedia.org/wiki/Glyph
[unicode]: https://en.wikipedia.org/wiki/Unicode
[ligature]: https://en.wikipedia.org/wiki/Typographic_ligature
[why-not-chrome]: https://bugs.chromium.org/p/chromium/issues/detail?id=306078

## Examples

* [Twitter Color Emoji][twemoji-color-font] - Color emoji font using Twitter
  Emoji for Everyone graphics.
* Color CC-BY-4.0 alphanumeric fonts:
  * [Reinebow][reinebow] -  [[source][reinebow-src]]
  * [Gradiently][gradiently] - [[source][gradiently-src]]
  * [Multicoloure][multicoloure] - [[source][multicoloure-src]]
  * [Freizer][freizer] - [[source][freizer-src]]

[twemoji-color-font]: https://github.com/eosrei/twemoji-color-font
[reinebow]: http://xerographer.github.io/reinebow/
[reinebow-src]: https://github.com/xerographer/reinebow-color-font
[gradiently]: http://xerographer.github.io/gradiently/
[gradiently-src]: https://github.com/xerographer/gradiently-color-font
[multicoloure]: http://xerographer.github.io/multicoloure/
[multicoloure-src]: https://github.com/xerographer/multicoloure-font
[freizer]: http://xerographer.github.io/freizer/
[freizer-src]: https://github.com/xerographer/freizer-color-font

## What is SVGinOT?

*SVG in Open Type* is a standard by Adobe and Mozilla for color OpenType
and Open Font Format fonts. It allows font creators to embed complete SVG files
within a font enabling full color and even animations. There are more details in
the [SVGinOT proposal][8] and the [OpenType SVG table specifications][9].

SVGinOT Demos:

* https://www.adobe.com/devnet-apps/type/svgopentype.html
* https://hacks.mozilla.org/2014/10/svg-colors-in-opentype-fonts/

[8]: https://www.w3.org/2013/10/SVG_in_OpenType/
[9]: https://www.microsoft.com/typography/otspec/svg.htm

## Setup - Linux

Ubuntu 20.04 LTS / Mint 20

```bash
sudo apt-get update
sudo apt-get install fontforge \
  python3-fontforge python3-fonttools python3-pip python3-yaml
sudo pip3 install fonttools
```

## Usage - Linux

Required Python 3 libraries:

* FontTools 4.5+
* FontForge 20190801+

Run: `bin/scfbuild`

```sh
$ bin/scfbuild --help
usage: scfbuild [-h] [-o OUTPUT] [-g DIR] [-s DIR] [--transform TRANSFORM]
                [--font-family FAMILY] [--font-subfamily SUBFAMILY]
                [--font-version FONT_VERSION] [-c YAML_CONF] [-v] [-V]

SCFBuild - SVGinOT Color Font Builder 1.x.x

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        output font file
  -g DIR, --glyph-svg-dir DIR
                        directory of regular no-color SVG glyphs to add to the
                        font
  -s DIR, --color-svg-dir DIR
                        directory of SVGinOT color SVG glyphs to add to the
                        font.
  --transform TRANSFORM
                        add a transform to the <svg> tag of each color SVG.
                        Example "translate(0 -1638) scale(2.048)"
  --font-family FAMILY  family name for the font. default: Untitled
  --font-subfamily SUBFAMILY
                        weight/style for the font. default: Regular
  --font-version FONT_VERSION
                        version number for the font. default: 1.0
  -c YAML_CONF, --yaml-conf YAML_CONF
                        yaml build configuration, overridden by command line
                        options.
  -v, --verbose         print detailed debug information
  -V, --version         print version information
```

## Other Tools
`scfbuild` softens the learning curve for font creation, but cannot replace more
advanced tools. Here are some starting points if you need more features,
although none support color fonts at this time:

* http://fontforge.github.io/en-US/
* https://github.com/adobe-type-tools/afdko
* https://birdfont.org/

## License

SCFBuild is released under the GNU General Public License v3.
See [LICENSE.txt](LICENSE.txt) in the project root directory.
