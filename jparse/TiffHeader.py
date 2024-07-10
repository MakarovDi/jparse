from typing import IO

from jparse import parser
from jparse import endianess
from jparse.endianess import ByteOrder


class TiffHeader:
    ID  : int = 0x002A
    SIZE: int = 8

    @property
    def byte_order(self) -> ByteOrder:
        return self._byte_order

    @property
    def ifd0_offset(self) -> int:
        return self._ifd0_offset

    @property
    def offset(self) -> int:
        return self._offset


    def __init__(self, byte_order: ByteOrder, ifd0_offset: int, offset: int=0):
        self._byte_order = byte_order
        self._ifd0_offset = ifd0_offset
        self._offset = offset


    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(byte_order={self.byte_order.name}, ifd0_offset={self.ifd0_offset})'


    @classmethod
    def parse(cls, stream: IO) -> 'TiffHeader':
        tiff_header_offset = stream.tell()

        # read byte order

        byte_order = parser.read_bytes_strict(stream, 2)

        if byte_order[0] == byte_order[1] == 0x49:
            byte_order = ByteOrder.LITTLE_ENDIAN
        elif byte_order[0] == byte_order[1] == 0x4D:
            byte_order = ByteOrder.BIG_ENDIAN
        else:
            raise RuntimeError('invalid tiff header format')

        # check tiff header signature

        tiff_id = parser.read_bytes_strict(stream, 2)
        tiff_id = endianess.convert(tiff_id, byte_order=byte_order)
        if tiff_id != TiffHeader.ID:
            raise RuntimeError('invalid tiff header format')

        # read IFD0 offset

        ifd0_offset = parser.read_bytes_strict(stream, 4)
        ifd0_offset = endianess.convert(ifd0_offset, byte_order=byte_order)

        return TiffHeader(offset=tiff_header_offset,
                          byte_order=byte_order,
                          ifd0_offset=ifd0_offset)