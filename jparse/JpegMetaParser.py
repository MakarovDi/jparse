from io import SEEK_CUR
from typing import IO

from jparse import tools
from jparse import endianess
from jparse.JpegMarker import JpegMarker, SOI, EOI, SOS
from jparse.JpegSegment import JpegSegment


class JpegMetaParser:

    def __init__(self, stream: IO):
        if 'r' not in stream.mode or 'b' not in stream.mode:
            raise RuntimeError('IO mode should be "rb"')

        self._stream = stream
        self._structure = scan_jpeg_structure(stream)



def scan_jpeg_structure(stream: IO) -> list:
    offset = stream.tell()

    check_jpeg_signature(stream)
    segment = JpegSegment(marker=SOI, stream=stream, offset=offset, size=JpegMarker.MARKER_SIZE)
    segment.log()
    structure = [ segment ]

    offset += JpegMarker.MARKER_SIZE

    # scan segments

    segment_marker = stream.read(JpegMarker.MARKER_SIZE)
    while len(segment_marker) == JpegMarker.MARKER_SIZE:
        segment_marker = endianess.convert_big_endian(segment_marker)
        segment_marker = JpegMarker.detect(segment_marker)

        if segment_marker == EOI:
            raise RuntimeError('unexpected EOI marker before SOS marker')

        segment_size = tools.read_bytes_strict(stream, JpegMarker.LENGTH_SIZE)
        segment_size = endianess.convert_big_endian(segment_size) + JpegMarker.MARKER_SIZE

        segment = JpegSegment(marker=segment_marker, stream=stream, offset=offset, size=segment_size)
        segment.log()
        structure.append(segment)

        offset += segment_size
        stream.seek(segment_size - JpegMarker.MARKER_SIZE - JpegMarker.LENGTH_SIZE, SEEK_CUR)

        if segment_marker == SOS:
            break

        segment_marker = stream.read(JpegMarker.MARKER_SIZE)

    return structure


def check_jpeg_signature(stream: IO):
    marker = tools.read_bytes_strict(stream, JpegMarker.MARKER_SIZE)
    marker = endianess.convert_big_endian(marker)

    if marker != SOI.signature:
        raise RuntimeError('file is not JPEG')