# Parsing Image Metadata

## Implementation

When implementing our bitmap parser, `bp`, let's start with basic functionality
that enables us to modify our parser, run it against input, and see what
changed. This way we can quickly visually debug things.

## `main`

Our main script will be `bp.py`. We'll use `argparse` to build a CLI that takes
as input a pathname to an image file. We'll open that file for reading as
binary, slurp its contents, and pass them to a (currently stub) `BitmapV4` class
for parsing.

```python
#!/usr/bin/python3 -B

import argparse

class BitmapV4:
    def __init__(self, data):
        pass

def main():
    parser = argparse.ArgumentParser(
        description="Limited-functionality bitmap parser")
    parser.add_argument("image", help="An image file pathname")
    args = parser.parse_args()

    with open(args.image, "rb") as f:
        data = f.read()

    image = BitmapV4(data)
    print(image)

if __name__ == "__main__":
    main()
```

At this point, you can run your program, and if your input file exists, your
program will print details about your `BitmapV4` instance.

```text
$ chmod +x bp.py
$ ./bp.py 2021-02-22-tokyo-skytree-grayscale.bmp
<__main__.BitmapV4 object at 0x7fcd816bad30>
```

## `BitmapV4`

We'll do our bitmap parsing logic in `BitmapV4` and some additional classes. If
this were a proper tool, we might have an `Image` base class with some generic
properties like `width`, `height`, and `pixels` so that we could parse various
image file types in corresponding classes but present a common API to the user
through polymorphism. We won't go that far here, though.

We anticipate having to parse the general bitmap file header and also the V4
header, so we create class stubs for those. In the `BitmapV4` constructor, we
pass the bitmap data and a corresponding byte offset to constructors of the
header stubs.

We define our own `__str__` method which will now be used when we call
`print(image)` as we did in `main()`.

```python
class BitmapFileHeader:
    def __init__(self, data, offset):
        pass

class V4InfoHeader:
    def __init__(self, data, offset):
        pass

class BitmapV4:
    def __init__(self, data):
        """
        Arguments:
            data(bytes): The binary data of an entire bitmap image file.
        """
        self.file_header = BitmapFileHeader(data, 0)
        self.info_header = V4InfoHeader(data, 14)

    def __str__(self):
        return f"{self.file_header}\n{self.info_header}"
```

Running our program now prints something similar to

```text
$ ./bp.py 2021-02-22-tokyo-skytree-grayscale.bmp
<__main__.BitmapFileHeader object at 0x7f3acd451610>
<__main__.V4InfoHeader object at 0x7f3acd49a9d0>
```

## `BitmapFileHeader`

Our `BitmapFileHeader` corresponds to the official bitmap `BITMAPFILEHEADER`.

