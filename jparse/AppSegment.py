from typing import IO

from jparse import parser
from jparse.log import logger
from jparse.JpegMarker import JpegMarker
from jparse.JpegSegment import JpegSegment


class AppSegment(JpegSegment):
    """
    Basic container for the APPx segments.
    """

    @property
    def is_loaded(self) -> bool:
        """
        Check if the segment's header already loaded (not the segment's content).
        """
        return self._is_loaded

    @property
    def name(self) -> str:
        self.load()
        return self._name


    def __init__(self, marker: JpegMarker, stream: IO, offset: int, size: int):
        super().__init__(marker=marker, stream=stream, offset=offset, size=size)

        self._name = None
        self._is_loaded = False


    def __str__(self) -> str:
        return f'{self.marker.name} - {self.name} - offset: 0x{self.offset:08X}, {self.size} bytes'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(marker={repr(self.marker)}, name={repr(self.name)}, offset={self.offset}, size={self.size})'


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

        self._is_loaded = True