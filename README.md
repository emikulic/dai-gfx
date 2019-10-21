# dai-gfx

Decoder for DAInamic framebuffer data in UT hex dump format.

Quickstart:
```shell
./decode.py monalisa.txt
```

This will produce:
 * `monalisa.txt.png` - image decoded from hex data
 * `monalisa.txt.bin` - unhexed (binary) data

The generator script can be used to produce binary data from an image file.
e.g.:
```shell
./gen.py photo.jpg photo.bin
```
