#!/usr/bin/env python

import imghdr
import struct

# Map of imghdr type string to sizing function
SIZE = {}

def size(fname):
    '''
    Return a dict of data about a file if we can determine its file type.

    fname::
        Either a filename str, or a file object.

    Returns::
        dict() of details with at least 'width', 'height', and 'type'.
        None if type is not known.
    '''
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


def size_tiff(fin):
    hdr = fin.read(8)
    end = '<' if hdr[:2] == 'II' else '>'

    # width is tag 256
    # height is tag 257
    width = height = None

    ifd = struct.unpack(end + 'I', hdr[4:8])[0]
    while (width is None and height is None) or ifd == 0:
        fin.seek(ifd)
        count = struct.unpack(end + 'H', fin.read(2))[0]
        while count:
            count -= 1
            entry = fin.read(12)
            tag, size, vals, offset = struct.unpack(end + 'HHII', entry)
            if tag == 256:
                vals = read_tag(fin, end, size, vals, offset)
                width = vals[0]
            elif tag == 257:
                vals = read_tag(fin, end, size, vals, offset)
                height = vals[0]

        ifd = struct.unpack(end + 'I', fin.read(4))

    return {'width': width, 'height': height}


def read_tag(fin, end, size, vals, offset):
    '''Read and decode a TIFF tag's data'''
    sfmt = end + ''.join(['H' if size == 3 else 'I'] * vals)
    bcount = struct.calcsize(sfmt)
    if bcount <= 4:
        # Special case -- data are in offset
        result = struct.unpack(sfmt, struct.pack(end + 'I', offset)[:bcount])
    else:
        pos = fin.tell()
        fin.seek(offset)
        result = struct.unpack(sfmt, fin.read(bcount))
        fin.seek(pos)
    return result


SIZE['tiff'] = size_tiff

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
