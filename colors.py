#!/usr/bin/env python3
import numpy as np
import gfx
f = open('out')
lines = f.readlines()
f.close()

# expecting 352 x 255

img = []

for l in lines:
  l = l.strip()
  l = l[4:]
  imgline = []
  while l:
    lb = l[:2]
    hb = l[2:4]
    l = l[4:]
    lb = ord(bytes.fromhex(lb))
    hb = ord(bytes.fromhex(hb))
    for i in range(8):
      color = ((lb >> i) & 1)
      color |= ((hb >> i) & 1) * 2
      imgline.append(color)
  img.append(imgline)

img = np.asarray(img, dtype=np.uint8)
img = img[::-1,::-1]
print(np.max(img))
gfx.show(img * 80)

# vim:set sw=2 ts=2 sts=2 et tw=80:
