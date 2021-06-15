<style>
.bordered {
  border: 1px solid;
}
.square {
  width: 20px;
  height: 20px;
}
.black { background: #000000; }
.red { background: #ff0000; }
.green { background: #00ff00; }
.blue { background: #0000ff; }
.yellow { background: #ffff00; }
.cyan { background: #00ffff; }
.purple { background: #ff00ff; }
.white { background: #ffffff; }
.light-blue { background: #55aaff; }
</style>

# About Images

## Images

Images are our fundamental input in this text. Image files contain (1) metadata
about the image and (2) pixel data. Metadata includes properties such as the
dimensions of the image and the binary format the pixel data is stored in.
"Pixel" is a combination of the word "picture" and "element" and describes the
smallest renderable element in an image. A 640x480 image is 640 pixels wide by
480 pixels tall. Each pixel in the pixel data describes its renderable element
in terms of a combination of intensities of fundamental colors (like amount of red, green, and blue) or properties (like hue, saturation, and value).

Right now, let's consider pixels that encode color information using fundamental colors. The fundamental colors come from a color model. A color model defines a way to
represent a color in a spectrum by combining intensities of a select few colors,
the fundamental colors of the model. Some popular color models are RGB (red,
green, blue) and CMY (cyan, magenta, yellow), in this case named after their
fundamenal colors.

## Color Representation

Let's explore color representation more deeply. Consider the RGB color model.
This model represents white as a combination of maximum intensities of all three
fundamental colors. If we represent the intensities in a tuple-like form of
`(%R, %G, %B)` with each element in the range `[0.0, 1.0]`, white would be
`(1.0, 1.0, 1.0)`. Black is the absence of any color, in this case
`(0.0, 0.0, 0.0)`.

With a representation like this, one that uses percentages of arbitrary
precision, our color spectrum is technically infinitely wide, since
`(0.1, 0.0, 0.0)`, `(0.01, 0.0, 0.0)`, `(0.001, 0.0, 0.0)`, etc. all specify
unique colors. We don't usually represent colors like this in files on our computers
though. The reasons are numerous, but two important ones are that (1) for a
variety of purposes far more efficient representations of intensities meet our
needs and (2) after some point humans can no longer visually distinguish between
two subtly-different shades of color, and therefore having the ability to encode
those unique colors is moot if we are only interested in casual visual
consumption.

We make our spectrum of colors finite by representing intensities with integers
in some bounded domain. For example, if we only allow fundamental colors to be
zero intensity or maximum intensity, our range is `[0, 1]`. The possible colors
using the RGB color model are then:

| `(R, G, B)` | Color                                     | English Name |
| ----------- | ----------------------------------------- | ------------ |
| `(0, 0, 0)` | <div class="black square"></div>          | Black        |
| `(1, 0, 0)` | <div class="red square"></div>            | Red          |
| `(0, 1, 0)` | <div class="green square"></div>          | Green        |
| `(0, 0, 1)` | <div class="blue square"></div>           | Blue         |
| `(1, 1, 0)` | <div class="yellow square"></div>         | Yellow       |
| `(0, 1, 1)` | <div class="cyan square"></div>           | Cyan         |
| `(1, 0, 1)` | <div class="purple square"></div>         | Purple       |
| `(1, 1, 1)` | <div class="white bordered square"></div> | White        |

Using this scheme, we can represent a pixel using only 3 bits. In other words,
our representation is **3 bits per pixel (bpp)**. Each element `R`, `G`, and `B`
is called a color channel, so we have a **1 bit per channel (bpc)**
representation.

If we represented a 640x480 image using this scheme, the pixel data would
consume

```math
\dfrac {640 \cdot 480 \text { pixels} \cdot 3 \text { bpp}}{8 \text { bits per byte}} = 115,200 \text { bytes}
```

or approximately 115 kB worth of space, uncompressed. If we were to have used
high-precision floating-point numbers, such as a 64-bit `double` in C or C++
parlance, for each channel intensity value to represent them as precise
percentages, our image would consume 64 times more space, roughly 7.4 MB!

With our 3 bpp scheme, we have only 2 choices (`1` or `0`) for each channel of a
pixel, giving us a total of

```math
2^{\text {bpp}} = 2^{\text {bpc } \cdot \text { num channels}} = 2^{1 \cdot 3} = 2^{3} = 8
```

unique colors. If we instead used 24 bpp, our spectrum would contain over 16
million colors, and the hypothetical 640x480 image would be approximately 921
kB.

The below image simulates--by limiting the color palette--the effect various
bit-per-pixel values may have on rendering a particular image. From left to
right: 128 colors, 64 colors, 32 colors, and finally 16 colors.

![Tokyo Skytree rendered at various color palette depths](../assets/img/2021-05-01-skytree-various-color-tables.jpg)

## Interpreting Pixel Values

Although we don't represent channel intensity values directly as percentages,
they are implicit fractions. Using an 8 bpc scheme, the possible intensity
values are between

```math
\left[0,\ 2^{\text {bpc}} - 1\right] = \left[0,\ 2^{8} - 1\right] = \left[0, 255\right]
```

If our color mode is RGB, we can mentally visualize the pixel `(85, 170, 255)`
as being

```math
\left[\frac{r}{2^{\text {bpc}} - 1}, \frac{g}{2^{\text {bpc}} - 1}, \frac{b}{2^{\text {bpc}} - 1}\right] =
\left[\frac{85}{2^{8} - 1}, \frac{170}{2^{8} - 1}, \frac{255}{2^{8} - 1}\right] \approx
\left[0.3, 0.6, 1.0\right]
```

which is a little bit of red, a moderate ammount of green, and a lot of blue,
yielding the color below.

| `(R, G, B)`       | Color                                 | English Name |
| ----------------- | ------------------------------------- | ------------ |
| `(0.3, 0.6, 1.0)` | <div class="light-blue square"></div> | Light Blue   |

## Image Metadata

If we encounter the pixel data `(1, 2, 3, 4)` in the wild, how do we interpret
it? For example, what is this new fourth element that we haven't dealt with yet?
Are the elements RGBA intensities, or maybe CMYK, or something else? The pixel
data is valid using a 3 bpc / 12 bpp scheme, but does that scheme really give us
the intended upper limits? The pixel is also valid (but semantically different)
if interpretted using an 8 bpc / 32 bpp scheme.

Image metadata answers all of these questions for us and in general teaches us
how to interpret not only an image's pixel data but even other parts of its
metadata. As we know, there are multiple popular image file formats (for
example, bitmaps, JPEG, and PNG) in circulation today. Most image formats have
their own metadata schema, and many of those schemas have multiple schema
versions as a result of their filetypes evolving over the years. This alone
makes parsing images nontrivial. We will experience this firsthand in the next
section.
