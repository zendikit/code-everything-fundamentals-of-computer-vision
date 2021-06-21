# Parsing Pixel Data

## Challenge

If you're following along using our prepared grayscale bitmap v4 image or one with identical properties to it, parsing pixel data is not much of a challenge. Instead, let's consider how we can confirm
that we parsed the pixel values correctly. There are many ways to do this. Perhaps the most convenient and entertaining for us is to render an image created from our parsed pixel data. We can't simply write
the bitmap file bytes back out to a bitmap file, though, as we know it would be bit-identical to our input file and therefore a moot test.

First, parse the pixel data out of the image file and store it in your image abstraction you created previously.

Next, create a new image based on your pixel data and render that to visually confirm you've parsed the pixel data correctly. To create a new image, you can use libraries like
[OpenCV](https://pypi.org/project/opencv-python/) or [Pillow](https://pypi.org/project/Pillow/) if you are already familiar with them. If you are not, no need to go out of your way to learn them at this
time. We will deal with at least OpenCV later. In our implementation, we will create a new image manually using a very simple image file format: the Portable GrayMap (PGM).

## PGM Primer

You can easily find information on the [PGM format](https://en.wikipedia.org/wiki/Netpbm#PGM_example) on sites like Wikipedia. Our description here, though, is all you need should you choose to
create a PGM image.

A PGM file encodes a grayscale image as ASCII in a text file. The file has two sections: the header and the pixel data. The file extension is `.pgm`.

### PGM Header

The PGM header is as follows:

```text
P2
WIDTH HEIGHT
MAX_VALUE
```

`P2` is the PGM file format identifier and must be specified verbatim. (PGM is part of a broader family of formats called the Portable Anymap Format (PNM).)

`WIDTH` and `HEIGHT` are both positive integers specifying the corresponding dimension of the image in pixels.

Finally, `MAX_VALUE` is the maximum value of any given pixel. If less than 256, each pixel is encoded in 1 byte. If 256 or greater, each pixel is encoded in 2 bytes (for a maximum value of 65,535).

### PGM Pixel Data

Pixel data follows the header.

Pixel data is encoded simply as the unsigned integer value (in ASCII) of each pixel. You can encode one or more pixels on each line, but we recommend you keep lines short because we know of no guarantee that
lines can be of arbitrary length.

Black is encoded as `0`, and white is the user-specified maximum value. Any other value is a blend between black and white. Note that the PGM file does not specify how to blend the colors, so various
software may render a PGM image slightly differently.

### Example

Consider a square image 2 pixels by 2 pixels. The top left pixel is black, the top right and bottom left pixels are gray, and the bottom right pixel is white. Such an image may be encoded as a PGM as
follows. (`#` starts a comment in PGM files.)

```text
# image.pgm
# This is the header.
P2
2 2
255
# And these are our 4 pixel values.
0
127
127
255
```

## Bitmap Hint

Recall the documentation of the `height_px` field of the bitmap V4 header. Pixel data in a bitmap is stored in one of two ways, depending on the sign of this field.
