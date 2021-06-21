# Parsing Pixel Data

## Theory

If we intended for the bitmap metadata-parsing tool we wrote earlier to be a general image-processing tool, we'd want a way to parse a variety of image types and present their pixel data in a single format,
independent of the original file type. When parsing pixel data from a file, you need to consider two things primarily. The first is general metadata such as bits per pixel, the color space the pixels are
encoded in, number of channels, and image width and height. The second is whether or not you can simply read the values as binary out of the image file or if you first need to decompress the pixel data.

In our specific case, with a grayscale bitmap v4 image with a width evenly divisible by 4 [recall from the previous section that a row of a bitmap's pixel array is padded to be evenly divisible by 4], we
made our life very easy. The pixels are packed contiguously as individual bytes right in the file--no decompression necessary or color channels to deal with.

We won't cover compression here. When you're dealing with pixels in RAM later on, which is what we want to focus more on, they will be uncompressed.

Regarding pixel encoding, though, if images have `C` channels, `W` width, and `H` height, then their pixel values are often encoded in what we call CHW (sometimes CWH) or HWC (sometimes WHC).

## CHW

Think of CHW, for example, as "channels, then height, then width," meaning that in the file's pixel array we first have all pixels (width * height) for the first color channel, and then the next set of
pixels (width * height) for the second color channel, etc. If pixels were encoded as CHW, we could iterate over a flat array of pixels as

```python
for c in range(CHANNELS):
    for h in range(HEIGHT):
        for w in range (WIDTH):
            pixel_value = pixel_data[c * WIDTH * HEIGHT + h * WIDTH + w]
```

Note that in CHW the first dimension (channels) is the outermost loop and the last dimension (width) is the innermost loop. Seen another way, the width value changes the fastest, then the height, and lastly
the channels. If we drew the array for a 3-channel image and represented coordinates as `(row, column)`, it would look like

```text
(0, 0)---------------------------------------------------(0, WIDTH - 1) 
  |                                                              |
  |                          Channel 1                           |
  |                                                              |
  |                                                              |
(HEIGHT - 1, 0)------------------------------------------(HEIGHT - 1, WIDTH - 1)
  |                                                              |
  |                          Channel 2                           |
  |                                                              |
  |                                                              |
(2 * HEIGHT - 2, 0)----------------------------------(2 * HEIGHT - 2, WIDTH - 1)
  |                                                              |
  |                          Channel 3                           |
  |                                                              |
  |                                                              |
  +--------------------------------------------------------------+ 
```

## HWC

The other popular encoding interleaves the channel values for each pixel. We could iterate over a flat array of such pixels as

```python
for h in range(HEIGHT):
    for w in range (WIDTH):
        for c in range(CHANNELS):
            pixel_value = pixel_data[w * CHANNELS + h * WIDTH * CHANNELS + c]

```

If we are dealing with RGB (the red-green-blue color space) and represent a pixel's channel values as `Rn`, `Gn`, `Bn`, where `n` is the index of a particular pixel in the pixel data, the memory layout
looks like

```text
Index:   0    1     2    3    4    5    ...
       +----+----+----+----+----+----+--------+
       | R1 | G1 | B1 | R2 | G2 | B2 | <etc.> |
       +----+----+----+----+----+----+--------+
```
