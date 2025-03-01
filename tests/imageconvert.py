#!/usr/bin/env python3

from PIL import Image
import sys
import argparse

parser = argparse.ArgumentParser(description="RGB888 to PNG converter")
parser.add_argument("file", help="file/s name", nargs="*")

args = parser.parse_args()

for file in args.file:
    with open(file, "rb") as ff:
        w, h, cs = ff.readline().split(b":")
        width, height = int(w.decode()), int(h.decode())
        frame = ff.read()
        assert len(frame) == width * height * int(cs)

    image = Image.new("RGB", (width, height))
    image.frombytes(frame)
    image.save(file.replace(".bin", ".png"), "PNG")
    image.close()
