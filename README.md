# Imgsize - sizing to match imghdr

Python provides you a file type detection library using `imghdr`, but it will
only guess the type.

This library goes a step further, determining the pixel dimensions of an image,
based on the type determined by imghdr.

## Usage:

    >>> import sizeof

    >>> data = sizeof.this('myimage.png')
    >>> print(data)
    {'width': 32, 'height': 64, 'type': 'png', 'depth': 8}

    >>> with open('unknown.txt', 'rb') as fin:
    ...     data = sizeof.this(fin)
    ...
    >>> print(data)
    None

## Supported Formats

Currently the following formats are supported:

- JPEG
- PNG
- GIF
- TIFF
- PNM (PBM, PGM, PPM) *

* Currently does not support comments

The `imghdr` library also recognises:

- SGI RGB
- SUN Raster
- XBM
- BMP
