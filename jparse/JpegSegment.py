from typing import IO
from jparse.JpegMarker import JpegMarker, APPn
from jparse.log import logger


class JpegSegment:

    @property
    def marker(self) -> JpegMarker:
        return self._marker

    @property
    def offset(self) -> int:
        return self._offset

    @property
    def size(self) -> int:
        return self._size

    @property
    def is_loaded(self) -> bool:
        """
        Check if the segment's header already loaded (not the segment's content).
        """
        return False


    @staticmethod
    def create(marker: JpegMarker, stream: IO, offset: int, size: int) -> 'JpegSegment':
        """
        Segment creationg factory method.
        """
        if APPn.check_mask(marker.signature):
            from jparse.GenericAppSegment import GenericAppSegment
            SegmentType = GenericAppSegment
        else:
            SegmentType = JpegSegment

        return SegmentType(marker=marker,
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
        Load segment header without loading the segment content.
        It will be called automatically when the segment property is accessed.
        """
        raise NotImplementedError()