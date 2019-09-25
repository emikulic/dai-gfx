#!/usr/bin/env python3
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

# vim:set sw=2 ts=2 sts=2 et tw=80:
