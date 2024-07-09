from typing import IO, OrderedDict

from jparse import parser
from jparse import endianess
from jparse.TiffHeader import TiffHeader
from jparse.IfdField import IfdField


class IFD:
    """
    IFD - Image File Directory.
    """

    @property
    def offset(self) -> int:
        """
        IFD offset from the start of the file.
        """
        return self.__offset

    @property
    def size(self) -> int:
        return self.__size

    @property
    def fields(self) -> OrderedDict[int, IfdField]:
        return self._fields

    @property
    def field_count(self) -> int:
        return len(self.fields)

    @property
    def next_ifd_offset(self) -> int:
        """
        Next IFD offset relative to TiffHeader of the segment.
        """
        return self.__next_ifd_offset

    @property
    def index(self) -> int:
        return self.__index


    def __init__(self, fields: OrderedDict[int, IfdField],
                       index : int,
                       next_ifd_offset: int,
                       size  : int,
                       offset: int=0):
        self._fields = fields
        self.__next_ifd_offset = next_ifd_offset
        self.__offset = offset
        self.__size = size
        self.__index = index


    def __repr__(self) -> str:
        return (f'{self.__class__.__name__}(index={self.index}, '
                f'fields={self.field_count}, '
                f'next_ifd_offset={self.next_ifd_offset}, '
                f'size={self.size}, '
                f'offset={self.offset})')

    @classmethod
    def parse(cls, stream: IO, tiff_header: TiffHeader, index: int) -> 'IFD':
        ifd_offset = stream.tell()

        field_count = parser.read_bytes_strict(stream, count=2)
        field_count = endianess.convert(field_count, byte_order=tiff_header.byte_order)

        fields = OrderedDict[int, IfdField]()
        size = 2 + 4 # sizeof(field_count) + sizeof(next_ifd_offset)
        for i in range(field_count):
            ifd_field = IfdField.parse(stream, tiff_header=tiff_header)
            ifd_field.log()

            fields[ifd_field.tag_id] = ifd_field
            size += ifd_field.size

        next_ifd_offset = parser.read_bytes_strict(stream, 4)
        next_ifd_offset = endianess.convert(next_ifd_offset, byte_order=tiff_header.byte_order)

        return IFD(offset=ifd_offset,
                   index=index,
                   fields=fields,
                   next_ifd_offset=next_ifd_offset,
                   size=size)