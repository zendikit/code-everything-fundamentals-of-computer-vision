# Parsing Pixel Data

## Implementation

As mentioned in [Challenge](./challenge.md), we will produce a PGM image to visualize our parsed pixels. We extend our tool we made in the previous
[Implementation](../parsing_image_metadata/implementation.md) by adding a new optional command-line argument, `--pgm-outdir`. If the user specifies this, we convert the specified bitmap image into a PGM
image. Otherwise, we print the file metadata as we did previously. Below we show the changes to `main()` interleaved with our previous code.

```python
import os

# ...

def main():
    parser = argparse.ArgumentParser(
            description="Limited-functionality bitmap parser")
    parser.add_argument("image", help="An image file pathname")
    parser.add_argument("--pgm-outdir",
            help="A path to a directory to write a PGM output file into")
    args = parser.parse_args()

    with open(args.image, "rb") as f:
        data = f.read()

    image = BitmapV4(data)

    if args.pgm_outdir:
        os.makedirs(args.pgm_outdir, exist_ok=True)
        with open(os.path.join(args.pgm_outdir, "image.pgm"), "w") as f:
            f.write(image.as_pgm())
    else:
        print(image)
```

`BitmapV4.as_pgm` is straightforward, the only trick here being that we iterate over the number of rows (the height) in reverse if the height is positive.

```python
class BitmapV4:
    def __init__(self, data):
        # ...
        self.pixels = list(data[self.file_header.pixel_data_offset_bytes:])

    def as_pgm(self):
        """
        Return an ASCII string encoding this iamge as a PGM.
        """
        width = self.info_header.width_px
        height = self.info_header.height_px

        pgm = "P2\n"
        pgm += f"{width} {height}\n"
        pgm += f"{self.info_header.num_colors_required - 1}\n"

        # If the pixel array is stored bottom-up, we reverse its rows.
        height_iter = reversed(range(height)) if height > 0 else range(height)
        for h in height_iter:
            for pixel in range(h * width, h * width + width):
                pgm += f"{self.pixels[pixel]}\n"
        return pgm
```

We can view our new image to confirm that we converted the grayscale bitmap V4 to a PGM correctly.

```sh
$ ./bp.py --pgm-outdir /tmp test/data/2021-02-22-tokyo-skytree-grayscale.bmp
# `eog` means Eye of Gnome and is the default image viewer in Ubuntu.
$ eog /tmp/image.pgm
```
