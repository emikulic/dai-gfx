#!/usr/bin/env python3
import argparse
import numpy as np
from PIL import Image  # pip3 install pillow

WIDTH = 352

# Palette for 4 color gfx.
G0 = 10
G1 = 50
G2 = 100
G3 = 200
PALETTE4 = [
    [G0,G0,G0],
    [G1,G1,G1],
    [G2,G2,G2],
    [G3,G3,G3],
]

# Palette for 16 color gfx.
# Taken from src/mame/video/dai.cpp
PALETTE16 = [
    [0x00, 0x00, 0x00],  #  0 Black
    [0x00, 0x00, 0x8b],  #  1 Dark Blue
    [0xb1, 0x00, 0x95],  #  2 Purple Red
    [0xff, 0x00, 0x00],  #  3 Red
    [0x75, 0x2e, 0x50],  #  4 Purple Brown
    [0x00, 0xb2, 0x38],  #  5 Emerald Green
    [0x98, 0x62, 0x00],  #  6 Kakhi Brown
    [0xae, 0x7a, 0x00],  #  7 Mustard Brown
    [0x89, 0x89, 0x89],  #  8 Grey
    [0xa1, 0x6f, 0xff],  #  9 Middle Blue
    [0xff, 0xa5, 0x00],  # 10 Orange
    [0xff, 0x99, 0xff],  # 11 Pink
    [0x9e, 0xf4, 0xff],  # 12 Light Blue
    [0xb3, 0xff, 0xbb],  # 13 Light Green
    [0xff, 0xff, 0x28],  # 14 Light Yellow
    [0xff, 0xff, 0xff],  # 15 White
]

def cut(b, l):
  """Cut the last `l` bytes from `b`, returns the left and right parts."""
  assert len(b) >= l, (len(b), l)
  return b[:-l], b[-l:]

assert cut(b'hello', 3) == (b'he', b'llo')

def valid_dump_line(l):
  """Returns True if `l` looks like a valid UT hex dump line."""
  if len(l) < 5: return False
  if l[4] != ' ': return False
  for i in range(4):
    if l[i] not in '0123456789ABCDEF': return False
  return True

def cols_from_res(res):
  """Returns the number of columns based on the resolution number."""
  # 528 cols is also 66 chars per line in character mode.
  return [88, 176, 352, 528][res]

def mul_from_res(res):
  """Returns the width multiplier based on the resolution number."""
  return [4,2,1][res]

def get_line_len(not_unit_color, disp, res, data):
  """Returns the length of the payload for this line."""
  if not not_unit_color:
    #assert disp == 0, disp  # Doesn't hold in FFFF?
    #assert res == 0, res  # Doesn't hold. Why?
    return 2  # FIXME: Why?
  elif disp in [0, 2]:
    # 2 bytes = 8 cols
    return cols_from_res(res) // 8 * 2
  elif disp == 1 and res == 3:
    # 66 text cols * 2 bytes each
    return 66 * 2
  elif disp == 3 and res == 3:
    # FIXME: Guessing here!
    # 66 text cols * 2 bytes each
    return 66 * 2
  print('Unknown mode, trailing data is:')
  print(data[-70:].hex())
  return None

def main():
  p = argparse.ArgumentParser()
  p.add_argument('infile')
  p.add_argument('-outfile')
  args = p.parse_args()
  if args.outfile is None:
    args.outfile = args.infile + '.png'

  f = open(args.infile)
  lines = f.readlines()
  f.close()

  print('info: loading hex')
  # Example line:
  # "BFE0 00 00 00 00 00 00 00 00 00 00 00 00 00 00 40 20
  data = ''
  for l in lines:
    l = l.strip()  # Remove newline.
    if not valid_dump_line(l):
      print('ignoring line', repr(l))
      continue
    l = l.split(' ')
    addr = l.pop(0)
    assert len(addr) == 4, addr
    if addr[-1] == '0': assert len(l) == 16, l
    data += ''.join(l)
  if addr != 'BFE0':
    print(f'WARNING: last seen line starts at addr {addr}, expecting BFE0')
  data = bytes.fromhex(data)
  print(f'info: loaded {len(data)} hex bytes')

  print('info: decoding lines')
  out = []
  ascii_break = None
  line_num = 0
  prev_bg = 0  # Used in 16 color gfx mode.
  while data:
    # Control word, high address byte (mode byte) (manual section 3.2.1)
    data, mode = cut(data, 1)
    mode = mode[0]
    # Bits:
    # 7, 6 - display mode control
    # 5, 4 - resolution control
    # 3, 2, 1, 0 - line repeat count
    # Disp:
    # (0) 00 -  4 color gfx
    # (1) 01 -  4 color chars
    # (2) 10 - 16 color gfx
    # (3) 11 - 16 color chars
    disp = (mode >> 6) & 3
    # Res:
    # (0) 00 -  88 cols
    # (1) 01 - 176 cols
    # (2) 10 - 352 cols
    # (3) 11 - 528 cols, text mode with 66 chars per line
    res = (mode >> 4) & 3
    line_rep = mode & 15

    # Low address byte (color byte)
    data, color = cut(data, 1)
    color = color[0]
    enable_change = (color >> 7) & 1
    not_unit_color = (color >> 6) & 1
    color_reg = (color >> 4) & 3
    color_sel = color & 15

    print(f'line {line_num:3} row {len(out):3} '
        f'mode {mode:02x} disp {disp} res {res} '
        f'rep {line_rep} '
        f'| color {color:02x} change {enable_change} '
        f'not_unit {not_unit_color} reg {color_reg} '
        f'sel {color_sel} ', end='')
    line_len = get_line_len(not_unit_color, disp, res, data)
    print(f'| len {line_len}')
    assert line_len is not None

    # Consume line.
    data, pixels = cut(data, line_len)
    pixels = pixels[::-1] # Reverse.

    # Convert to image.
    if mode == 0x7a:
      # Decode text but just log it.
      text = pixels[0::2]
      print(' Text:', repr(text))
    elif disp == 0 and not_unit_color == 1:
      # 4 color gfx.
      out_line = []
      mul = mul_from_res(res)
      for i in range(0,len(pixels),2):
        # High and low are flipped because the payload is reversed.
        hb, lb = pixels[i], pixels[i+1]
        for bit in range(7,-1,-1):
          color = ((lb >> bit) & 1)
          color |= ((hb >> bit) & 1) * 2
          out_line.extend([PALETTE4[color]] * mul)
      assert len(out_line) == WIDTH, len(out_line)
      out.extend([out_line] * (line_rep + 1))
    elif disp == 2 and not_unit_color == 1:
      # 16 color gfx.
      out_line = []
      mul = mul_from_res(res)
      seen_1 = False
      for i in range(0,len(pixels),2):
        hb, lb = pixels[i], pixels[i+1]
        bg = lb & 15
        fg = (lb >> 4) & 15
        for bit in range(7,-1,-1):
          color = prev_bg
          if seen_1:
            color = bg
          if (hb >> bit) & 1:
            color = fg
            seen_1 = True
            prev_bg = bg
          else:
            if not seen_1:
              print(f'holdover {prev_bg} vs {bg}')
          out_line.extend([PALETTE16[color]] * mul)
        #prev_bg = bg
      assert len(out_line) == WIDTH, len(out_line)
      out.extend([out_line] * (line_rep + 1))
    elif color == 0 and mode == 0:
      # Probably unused memory: skip it.
      pass
    elif color == 0xff and mode == 0xff:
      # Probably unused memory: skip it.
      pass
    elif len(out) == 212 and mode == 0x30 and color == 0x88 and \
        ascii_break is None:
      print(f'info: decided ascii break starts on line {line_num} '
          f'after {len(out)} image rows')
      ascii_break = len(out)
    else:
      print('unimplemented')
    line_num += 1
    if len(out) >= 260:
      print('info: giving up after a full screen')
      break
  print(f'info: decoded {len(out)} lines')
  if ascii_break:
    print(f'info: fixing ascii_break at image row {ascii_break}')
    out = out[ascii_break:260] + out[:ascii_break]
  img = np.asarray(out, dtype=np.uint8)
  print(img.shape)
  im = Image.fromarray(img)#, mode='L')
  print(f'info: writing image to {args.outfile}')
  im.save(args.outfile)

if __name__ == '__main__':
  main()

# vim:set sw=2 ts=2 sts=2 et tw=80:
