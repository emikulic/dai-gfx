#!/usr/bin/env python3
import argparse
import numpy as np
from PIL import Image  # pip3 install pillow
import decode

WIDTH, HEIGHT = 352, 256

def encode(img):
  # Set color registers. Not really important.
  out = bytes.fromhex('00 00 B5 36 00 00 AF 36 00 00 90 36 00 00 88 36')

  for y in range(HEIGHT):
    # 16 color gfx, 352 cols
    line = [0xA0, 0x40]
    sz = 8
    for x in range(0, WIDTH, sz):
      pixels = img[y, x:x+sz,:]
      gray = np.mean(pixels)
      gray = int(gray / 17 + .5)
      line += [0xff, gray << 4]
    # Assemble line, reverse it, add it to output.
    line = bytes(line[::-1])
    out = line + out
  return out

def main():
  p = argparse.ArgumentParser()
  p.add_argument('infile')
  p.add_argument('outfile')
  args = p.parse_args()

  fn = args.infile
  print(f'info: loading from {fn}')
  img = Image.open(fn)
  w,h = img.size
  print(f'info: loaded {w} x {h} image')

  # TODO: keep aspect
  img = img.resize((WIDTH, HEIGHT), Image.BICUBIC)
  img = np.asarray(img)

  out = encode(img)
  print(f'encoded {len(out)} bytes (0x{len(out):x})')

  outfn = args.outfile
  with open(outfn, 'wb') as f:
    f.write(out)

if __name__ == '__main__':
  main()

# vim:set sw=2 ts=2 sts=2 et tw=80:
