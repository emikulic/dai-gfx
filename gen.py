#!/usr/bin/env python3
"""
Generate DAI framebuffer data from an image file.
"""
import argparse
import numpy as np
from PIL import Image  # pip3 install pillow

WIDTH, HEIGHT = 352, 256

CONTROL_16COL_GFX = 0x80
CONTROL_TEXT_MODE = 0x30
CONTROL_352_COLS = 0x20

NOT_UNIT_COLOR = 0x40

def colort(c1, c2, c3, c4, line_rep = 6):
  """
  Emit list of color change instructions.
  """
  control = CONTROL_TEXT_MODE | line_rep
  return [
      bytes([control, 0x80 | c1, 0, 0]),
      bytes([control, 0x90 | c2, 0, 0]),
      bytes([control, 0xA0 | c3, 0, 0]),
      bytes([control, 0xB0 | c4, 0, 0]),
  ]

def encode(img):
  """
  Encodes image, returns an array of per-line memory chunks, in forward order.
  """
  control_byte = CONTROL_16COL_GFX | CONTROL_352_COLS
  color_byte = NOT_UNIT_COLOR

  # This bit pattern selects the color for every block of 8 pixels.
  # 1 = fg color, 0 = bg color
  pattern = 0b11110000

  out = []
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
    out.append(bytes(line))
  return out

def encode_text(t):
  """
  Returns a memory chunk (in forward order) encoding a line of text.
  If the line is too long, it gets truncated.
  """
  if type(t) is bytes: t = str(t)
  t = '    ' + t + ' ' * 66
  t = t[:66].encode()
  t = b''.join([bytes([c, 0]) for c in t])
  return bytes([0x7a, 0x40]) + t

def insert_text(lst, text, fn, mode):
  """
  Add text section to encoder output.
  """
  color_regs = lst[:4]
  top = lst[4:4+44]
  bottom = lst[4+44:]

  text += [f'{fn} {mode}', '', '', '']
  text = text[:4]

  return (
      color_regs +
      bottom +
      colort(8, 0, 0, 8, line_rep=0) +
      list(map(encode_text, text)) +
      colort(8, 0, 0, 8, line_rep=15) +
      top)

def main():
  p = argparse.ArgumentParser()
  p.add_argument('infile')
  p.add_argument('outfile')
  p.add_argument('-text', default=None, type=str,
    help='file to load text insert from')
  args = p.parse_args()

  text = []
  if args.text is not None:
    with open(args.text) as f:
      text = f.read().splitlines()

  fn = args.infile
  print(f'info: loading from {fn}')
  img = Image.open(fn)
  w,h = img.size
  print(f'info: loaded {w} x {h} image')
  img = img.convert(mode='RGB')

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

  out = colort(8, 0, 15, 5) + encode(img)
  out = insert_text(out, text, args.infile, 'MODE 5A')

  # Join into one run.
  out = b''.join(out)
  # The framebuffer is in reverse order.
  out = out[::-1]
  print(f'encoded {len(out)} bytes (0x{len(out):x})')

  outfn = args.outfile
  with open(outfn, 'wb') as f:
    f.write(out)

if __name__ == '__main__':
  main()

# vim:set sw=2 ts=2 sts=2 et tw=80:
