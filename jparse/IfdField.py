import io
import struct
from numbers import Number
from typing import Tuple, IO, Union

from jparse import reader
from jparse.log import logger, logging
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
        if logger.isEnabledFor(logging.DEBUG):
            # IFD contain a lot of fields sometimes, so IfdFiled.parse() and IfdFiled.log() are hot.
            # The check for logging.DEBUG level will prevent formatting and repr overhead.
            indent = '\t'*tabs
            logger.debug(f'{indent}Field[0x{self.tag_id:04X}]: {repr(self.field_type):>24s}, '
                         f'count={self.count:<3d}, '
                         f'size={self.size:<3d}, '
                         f'field_offset=0x{self.offset:08X}, '
                         f'value_offset=0x{self.value_offset:08X}')

    def load(self):
        if self.is_loaded:
            return

        self._stream.seek(self.value_offset)
        data = reader.read_bytes_strict(self._stream, self.count*self.field_type.byte_count)

        self._value = parse_value(data=data, count=self.count, field_type=self.field_type, byte_order=self._byte_order)
        self._is_loaded = True


    @classmethod
    def parse(cls, stream: IO, tiff_header: TiffHeader) -> 'IfdField':
        field_offset = stream.tell()

        tag_id = reader.read_bytes_strict(stream, 2)
        tag_id = endianess.convert(tag_id, byte_order=tiff_header.byte_order)

        type_id = reader.read_bytes_strict(stream, 2)
        type_id = endianess.convert(type_id, byte_order=tiff_header.byte_order)

        if FieldType.is_unknown(type_id):
            type_id = FieldType.Unknown
        else:
            type_id = FieldType(type_id)

        count = reader.read_bytes_strict(stream, 4)
        count = endianess.convert(count, byte_order=tiff_header.byte_order)

        field_size = count * type_id.byte_count
        if field_size <= 4:
            value_offset = field_offset + 8
            stream.seek(4, io.SEEK_CUR) # skip value data
            field_size = IfdField.FIXED_SIZE # no extra data outsize the field structure
        else:
            value_offset = reader.read_bytes_strict(stream, 4)
            value_offset = endianess.convert(value_offset, byte_order=tiff_header.byte_order)
            value_offset += tiff_header.offset
            field_size = reader.align4(field_size) + IfdField.FIXED_SIZE

        return IfdField(tag_id=tag_id,
                        count=count,
                        field_type=type_id,
                        stream=stream,
                        byte_order=tiff_header.byte_order,
                        value_offset=value_offset,
                        size=field_size,
                        offset=field_offset)


def parse_value(data : bytes,
                count: int,
                field_type: FieldType,
                byte_order: ByteOrder) -> ValueType:
    if field_type == FieldType.Unknown:
        raise NotImplementedError('can not parse unknown value type')

    offset = 0
    value = []
    for i in range(count):
        value_data = data[ offset + field_type.byte_count*i : offset + field_type.byte_count*(i+1) ]
        value_data = unpack_value(value_data, field_type=field_type, byte_order=byte_order)
        value.append(value_data)

    if field_type == field_type.ASCII:
        return ''.join(value)

    if len(value) == 1:
        return value[0]

    return tuple(value)


def unpack_value(data: bytes,
                 field_type: FieldType,
                 byte_order: ByteOrder) -> Union[Number, chr]:
    assert len(data) == field_type.byte_count, 'invalid dat size'

    if field_type.is_rational:
        from fractions import Fraction
        numerator = struct.unpack(f'{byte_order.format_chr}{field_type.type_chr}', data[:4])
        denominator = struct.unpack(f'{byte_order.format_chr}{field_type.type_chr}', data[4:])
        return Fraction(numerator=numerator[0], denominator=denominator[0])

    value = struct.unpack(f'{byte_order.format_chr}{field_type.type_chr}', data)
    value = value[0]

    if field_type == FieldType.ASCII:
        value = value.decode('ascii') if value[0] != 0 else ''

    return value