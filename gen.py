#!/usr/bin/env python3
"""
Generate DAI framebuffer data from an image file.
"""
import argparse
import numpy as np
from PIL import Image  # pip3 install pillow

WIDTH, HEIGHT = 352, 256

CONTROL_16COL_GFX = 0x80
CONTROL_352_COLS = 0x20

NOT_UNIT_COLOR = 0x40

def encode(img):
  control_byte = CONTROL_16COL_GFX | CONTROL_352_COLS
  color_byte = NOT_UNIT_COLOR

  # This bit pattern selects the color for every block of 8 pixels.
  # 1 = fg color, 0 = bg color
  pattern = 0b11110000

  # Set color registers. Not really important.
  out = bytes.fromhex('00 00 B5 36 00 00 AF 36 00 00 90 36 00 00 88 36')

  for y in range(HEIGHT):
    line = [control_byte, color_byte]
    sz = 8
    for x in range(0, WIDTH, sz):
      # Use fg color on the left and bg color on the right.
      fg = img[y, x:x+sz//2,:]
      bg = img[y, x+sz//2:x+sz,:]
      fg = int(np.mean(fg) / 17 + .5)
      bg = int(np.mean(bg) / 17 + .5)
      line += [pattern, (fg << 4) | bg]
    # Assemble line, reverse it, prepend it to output.
    # (the framebuffer is stored backwards)
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

  if (w,h) != (WIDTH, HEIGHT):
    # Need to resize image.
    if w / h > WIDTH / HEIGHT:
      s = WIDTH / w
    else:
      s = HEIGHT / h
    w = int(w * s + .5)
    h = int(h * s + .5)
    print(f'warn: scaling image to {w} x {h}')
    assert w <= WIDTH, w
    assert h <= HEIGHT, h
    img = img.resize((w, h), Image.BICUBIC)
    # Center.
    xo = (WIDTH - w) // 2
    yo = (HEIGHT - h) // 2
    mid = np.asarray(img)
    img = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    img[yo:yo+h, xo:xo+w, :] = mid
  else:
    img = np.asarray(img)

  out = encode(img)
  print(f'encoded {len(out)} bytes (0x{len(out):x})')

  outfn = args.outfile
  with open(outfn, 'wb') as f:
    f.write(out)

if __name__ == '__main__':
  main()

# vim:set sw=2 ts=2 sts=2 et tw=80:
