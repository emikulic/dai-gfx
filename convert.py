#!/usr/bin/env python3
import argparse

def main():
  p = argparse.ArgumentParser()
  p.add_argument('infile')
  p.add_argument('outfile')
  args = p.parse_args()

f = open('tani.txt')
d = f.readlines()
f.close()
h = ''
for l in d:
  l = l.strip()
  l = l[5:]
  h += ''.join(l.split())

h = h.split('00004020')

for l in h:
  print(l)

if __name__ == '__main__':
  main()

# vim:set sw=2 ts=2 sts=2 et tw=80:
