#!/usr/bin/env python3
"""Cut a subject out of its background and fill the hole behind it (two layers for a project).
  python tools/cutout.py photo.jpg --size 600x800 --rect 150,100,500,715 --out examples/name \\
      [--poly "x,y;x,y;..."]  rough outline of the subject (optional, helps a lot)
      [--fg "x,y;x,y;x,y@30"] polyline of pixels that are DEFINITELY subject, @width (repeatable; trace limbs, head, torso)
Writes <out>-char.webp (RGBA subject) and <out>-bg.jpg (background, hole filled).
Always open the two files and look. If the cutout leaks or misses parts, add more --fg lines and re-run.
Needs: pip install opencv-python pillow numpy"""
import argparse, cv2, numpy as np
from PIL import Image
a = argparse.ArgumentParser(); a.add_argument("image"); a.add_argument("--size", required=True); a.add_argument("--rect", required=True)
a.add_argument("--poly"); a.add_argument("--fg", action="append", default=[]); a.add_argument("--out", required=True); a = a.parse_args()
W, H = map(int, a.size.lower().split("x")); im = cv2.resize(cv2.imread(a.image), (W, H), interpolation=cv2.INTER_AREA)
x0, y0, x1, y1 = map(int, a.rect.split(","))
pts = lambda s: np.array([[int(v) for v in p.split(",")] for p in s.split(";")], np.int32)
m = np.full((H, W), cv2.GC_BGD, np.uint8); m[y0:y1, x0:x1] = cv2.GC_PR_BGD
if a.poly: cv2.fillPoly(m, [pts(a.poly)], cv2.GC_PR_FGD)
elif not a.fg:
    dx, dy = (x1 - x0) // 6, (y1 - y0) // 6; m[y0 + dy:y1 - dy, x0 + dx:x1 - dx] = cv2.GC_PR_FGD
for s in a.fg:
    p, w = (s.split("@") + ["30"])[:2]; cv2.polylines(m, [pts(p)], False, cv2.GC_FGD, int(w))
cv2.grabCut(im, m, None, np.zeros((1, 65)), np.zeros((1, 65)), 10, cv2.GC_INIT_WITH_MASK)
fg = ((m == cv2.GC_FGD) | (m == cv2.GC_PR_FGD)).astype(np.uint8)
n, l, st, _ = cv2.connectedComponentsWithStats(fg); fg = (l == 1 + np.argmax(st[1:, 4])).astype(np.uint8)
fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
c, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE); fg = np.zeros_like(fg); cv2.drawContours(fg, c, -1, 1, -1)
big = cv2.dilate(fg, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
bg = cv2.inpaint(im, big * 255, 9, cv2.INPAINT_TELEA).astype(np.float32)
g = cv2.GaussianBlur(np.random.default_rng(1).normal(0, 14, (H, W)).astype(np.float32), (0, 0), 1.2)
bg = np.clip(np.where((big > 0)[..., None], bg + g[..., None], bg), 0, 255).astype(np.uint8)
cv2.imwrite(a.out + "-bg.jpg", bg, [cv2.IMWRITE_JPEG_QUALITY, 82])
al = cv2.GaussianBlur(cv2.erode(fg, np.ones((3, 3), np.uint8)).astype(np.float32), (0, 0), 0.9)
Image.fromarray(cv2.cvtColor(np.dstack([im, (al * 255).astype(np.uint8)]), cv2.COLOR_BGRA2RGBA)).save(a.out + "-char.webp", quality=88, method=6)
print(f'wrote {a.out}-char.webp and {a.out}-bg.jpg; project: "image", "background", "size": [{W}, {H}]')
