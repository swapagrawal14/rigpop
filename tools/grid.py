#!/usr/bin/env python3
"""Draw a labelled coordinate grid on an image so you can read joint positions off it.
  python tools/grid.py photo.jpg --size 600x800 --out grid.png [--step 50]
The grid uses the SAME pixel space as the project's "size". Open grid.png and read x/y from it."""
import argparse
from PIL import Image, ImageDraw
a = argparse.ArgumentParser(); a.add_argument("image"); a.add_argument("--size"); a.add_argument("--out", default="grid.png"); a.add_argument("--step", type=int, default=50)
a = a.parse_args()
im = Image.open(a.image).convert("RGB")
if a.size: w, h = map(int, a.size.lower().split("x"))
else: s = min(1, 800 / max(im.size)); w, h = round(im.width * s), round(im.height * s)
im = im.resize((w, h)); d = ImageDraw.Draw(im)
for x in range(0, w, a.step):
    d.line([(x, 0), (x, h)], fill=(255, 255, 0) if x % (a.step * 2) == 0 else (255, 255, 255), width=1); d.text((x + 2, 2), str(x), fill=(0, 0, 0))
for y in range(0, h, a.step):
    d.line([(0, y), (w, y)], fill=(255, 255, 0) if y % (a.step * 2) == 0 else (255, 255, 255), width=1); d.text((2, y + 2), str(y), fill=(0, 0, 0))
im.save(a.out); print(f'wrote {a.out}; use "size": [{w}, {h}] in the project')
