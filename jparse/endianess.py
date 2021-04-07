import struct
from enum import IntEnum
from functools import partial


class ByteOrder(IntEnum):
    LITTLE_ENDIAN = 0
    BIG_ENDIAN    = 1

    @property
    def unpack_format_chr(self) -> chr:
        return { ByteOrder.LITTLE_ENDIAN: '<', ByteOrder.BIG_ENDIAN: '>' }[self]



def convert(data: bytes, byte_order: ByteOrder) -> int:
    byte_cnt = len(data)
    assert byte_cnt in (1, 2, 4), 'unsupported data size'

    format_str = { 1: 'B', 2: 'H', 4: 'I' }[byte_cnt]
    result = struct.unpack(f'{byte_order.unpack_format_chr}{format_str}', data)

    return int(result[0])



convert_big_endian = partial(convert, byte_order=ByteOrder.BIG_ENDIAN)
convert_little_endian = partial(convert, byte_order=ByteOrder.LITTLE_ENDIAN)