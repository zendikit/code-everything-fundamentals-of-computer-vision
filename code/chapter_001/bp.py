#!/usr/bin/python3 -B

# Bitmap parser. Parses only V4 grayscale images.

import argparse
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
        self.pixel_data_offset_bytes = struct.unpack_from("<HIHHI", data, offset=offset)

    def __str__(self):
        magic_byte_1 = chr(self.file_type & 0xff)
        magic_byte_2 = chr((self.file_type & 0xff00) >> 8)
        return f"File type        : {magic_byte_1}{magic_byte_2}\n" +\
               f"Size             : {self.size_bytes} bytes\n" +\
               f"Pixel data offset: {self.pixel_data_offset_bytes} bytes"

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
        self.color_space_type = struct.unpack_from("<IiiHHIIiiIIIIIII", data, offset=offset)

        self.color_space_endpoints = CIEXYZTriple(data, offset + 60)

        red_gamma, \
        green_gamma, \
        blue_gamma = struct.unpack_from("<III", data, offset=offset + 96)

        self.red_gamma = red_gamma / 2**30
        self.green_gamma = green_gamma / 2**30
        self.blue_gamma = blue_gamma / 2**30

    def __str__(self):
        return f"Size                     : {self.size_bytes} bytes\n" +\
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


def main():
    parser = argparse.ArgumentParser(description="Limited-functionality bitmap parser")
    parser.add_argument("image", help="An image file pathname")
    args = parser.parse_args()

    with open(args.image, "rb") as f:
        data = f.read()

    image = BitmapV4(data)
    print(image)


if __name__ == "__main__":
    main()
