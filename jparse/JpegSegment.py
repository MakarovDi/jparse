from typing import IO
from jparse.JpegMarker import JpegMarker, APPn, APP0, APP1
from jparse.log import logger


class JpegSegment:

    @property
    def marker(self) -> JpegMarker:
        return self._marker

    @property
    def name(self) -> str:
        return self.marker.name

    @property
    def offset(self) -> int:
        """
        The segment offset from the file start.
        """
        return self._offset

    @property
    def size(self) -> int:
        return self._size

    @property
    def is_loaded(self) -> bool:
        """
        Check if the segment's header already loaded (not the segment's content).
        """
        return True


    @staticmethod
    def create(marker: JpegMarker, stream: IO, offset: int, size: int) -> 'JpegSegment':
        """
        Segment creation factory method.
        """
        if marker == APP0:
            # JFIF segment contains no meta, only image data
            from jparse.AppSegment import AppSegment
            Segment = AppSegment
        elif marker == APP1:
            # standard Exif segment - Exif Attribute Information
            from jparse.ExifSegment import ExifSegment
            Segment = ExifSegment
        elif APPn.check_mask(marker.signature):
            # custom APP segment, trying to parse it with generic exif parser
            from jparse.ExifSegment import ExifSegment # TODO: Generic
            Segment = ExifSegment
        else:
            Segment = JpegSegment

        return Segment(marker=marker,
                       stream=stream,
                       offset=offset,
                       size=size)


    def __init__(self, marker: JpegMarker, stream: IO, offset: int, size: int):
        self._marker = marker
        self._offset = offset
        self._size = size
        self._stream = stream


    def __str__(self) -> str:
        return f'{self.marker.name} - offset: 0x{self.offset:08X}, {self.size} bytes'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(marker={repr(self.marker)}, offset={self.offset}, size={self.size})'


    def log(self):
        logger.debug(f'0x{self.offset:08X} -> {self.marker.name:5s}: {self.size} bytes')


    def load(self):
        """
        Load segment header without content.
        It will be called automatically when the segment property is accessed.
        """
        pass