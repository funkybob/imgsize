import imghdr
import struct


SIZE = {}


def size(fname):
    with open(fname, 'rb') as fin:
        t = imghdr.what(fname)
        try:
            func = SIZE[t]
        except KeyError:
            return
        return dict(func(fin), type=t)


def size_jpeg(fin):
    soi = fin.read(2)
    assert soi == '\xff\xd8'
    while True:  # Find the SOFx block
        mkr, ll = struct.unpack('!2sH', fin.read(4))
        assert mkr[0] == '\xff'
        data = fin.read(ll - 2)
        if mkr[1] not in {'\xc0', '\xc1', '\xc2', '\xc3', '\xc5', '\xc6',
                          '\xc7', '\xc9', '\xca', '\xcb', '\xcd', '\xce',
                          '\xcf'}:
            continue
        bps, height, width = struct.unpack('!cHH', data[:5])
        break
    return {
        'width': width,
        'height': height,
    }

SIZE['jpeg'] = size_jpeg


def size_png(fin):
    fin.read(8)  # Skip the Magick Numbers
    # First chunk MUST be IHDR
    clen, ctype = struct.unpack('!I4s', fin.read(8))
    assert ctype == 'IHDR'
    data = fin.read(clen)
    fin.read(4)  # CRC
    w, h, d, ct, comp, filt, ilace = struct.unpack('!IIccccc', data)
    return {
        'width': w,
        'height': h,
        'depth': ord(d),
    }

SIZE['png'] = size_png


def size_gif(fin):
    fin.read(6)  # Skip the Magick Numbers
    width, height = struct.unpack('<HH', fin.read(4))
    return {
        'width': width,
        'height': height,
    }

SIZE['gif'] = size_gif


# TIFF
def size_tiff(fin):
    endian = fin.read(2)  # II = Intel, MM = Motorola
    return

# SGI RGB


# PBM
# PGM
# PPM
def size_pnm(fin):
    fin.read(2)  # Skip the Magick Numbers
    c = fin.read(1)
    assert c.isspace()
    # XXX Remember to skip lines starting with # after a newline
    while c.isspace():
        c = fin.read(1)
    width = []
    while not c.isspace():
        width.append(c)
        c = fin.read(1)
    width = int(''.join(width))
    while c.isspace():
        c = fin.read(1)
    height = []
    while not c.isspace():
        height.append(c)
        c = fin.read(1)
    height = int(''.join(height))

    return {'width': width, 'height': height}

SIZE['pbm'] = size_pnm
SIZE['pgm'] = size_pnm
SIZE['ppm'] = size_pnm


# SUN Raster
# XBM
# BMP

if __name__ == '__main__':
    import sys

    for name in sys.argv[1:]:
        info = size(name)
        if not info:
            print("{}: Unknown".format(name))
        else:
            print("{}: {} {} x {} ({})".format(name,
                                               info['type'],
                                               info['width'],
                                               info['height'],
                                               info))
