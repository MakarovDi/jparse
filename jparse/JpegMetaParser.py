from typing import IO

from jparse import tools
from jparse import endianess
from jparse.JpegMarker import JpegMarker, SOI


class JpegMetaParser:

    def __init__(self, stream: IO):
        if 'r' not in stream.mode or 'b' not in stream.mode:
            raise RuntimeError('IO mode should be "rb"')

        self._stream = stream
        self._structure = scan_jpeg_structure(stream)



def scan_jpeg_structure(stream: IO) -> list:
    offset = stream.tell()

    check_jpeg_signature(stream)
    structure = [ SOI ]

    offset += JpegMarker.MARKER_SIZE

    return structure


def check_jpeg_signature(stream: IO):
    marker = tools.read_bytes_strict(stream, JpegMarker.MARKER_SIZE)
    marker = endianess.convert_big_endian(marker)

    if marker != SOI.signature:
        raise RuntimeError('file is not JPGE')