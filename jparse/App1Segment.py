from __future__ import annotations

from typing import IO, Union

from jparse.log import logger
from jparse.JpegMarker import JpegMarker
from jparse.ExifSegment import ExifSegment
from jparse.ImageFileDirectory import ImageFileDirectory


class App1Segment(ExifSegment):
    """
    Standard APP1/Exif segment. Contains linked IFD0 and IFD1.
    Other stuff (GPS IFD, ExifPrivate IFD, thumbnail image) should be loaded separately.
    """

    @property
    def ifd0(self) -> Union[ImageFileDirectory, None]:
        return self.ifd(0)

    @property
    def ifd1(self) -> Union[ImageFileDirectory, None]:
        return self.ifd(1)


    def __init__(self, marker: JpegMarker, stream: IO, offset: int, size: int):
        super().__init__(marker=marker, stream=stream, offset=offset, size=size)
        self.__ifd0 = None
        self.__ifd1 = None


    def ifd(self, index: int) -> Union[ImageFileDirectory, None]:
        """
        Load the segment's IFD by index (lazy, only IFD's header not content).
        If None is returned, the IFD with the specified index is not present in the segment.
        """
        if index > 1:
            # APP1 contains only 2 IFDs
            return None

        if index == 0:
            return self._load_ifd0()
        elif index == 1:
            return self._load_ifd1()
        else:
            raise RuntimeError(index)


    def _load_ifd0(self) -> Union[ImageFileDirectory, None]:
        if self.__ifd0 is not None:
            return self.__ifd0

        if self.tiff_header is None:
            logger.debug(f'-> TiffHeader is missing for APP1 -> stop parsing')
            return None

        ifd0_offset = self.tiff_header.offset + self.tiff_header.ifd0_offset
        logger.debug(f'-> IDF #0, offset=0x{ifd0_offset:08X}')

        self._stream.seek(ifd0_offset)
        self.__ifd0 = ImageFileDirectory.parse(self._stream, tiff_header=self.tiff_header)
        return self.__ifd0


    def _load_ifd1(self) -> Union[ImageFileDirectory, None]:
        if self.__ifd1 is not None:
            return self.__ifd1

        ifd0 = self.ifd0
        if ifd0 is None:
            logger.debug(f'-> IFD0 is missing for APP1 -> stop parsing')
            return None

        ifd1_offset = self.tiff_header.offset + ifd0.next_ifd_offset
        logger.debug(f'-> IDF #1, offset=0x{ifd1_offset:08X}')

        self._stream.seek(ifd1_offset)
        self.__ifd1 = ImageFileDirectory.parse(self._stream, tiff_header=self.tiff_header)
        return self.__ifd1