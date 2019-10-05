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

  print('info: decoding lines')
  out = []
  line_num = 1
  while data:
    # Control word, high address byte (mode byte) (manual section 3.2.1)
    mode = data[-1]
    # Bits:
    # 7, 6 - display mode control
    # 5, 4 - resolution control
    # 3, 2, 1, 0 - line repeat count
    # Disp:
    # 00 -  4 color gfx
    # 01 -  4 color chars
    # 10 - 16 color gfx
    # 11 - 16 color chars
    disp = (mode >> 6) & 3
    # Res:
    # 00 -  88 cols
    # 01 - 176 cols
    # 10 - 352 cols
    # 11 - 528 cols, text mode with 66 chars per line
    res = (mode >> 4) & 3
    line_rep = mode & 15

    # Low address byte (color byte)
    color = data[-2]
    enable_change = (color >> 7) & 1
    unit_color = 1 - ((color >> 6) & 1)  # Invert.
    color_reg = (color >> 4) & 3
    color_sel = color & 15

    print(f'line {line_num}: control {data[-2:].hex()} '
        f'| color {color:02x} enable_change {enable_change} '
        f'unit_color {unit_color} color_reg {color_reg} color_sel {color_sel} '
        f'| mode {mode:02x} disp {disp} res {res} line_rep {line_rep}')
    # Consume control word.
    data = data[:-2]
    # Determine length of line.
    if res == 2 and disp == 0 and not unit_color:
      # 2 bytes = 8 cols
      ln = 352 // 8 * 2
    elif unit_color:
      ln = 2  # FIXME: Why?
    else:
      print(data[-60:].hex())
      assert False, ('unknown mode', mode, disp, res, line_rep)
    # Consume line.
    assert len(data) >= ln, (len(data), ln)
    pixels = data[-ln:]
    data = data[:-ln]
    pixels = pixels[::-1] # Reverse.
    #print(f'line {line_num}: disp {disp} res {res} length {ln}')
    line_num += 1

    # TODO: deal with line rep
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