We use the [`struct`](https://docs.python.org/3.8/library/struct.html) module to
parse the image byte array. The struct module returns tuples, and we don't want
to create an intermediate data structure that essentially mirrors our class
members, so we unpack the tuple in-place. Remember that bitmap data is stored
unconditionally in little endian. Therefore, our `struct.unpack_from` format
string leads with `<` indicating little endian. `H` indicates an unsigned 16-bit
integer, and `I` indicates an unsigned 32-bit integer.

We define our own `__str__` method which prints information about our instance.
Since the "magic" bytes are stored in little endian, we have to swap the two
lowest bytes and then convert them to characters before printing in order to see
the text "BM."

```python
import struct

class BitmapFileHeader:
    def __init__(self, data, offset):
        """
        Parse a bitmap file header from a byte array.

        Args:
            data(bytes): Binary data read from a bitmap file.
            offset(int): The byte offset in `data` at which parsing starts.
        """
        self.file_type, \
        self.size_bytes, \
        self.reserved_1, \
        self.reserved_2, \
        self.pixel_data_offset_bytes = struct.unpack_from(
            "<HIHHI", data, offset=offset)

    def __str__(self):
        magic_byte_1 = chr(self.file_type & 0xff)
        magic_byte_2 = chr((self.file_type & 0xff00) >> 8)
        return f"File type        : {magic_byte_1}{magic_byte_2}\n" +\
               f"Size             : {self.size_bytes} bytes\n" +\
               f"Pixel data offset: {self.pixel_data_offset_bytes} bytes"
```

Now our program will print something more interesting.

```
$ ./bp 2021-02-22-tokyo-skytree-grayscale.bmp
File type        : BM
Size             : 263290 bytes
Pixel data offset: 1146 bytes
<__main__.V4InfoHeader object at 0x7f2d5c153a00>
```

`du` confirms the file size.

```
$ du -b ./2021-02-22-tokyo-skytree-grayscale.bmp
263290	./2021-02-22-tokyo-skytree-grayscale.bmp
```

## `V4InfoHeader`

Our `V4InfoHeader` corresponds to the official bitmap `BITMAPV4HEADER`.

Parsing `V4InfoHeader` is a lot like parsing `BitmapFileHeader` except that our
constructor delegates to another constructor partway through parsing. Also, some
of our fields are in fixed (x.y) notation, so we need to convert them after
parsing. We do this by assigning the parsed value to a temporary, dividing that
temporary by `2**y`, and then assigning the quotient to a member variable. Note
also that we have to manually adjust `offset` as we parse different parts of
`data`.

```python
class CIEXYZ:
    def __init__(self, data, offset):
        pass

class CIEXYZTriple:
    def __init__(self, data, offset):
        pass

class V4InfoHeader:
    def __init__(self, data, offset):
        """
        Parse a bitmap version 4 info header from a byte array.

        Args:
            data(bytes): Binary data read from a bitmap file.
            offset(int): The byte offset in `data` at which parsing starts.
        """
        self.size_bytes, \
        self.width_px, \
        self.height_px, \
        self.num_color_planes, \
        self.num_bits_per_pixel, \
        self.compression_type, \
        self.pixel_data_size_bytes, \
        self.pixels_per_meter_width, \
        self.pixels_per_meter_height, \
        self.num_colors_used, \
        self.num_colors_required, \
        self.red_bitmask, \
        self.green_bitmask, \
        self.blue_bitmask, \
        self.alpha_bitmask, \
        self.color_space_type = struct.unpack_from(
            "<IiiHHIIiiIIIIIII", data, offset=offset)

        self.color_space_endpoints = CIEXYZTriple(data, offset + 60)

        red_gamma, \
        green_gamma, \
        blue_gamma = struct.unpack_from("<III", data, offset=offset + 96)

        self.red_gamma = red_gamma / 2**30
        self.green_gamma = green_gamma / 2**30
        self.blue_gamma = blue_gamma / 2**30

    def __str__(self):
        return \
            f"Size                     : {self.size_bytes} bytes\n" +\
            f"Width                    : {self.width_px} px\n" +\
            f"Height                   : {self.height_px} px\n" +\
            f"Number of color planes   : {self.num_color_planes}\n" +\
            f"Number of bits per pixel : {self.num_bits_per_pixel}\n" +\
            f"Compression type         : {self.compression_type}\n" +\
            f"Pixel data size          : {self.pixel_data_size_bytes} bytes\n" +\
            f"Width resolution         : {self.pixels_per_meter_width} ppm\n" +\
            f"Height resolution        : {self.pixels_per_meter_height} ppm\n" +\
            f"Number of colors used    : {self.num_colors_used}\n" +\
            f"Number of colors required: {self.num_colors_required}\n" +\
            f"Red bitmask              : 0x{self.red_bitmask:X}\n" +\
            f"Green bitmask            : 0x{self.green_bitmask:X}\n" +\
            f"Blue bitmask             : 0x{self.blue_bitmask:X}\n" +\
            f"Alpha bitmask            : 0x{self.alpha_bitmask:X}\n" +\
            f"Color space type         : {self.color_space_type}\n" +\
            f"Color space endpoints    : \n{self.color_space_endpoints}\n" +\
            f"Red gamma                : {self.red_gamma}\n" +\
            f"Green gamma              : {self.green_gamma}\n" +\
            f"Blue gamma               : {self.blue_gamma}"
```

We can run our program again and see additional, interesting output.

```text
$ ./bp 2021-02-22-tokyo-skytree-grayscale.bmp
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
<__main__.CIEXYZTriple object at 0x7fa28c7c5100>
Red gamma                : 0.0
Green gamma              : 0.0
Blue gamma               : 0.0
```

Let's confirm the output. Using an image viewer, we can confirm that our input image is indeed 512x512 pixels, so the height and width are okay. From the documentation, we expect the number of color planes
to be 1, so that is also okay.

As for bits per pixel, since our image is grayscale, each pixel is encoded as a single intensity value of black (that is, we have only one "color" channel). If there are 8 bits per pixel, the possible
pixel values are [0, 255]. Other image properties agree with our 8 bpp report, too. For example, the number of colors used and the number of colors required. But even more telling is the pixel data size.

```math
\begin{align}
\text {pixel data size} &= \text {width} \cdot \text {height} \cdot \text {num channels} \cdot \text {bytes per pixel} \\
& = 512 \cdot 512 \cdot 1 \cdot 1 \\
& = 262144
\end{align}
```

Note that in (1) above we are concerned with _bytes_ per pixel. We see that our pixel data size agrees with our other measurements!

We ignore the width and height resolution as they're not important to our learning here.

Do note the red bitmask, though. It is non-zero, but does it matter? The answer is no, according to the bitmap documentation. Our compression type is 0, indicating an uncompressed format that disregards the
RGB bitmasks. That the red bitmask is non-zero here seems to be an artifact from GIMP (in the case of our sample image), but it is of no other concern to us.

We are okay with the RGB gamma values being 0 because our image is grayscale.

## `CIEXYZ` and `CIEXYZTriple`

`CIEXYZ` and `CIEXYZTriple` correspond to the official bitmap `CIEXYZ` and
`CIEXYZTRIPLE` data structures.

Parsing these is straightforward by now and uses no techniques we haven't seen
already.

```python
class CIEXYZ:
    def __init__(self, data, offset):
        """
        Parse a color endpoint from a byte array.

        Arguments:
            data(bytes): Binary data read from a bitmap file.
            offset(int): The byte offset in `data` at which parsing starts.
        """
        x, \
        y, \
        z = struct.unpack_from("<III", data, offset=offset)

        self.x = x / 2**16
        self.y = y / 2**16
        self.z = z / 2**16

    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"


class CIEXYZTriple:
    def __init__(self, data, offset):
        """
        Parse color endpoints in a color space from a byte array.

        Arguments:
            data(bytes): Binary data read from a bitmap file.
            offset(int): The byte offset in `data` at which parsing starts.
        """
        self.red = CIEXYZ(data, offset)
        self.green = CIEXYZ(data, offset + 12)
        self.blue = CIEXYZ(data, offset + 24)

    def __str__(self):
        return f"red  : {self.red}\n" +\
               f"green: {self.green}\n" +\
               f"blue : {self.blue}"
```

If we run our program against our image again, we see

```text
$ ./bp 2021-02-22-tokyo-skytree-grayscale.bmp
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

The new information here is that of the color space endpoints. All values are 0 except the last element of the blue endpoint (which is still very close to 0 in this case). Unlike the value for the red
bitmask which the documentation suggested we can ignore, our color space type is 0 here indicating (again, from the documentation) that we must take the color endpoints into consideration. However, these
are endpoints for an RGB color space, but we know that our image is grayscale, so we can actually disregard these values. The non-zero element in the blue endpoint seems to again be an artifact of GIMP.

## Conclusion

This concludes our work for parsing metadata for a bitmap v4 image. Take a moment to consider the many image file formats in existence today, and also think about the many image formats your operating
system can render for you with only a few clicks or keystrokes! It's nice to not have to deal with this kind of boilerplate work.
In the future, we will use libraries to handle all of this parsing for us.
We're not quite there yet, though. In the next section, we'll parse the pixel data out of our test image by hand.
