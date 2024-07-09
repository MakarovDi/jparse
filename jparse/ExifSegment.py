from __future__ import annotations

from typing import IO, Union

from jparse import parser
from jparse.log import logger
from jparse.JpegMarker import JpegMarker
from jparse.AppSegment import AppSegment
from jparse.TiffHeader import TiffHeader
from jparse.IFD import IFD


class ExifSegment(AppSegment):
    """
    Interface for Exif-like segments: set of IFDs.
    """

    @property
    def tiff_header(self) -> Union[TiffHeader, None]:
        self.load()
        return self.__tiff_header


    def __getitem__(self, item: int) -> Union[IFD, None]:
        assert type(item) == int, 'index must be int'
        return self.ifd(index=item)

    def __iter__(self) -> ExifIterator:
        return ExifIterator(self)


    def ifd(self, index: int) -> Union[IFD, None]:
        """
        Load the segment's IFD by index (lazy, only IFD's header not content).
        If None is returned, the IFD with the specified index is not present in the segment.
        """
        raise NotImplementedError()


    def __init__(self, marker: JpegMarker, stream: IO, offset: int, size: int):
        super().__init__(marker=marker, stream=stream, offset=offset, size=size)
        self.__tiff_header = None


    def load(self):
        """
        Load segment header without loading the segment content.
        It will be called automatically when the segment property is accessed.
        """
        if self.is_loaded: return

        self._stream.seek(self.offset + JpegMarker.MARKER_SIZE + JpegMarker.LENGTH_SIZE)
        logger.debug(f'[{self.marker.name}] segment loading...')

        self._name = parser.parse_app_name(self._stream)
        logger.debug(f'-> name: {self._name}')

        # skip one more 0x00 byte of exif signature ('Exif\0x00\0x00')
        byte = parser.read_bytes_strict(self._stream, 1)
        if byte[0] != 0x00:
            logger.debug(f'-> 0x00 padding is missing after exif-id -> stop parsing')
            self._is_loaded = True
            return

        self.__tiff_header = TiffHeader.parse(self._stream)
        logger.debug(f'-> {self.__tiff_header}')

        self._is_loaded = True


class ExifIterator:
    """
    Iterator for ExifSegment to enable for-support:

        for idf in segment:
            print(idf)

    """

    def __init__(self, segment: ExifSegment):
        self._segment = segment
        self._idx = 0

    def __next__(self) -> IFD:
        idf = self._segment.ifd(self._idx)

        if idf is None:
            # reached last IDF inside the segment
            raise StopIteration()

        self._idx += 1

        return idf