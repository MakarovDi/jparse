from __future__ import annotations

from io import SEEK_CUR
from typing import IO, Union
from collections.abc import Iterator

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
    def field_count(self) -> int:
        return self.__field_count

    @property
    def next_ifd_offset(self) -> int:
        """
        Next IFD offset relative to TiffHeader of the segment.
        """
        return self.__next_ifd_offset

    @property
    def index(self) -> int:
        """
        Index of the IFD
        """
        return self.__index

    def __len__(self) -> int:
        return self.field_count

    def __getitem__(self, tag: int) -> IfdField:
        assert type(tag) == int
        field = self.get_field(tag=tag)
        if field is None:
            raise KeyError(tag)
        return field

    def __iter__(self) -> IfdIterator:
        return IfdIterator(ifd=self)


    def __init__(self, stream: IO,
                       tiff_header: TiffHeader,
                       index : int,
                       next_ifd_offset: int,
                       filed_count: int,
                       offset: int):
        self._stream = stream
        self._tiff_header = tiff_header

        self.__next_ifd_offset = next_ifd_offset
        self.__offset = offset
        self.__index = index
        self.__field_count = filed_count

        # lazy field loading and caching
        self.__fields: dict[int, IfdField] = {}
        self.__fields_array = []
        self.__next_filed_offset = self.__offset + 2 # sizeof(field_count) = 2

        # the size will be updated with each loaded field
        # to get full IFD size all fields must be loaded
        self.__size = 2 + 4  # sizeof(field_count) + sizeof(next_ifd_offset)


    def __repr__(self) -> str:
        return (f'{self.__class__.__name__}(index={self.index}, '
                f'fields={self.field_count}, '
                f'next_ifd_offset={self.next_ifd_offset}, '
                f'offset={self.offset})')

    def size(self) -> int:
        """
        Estimate IFD size. All fields will be loaded to do so.
        """
        # load all fields to estimate the full size of IFD
        while len(self.__fields) != self.__field_count:
            self._load_next_filed()

        return self.__size


    def get_field(self, tag: Union[int, None]=None, index: Union[int, None]=None) -> Union[IfdField, None]:
        if tag is not None:
            assert index is None, 'only tag or index can be used at the same time'
            return self._get_field_by_tag(tag=tag)
        else:
            assert tag is None, 'only tag or index can be used at the same time'
            return self._get_field_by_index(index=index)


    @classmethod
    def parse(cls, stream: IO, tiff_header: TiffHeader, index: int) -> 'IFD':
        ifd_offset = stream.tell()

        field_count = parser.read_bytes_strict(stream, count=2)
        field_count = endianess.convert(field_count, byte_order=tiff_header.byte_order)

        # skip field headers, it will be loaded on request (lazy loading)
        stream.seek(field_count*12, SEEK_CUR)

        next_ifd_offset = parser.read_bytes_strict(stream, 4)
        next_ifd_offset = endianess.convert(next_ifd_offset, byte_order=tiff_header.byte_order)

        return IFD(stream=stream,
                   tiff_header=tiff_header,
                   offset=ifd_offset,
                   index=index,
                   filed_count=field_count,
                   next_ifd_offset=next_ifd_offset)


    def _get_field_by_tag(self, tag: int) -> Union[IfdField, None]:
        # check in cache
        ifd_filed = self.__fields.get(tag, None)
        if ifd_filed is not None:
            return ifd_filed

        # try to load more fields
        while True:
            ifd_filed = self._load_next_filed()
            if ifd_filed is None:
                # no more fields to load
                return None

            if ifd_filed.tag_id == tag:
                return ifd_filed

    def _get_field_by_index(self, index: int) -> Union[IfdField, None]:
        if len(self.__fields_array) > index:
            # field = iterate_to_index(self.__fields.values(), index=index)
            return self.__fields_array[index]

        index -= len(self.__fields) - 1
        field = None
        while index > 0:
            field = self._load_next_filed()
            if field is None:
                return None
            index -= 1

        return field


    def _load_next_filed(self) -> Union[IfdField, None]:
        if len(self.__fields) == self.__field_count:
            # all fields already loaded
            return None

        self._stream.seek(self.__next_filed_offset)

        ifd_field = IfdField.parse(self._stream, tiff_header=self._tiff_header)
        ifd_field.log()

        self.__size += ifd_field.size
        self.__fields[ifd_field.tag_id] = ifd_field
        self.__fields_array.append(ifd_field)
        self.__next_filed_offset += 12 # sizeof(ifd_filed_header)

        return ifd_field


class IfdIterator(Iterator):

    def __init__(self, ifd: IFD):
        self._ifd = ifd
        self._index = 0

    def __next__(self) -> IfdField:
        if self._index == self._ifd.field_count:
            raise StopIteration()

        field = self._ifd.get_field(index=self._index)
        self._index += 1

        return field