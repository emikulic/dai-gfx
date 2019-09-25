#!/usr/bin/env python3
import argparse

def main():
  p = argparse.ArgumentParser()
  p.add_argument('infile')
  p.add_argument('outfile')
  args = p.parse_args()

  f = open(args.infile)
  d = f.readlines()
  f.close()
  h = ''
  for l in d:
    l = l.strip()
    l = l[5:]
    h += ''.join(l.split())
  h = h.split('4020')
  assert len(h[0]) >= 176, len(h[0])
  h[0] = h[0][-176:]
  assert len(h[-1]) == 0, h[-1]
  h = h[:-1]

  # find non-image data
  idx = None
  for i, l in enumerate(h):
    if len(l) > 1000:
      idx = i
      break
  assert idx is not None

  h = h[idx+1:] + h[:idx]
  for l in h:
    if len(l) == 176:
      print(l)

#!/usr/bin/env python3
import numpy as np
from PIL import Image  # pip3 install pillow

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
  img *= (255//3)

  im = Image.fromarray(img, mode='L')
  im.save('out.png')

# vim:set sw=2 ts=2 sts=2 et tw=80:
if __name__ == '__main__':
  main()

# vim:set sw=2 ts=2 sts=2 et tw=80:
