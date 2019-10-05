#!/usr/bin/env python3
import argparse
import numpy as np
from PIL import Image  # pip3 install pillow

def main():
  p = argparse.ArgumentParser()
  p.add_argument('infile')
  p.add_argument('outfile')
  args = p.parse_args()

  f = open(args.infile)
  lines = f.readlines()
  f.close()

  print('info: loading hex')
  # Example line:
  # "BFE0 00 00 00 00 00 00 00 00 00 00 00 00 00 00 40 20
  data = ''
  for l in lines:
    l = l.strip()  # Remove newline.
    l = l.split(' ')
    addr = l.pop(0)
    assert len(addr) == 4, addr
    if addr[-1] == '0': assert len(l) == 16, l
    data += ''.join(l)
  assert addr == 'BFE0', ('last seen addr', addr)
  data = bytes.fromhex(data)
  print(f'info: loaded {len(data)} hex bytes')

  print(data)
  die
  h = h.split('4020')
  assert len(h[0]) >= 176, len(h[0])
  h[0] = h[0][-176:]
  assert len(h[-1]) == 0, h[-1]
  h = h[:-1]

  # find non-image data
  idx = None
  for i, l in enumerate(h):
    if len(l) != 176:
      print(f'line {i} has weird length {len(l)}')
    if len(l) > 1000:
      idx = i
      break
  print(f'non image data is line {idx}')
  assert idx is not None

  # Rotate.
  h = h[idx+1:] + h[:idx]

  # Expecting 352 x 255
  img = []

  for i,l in enumerate(h):
    if len(l) != 176:
      #print(f'line {i} has bad length {len(l)}')
      continue

    l = l.strip()
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
  im.save(args.outfile)

if __name__ == '__main__':
  main()

# vim:set sw=2 ts=2 sts=2 et tw=80:
