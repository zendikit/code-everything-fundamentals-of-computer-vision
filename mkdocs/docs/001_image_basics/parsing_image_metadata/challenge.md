# Parsing Image Metadata

## Challenge

Write a command-line program that takes an image file as its input and prints
all parsed image metadata as output. You don't have to deal with the pixel array yet.
If you'll be parsing a bitmap v4 image, use the data structure definitions in
[Theory](./theory.md) (or supplemental documentation) to guide your development.

Below is output from our bitmap parser (`bp.py`) program when passed our
provided sample image of the Tokyo Skytree. Note that most values are printed as
read out of the image file, but some values are adjusted before printing (for
example that for `File type`).

```text
$ ./bp.py 2021-02-22-tokyo-skytree-grayscale.bmp
File type        : BM
Size             : 263290 bytes
Pixel data offset: 1146 bytes
Size                     : 108 bytes
Width                    : 512 px
Height                   : 512 px
Number of color planes   : 1
Number of bits per pixel : 8
Compression type         : 0
Pixel data size          : 262144 bytes
Width resolution         : 11811 ppm
Height resolution        : 11811 ppm
Number of colors used    : 256
Number of colors required: 256
Red bitmask              : 0x73524742
Green bitmask            : 0x0
Blue bitmask             : 0x0
Alpha bitmask            : 0x0
Color space type         : 0
Color space endpoints    :
red  : (0.0, 0.0, 0.0)
green: (0.0, 0.0, 0.0)
blue : (0.0, 0.0, 3.0517578125e-05)
Red gamma                : 0.0
Green gamma              : 0.0
Blue gamma               : 0.0
```
