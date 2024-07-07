from typing import IO
from jparse import endianess
from jparse.JpegMarker import JpegMarker, EOI, SOI


def align4(addr: int) -> int:
    addr += (4 - (addr & 0x3)) & 0x3
    return addr


def read_bytes_strict(stream: IO, count: int) -> bytes:
    data = stream.read(count)

    if len(data) != count:
        raise RuntimeError('unexpected end of stream')
    
    return data


def parse_app_name(stream: IO) -> str:
    name = ''

    while True:
        byte = read_bytes_strict(stream, 1)

        if byte[0] == 0x00:
            break

        name += byte.decode('ascii')

    return name


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


def read_jpeg_signature(stream: IO):
    marker = read_bytes_strict(stream, JpegMarker.MARKER_SIZE)
    marker = endianess.convert_big_endian(marker)

    if marker != SOI.signature:
        raise RuntimeError('file is not JPEG')