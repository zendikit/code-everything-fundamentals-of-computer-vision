# Parsing Image Metadata

## Theory

Before we use handy libraries to parse images for us, we're going to write our
own limited-functionality parser to get an idea of what these parsing libraries
do for us behind the scenes.

## Preparing An Image

For this exercise, we'll be working with a bitmap image. If you want to generate
your own and follow our example code, it must:

1. be version 4
1. be grayscale
1. have a width evenly divisible by 4

Our example code will only correctly parse images which conform to the above.
We'll explain why later.

GIMP 2.10 can produce conformant bitmap images easily.

If you don't want to create your own image, you can use the image we have
prepared
[here, one of the Tokyo Skytree](../../assets/img/2021-02-22-tokyo-skytree-grayscale.bmp).
We will test against our prepared image.

## Why Bitmap?

While we want to understand the deeper intricacies of image parsing, we also
don't want to spend too much time on it. Parsing compressed JPEG or PNG files by
hand requires more effort than parsing an uncompressed bitmap image. On the
other end of the spectrum are filetypes such as PPM which are too trivial to be
useful parsing examples. We pick bitmaps as a comfortable medium. If you want to
challenge yourself with more sophisticated image file types, we encourage you.

## Bitmaps

The bitmap file format was developed by Microsoft. The file format evolved over
time, so while a file's extension may be ".bmp," the file data may be stored in
one of at least 5 different ways. We determine a bitmap file's version while we
are parsing it. In this exercise, we use bitmap version 4 simply because that's
the version that modern image processing tools such as GIMP output by default
for images with properties similar to that of our test image. For reference and
convenience, we detail the relevant parts of the bitmap version 4 data structure
in this text. For complete documentation, see Microsoft's own documentation or
that elsewhere online.

## Bitmap Version 4 Layout

| Entity                                                                                                   | Size (bytes) | Byte offset (decimal) |
| -------------------------------------------------------------------------------------------------------- | ------------ | --------------------- |
| [BITMAPFILEHEADER](https://docs.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-bitmapfileheader) | 14           | 0                     |
| [BITMAPV4HEADER](https://docs.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-bitmapv4header)     | 108          | 14                    |

Below we detail these types in C++ to show the byte mapping. Note that all data
in a bitmap file is stored in little endian.

### BITMAPFILEHEADER

The bitmap file header is common to all bitmaps. It provides basic file
metadata.

```c++
struct BITMAPFILEHEADER {
  // "Magic" bytes that indicate the file type. Should be ASCII "BM" in our case.
  uint16_t file_type;
  // The size in bytes of the entire bitmap file.
  uint32_t size_bytes;
  // Don't care.
  uint16_t reserved_1;
  // Don't care.
  uint16_t reserved_2;
  // The offset in bytes from the beginning of the file to the pixel data.
  uint32_t pixel_data_offset_bytes;
};
```

### BITMAPV4HEADER

The bitmap v4 header is a bitmap-version-specific data structure. When parsing
bitmap images, we determine which version-specific data structure to use by
parsing the first 4 bytes after the bitmap file header (in other words, the 4
bytes starting at absolute offset 14). These bytes correspond to the
`header_size_bytes` field below and indicate the byte size of the containing
version-specific header object. Version 4 requires a byte size of exactly 108.

Note the documentation for `pixel_data_size_bytes`. It is why we are working
with an image with a width evenly divisible by 4 (to make things easier for us
in later parsing).

Some fields below represent integers in a fixed x.y notation (ex: 2.30). This
means that the first x bits are the whole-number bits and the remaining y bits
are the fractional bits.

```c++
struct BITMAPV4HEADER {
  // The size in bytes of this header; must be 108 for a V4 header.
  uint32_t header_size_bytes;
  // The width in pixels of the image.
  int32_t width_px;
  // The height in pixels of the image. If the height is positive, the image is
  // a bottom-up one with an origin at the lower-left corner. If the height is
  // negative, the image is a top-down one with its origin at the top-left
  // corner.
  int32_t height_px;
  // The number of color planes in the image; must be 1.
  uint16_t num_color_planes;
  uint16_t num_bits_per_pixel;
  // The compression type used in a compressed, bottom-up image.
  uint32_t compression_type;
  // The size in bytes of the pixel data array, including any padding. Rows are
  // always padded to a size evenly divisible by 4 so that each row can be
  // encoded as a fixed number of 32-bit integers.
  uint32_t pixel_data_size_bytes;
  // The horizontal resolution in pixels-per-meter.
  int32_t pixels_per_meter_width;
  // The vertical resolution in pixels-per-meter.
  int32_t pixels_per_meter_height;
  // The number of color indices actually used in the color table. 0 indicates
  // all colors are used;
  uint32_t num_colors_used;
  // The number of colors required to render the image. 0 indicates all colors
  // are required.
  uint32_t num_colors_required;
  // A bitmask for extracting the red channel from pixel data.
  uint32_t red_bitmask;
  // A bitmask for extracting the green channel from pixel data.
  uint32_t green_bitmask;
  // A bitmask for extracting the blue channel from pixel data.
  uint32_t blue bitmask;
  // A bitmask for extracting the alpha channel from pixel data.
  uint32_t alpha_bitmask;
  // The color space type; must be LCS_CALIBRATED_RGB (0x0).
  // See: https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-wmf/eb4bbd50-b3ce-4917-895c-be31f214797f
  uint32_t color_space_type;
  CIEXYZTRIPLE color_space_endpoints;
  // Tone response curve for red in 16.16 format.
  uint32_t red_gamma;
  // Tone response curve for green in 16.16 format.
  uint32_t green_gamma;
  // Tone response curve for blue in 16.16 format.
  uint32_t blue_gamma;
};

// Contains the endpoints in a color space.
// See: https://docs.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-ciexyztriple
struct CIEXYZTRIPLE {
  CIEXYZ red;
  CIEXYZ green;
  CIEXYZ blue;
};

// The components of a color in a color space. The fields are in 2.30 form.
// See: https://docs.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-ciexyz
struct CIEXYZ {
  uint32_t x;
  uint32_t y;
  uint32_t z;
};
```
