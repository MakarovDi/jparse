from io import SEEK_CUR
from typing import IO, List, OrderedDict

from jparse import tools
from jparse import endianess
from jparse.JpegMarker import JpegMarker, SOI, EOI, SOS, APPn
from jparse.JpegSegment import JpegSegment
from jparse.AppSegment import AppSegment


class JpegMetaParser:

    @property
    def app_segments(self) -> OrderedDict[str, AppSegment]:
        return self._app_segments

    @property
    def image_data_offset(self) -> int:
        return self._sos.offset + self._sos.size

    @property
    def image_data_size(self) -> int:
        if self._eoi is None:
            raise RuntimeError('use JpegMetaParser(estimate_image_size=True, ...)')
        return self._eoi.offset - self._sos.offset - self._sos.size


    def __init__(self, stream: IO, estimate_image_size: bool=False):
        if 'r' not in stream.mode or 'b' not in stream.mode:
            raise RuntimeError('IO mode should be "rb"')

        self._stream = stream

        structure = scan_jpeg_structure(stream, include_eoi=estimate_image_size)
        self._structure = structure

        self._sos = None
        self._eoi = structure[-1] if structure[-1].marker == EOI else None

        self._app_segments = OrderedDict[str, AppSegment]()
        for segment in structure:
            if segment.marker == SOS:
                self._sos = segment
            elif APPn.check_mask(segment.marker.signature):
                self._app_segments[segment.marker.name.upper()] = segment



def scan_jpeg_structure(stream: IO, include_eoi: bool) -> List[JpegSegment]:
    offset = stream.tell()

    check_jpeg_signature(stream)
    segment = JpegSegment.create(marker=SOI, stream=stream, offset=offset, size=JpegMarker.MARKER_SIZE)
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

        segment = JpegSegment.create(marker=segment_marker, stream=stream, offset=offset, size=segment_size)
        segment.log()
        structure.append(segment)

        offset += segment_size
        stream.seek(segment_size - JpegMarker.MARKER_SIZE - JpegMarker.LENGTH_SIZE, SEEK_CUR)

        if segment_marker == SOS:
            break

        segment_marker = stream.read(JpegMarker.MARKER_SIZE)

    if include_eoi:
        eoi_offset = scan_for_eoi(stream)
        if eoi_offset == 0:
            raise RuntimeError('EOI is not found')

        segment = JpegSegment.create(marker=EOI, stream=stream, offset=offset + eoi_offset, size=JpegMarker.MARKER_SIZE)
        segment.log()
        structure.append(segment)

    return structure


def check_jpeg_signature(stream: IO):
    marker = tools.read_bytes_strict(stream, JpegMarker.MARKER_SIZE)
    marker = endianess.convert_big_endian(marker)

    if marker != SOI.signature:
        raise RuntimeError('file is not JPEG')


def scan_for_eoi(stream: IO) -> int:
    offset = 0

    while True:
        marker = stream.read(1)
        if len(marker) < 1:
            return 0  # not found

        offset += 1
        if marker[0] != JpegMarker.START:
            continue

        marker = stream.read(1)
        if len(marker) < 1:
            return 0  # not found

        if marker[0] == (EOI.signature & 0xFF):
            return offset -1

        offset += 1

    return 0