import io
import struct
from numbers import Number
from typing import Tuple, IO, Union

from jparse import tools
from jparse import endianess
from jparse.endianess import ByteOrder
from jparse.TiffHeader import TiffHeader
from jparse.FieldType import FieldType


ValueType = Union[Number, str, Tuple[Number, ...]]


class IfdField:
    FIXED_SIZE = 12

    @property
    def offset(self) -> int:
        return self._offset

    @property
    def size(self) -> int:
        return self._size

    @property
    def tag_id(self) -> int:
        return self._tag_id

    @property
    def field_type(self) -> FieldType:
        return self._field_type

    @property
    def count(self) -> int:
        return self._count

    @property
    def value(self) -> ValueType:
        if not self.is_loaded:
            self.load()
        return self._value

    @property
    def value_offset(self) -> int:
        return self._value_offset

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded


    def __init__(self, tag_id    : int,
                       count     : int,
                       field_type: FieldType,
                       stream    : IO,
                       byte_order: ByteOrder,
                       value_offset: int,
                       size      : int,
                       offset    : int):
        self._is_loaded = False
        self._tag_id = tag_id
        self._field_type = field_type
        self._count = count
        self._value_offset = value_offset
        self._stream = stream
        self._byte_order = byte_order
        self._value = None
        self._size = size
        self._offset = offset


    def log(self, tabs: int=2):
        tools.logger.debug('\t'*tabs + f'Field[0x{self.tag_id:04X}]: {repr(self.field_type):>24s}, '
                                       f'count={self.count:<3d}, '
                                       f'size={self.size}, '
                                       f'field_offset=0x{self.offset:08X}, '
                                       f'value_offset=0x{self.value_offset:08X}')

    def load(self):
        if self.is_loaded:
            return

        self._stream.seek(self.value_offset)
        data = tools.read_bytes_strict(self._stream, self.count*self.field_type.byte_count)

        # TODO: self._value = parse_value
        self._is_loaded = True


    @classmethod
    def parse(cls, stream: IO, tiff_header: TiffHeader) -> 'IfdField':
        field_offset = stream.tell()

        tag_id = tools.read_bytes_strict(stream, 2)
        tag_id = endianess.convert(tag_id, byte_order=tiff_header.byte_order)

        type_id = tools.read_bytes_strict(stream, 2)
        type_id = endianess.convert(type_id, byte_order=tiff_header.byte_order)

        if FieldType.is_unknown(type_id):
            type_id = FieldType.Unknown
        else:
            type_id = FieldType(type_id)

        count = tools.read_bytes_strict(stream, 4)
        count = endianess.convert(count, byte_order=tiff_header.byte_order)

        field_size = count * type_id.byte_count
        if field_size <= 4:
            value_offset = field_offset + 8
            stream.seek(4, io.SEEK_CUR) # skip value data # TODO: load immediately ?
            field_size = IfdField.FIXED_SIZE # no extra data outsize the field structure
        else:
            value_offset = tools.read_bytes_strict(stream, 4)
            value_offset = endianess.convert(value_offset, byte_order=tiff_header.byte_order)
            value_offset += tiff_header.offset
            field_size = tools.align4(field_size) + IfdField.FIXED_SIZE

        return IfdField(tag_id=tag_id,
                        count=count,
                        field_type=type_id,
                        stream=stream,
                        byte_order=tiff_header.byte_order,
                        value_offset=value_offset,
                        size=field_size,
                        offset=field_offset)