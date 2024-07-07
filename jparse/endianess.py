import struct
from enum import Enum

class ByteOrder(Enum):
    LITTLE_ENDIAN = '<'
    BIG_ENDIAN = '>'


TYPE_STR_MAPPING: dict[int, chr] = { 1: 'B', 2: 'H', 4: 'I' }


def convert(data: bytes, byte_order: ByteOrder) -> int:
    byte_cnt = len(data)
    assert byte_cnt in (1, 2, 4), 'unsupported data size'

    # Note: faster than byte_order.value
    byte_order = '<' if byte_order == ByteOrder.LITTLE_ENDIAN else '>'
    format_str = TYPE_STR_MAPPING[byte_cnt]

    result = struct.unpack(f'{byte_order}{format_str}', data)
    return int(result[0])


def convert_big_endian(data: bytes) -> int:
    return convert(data=data, byte_order=ByteOrder.BIG_ENDIAN)


def convert_little_endian(data: bytes) -> int:
    return convert(data=data, byte_order=ByteOrder.LITTLE_ENDIAN)