from typing import IO, OrderedDict

from jparse import reader
from jparse import endianess
from jparse.TiffHeader import TiffHeader
from jparse.IfdField import IfdField


class ImageFileDirectory:

    @property
    def offset(self) -> int:
        return self._offset

    @property
    def size(self) -> int:
        return self._size

    @property
    def fields(self) -> OrderedDict[int, IfdField]:
        return self._fields

    @property
    def field_count(self) -> int:
        return len(self._fields)

    @property
    def next_ifd_offset(self) -> int:
        return self._next_ifd_offset


    def __init__(self, fields: OrderedDict[int, IfdField],
                       next_ifd_offset: int,
                       size  : int,
                       offset: int=0):
        self._fields = fields
        self._next_ifd_offset = next_ifd_offset
        self._offset = offset
        self._size = size


    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(fields={repr(self.fields)}, ' \
                                         f'next_ifd_offset={self.next_ifd_offset}, ' \
                                         f'size={self.size}, ' \
                                         f'offset={self.offset})'

    @classmethod
    def parse(cls, stream: IO, tiff_header: TiffHeader) -> 'ImageFileDirectory':
        ifd_offset = stream.tell()

        field_count = reader.read_bytes_strict(stream, count=2)
        field_count = endianess.convert(field_count, byte_order=tiff_header.byte_order)

        fields = OrderedDict[int, IfdField]()
        size = 2 + 4 # sizeof(field_count) + sizeof(next_ifd_offset)
        for i in range(field_count):
            ifd_field = IfdField.parse(stream, tiff_header=tiff_header)
            ifd_field.log()

            fields[ifd_field.tag_id] = ifd_field
            size += ifd_field.size

        next_ifd_offset = reader.read_bytes_strict(stream, 4)
        next_ifd_offset = endianess.convert(next_ifd_offset, byte_order=tiff_header.byte_order)

        return ImageFileDirectory(offset=ifd_offset,
                                  fields=fields,
                                  next_ifd_offset=next_ifd_offset,
                                  size=size)