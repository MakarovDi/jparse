from typing import IO, Tuple

from jparse import tools
from jparse.JpegMarker import JpegMarker
from jparse.JpegSegment import JpegSegment

# TODO: special class for JFIF [APP0] segment
# TODO: special class for Exif [APP1] segment

class AppSegment(JpegSegment):

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    @property
    def name(self) -> str:
        if not self.is_loaded:
            self.load() # TODO: load only name
        return self._name

    @property
    def tiff_header(self) -> 'TiffHeader':
        return self._tiff_header

    @property
    def ifd(self) -> Tuple:
        if not self.is_loaded:
            self.load()
        return self._ifd


    def __init__(self, marker: JpegMarker, stream: IO, offset: int, size: int):
        super().__init__(marker=marker, stream=stream, offset=offset, size=size)

        self._tiff_header = None
        self._name = None
        self._is_loaded = False
        self._ifd = None


    def load(self):
        if self.is_loaded: return

        tools.logger.debug(f'[{self.marker.name}] segment loading...')
        self._stream.seek(self.offset + JpegMarker.MARKER_SIZE + JpegMarker.LENGTH_SIZE)

        self._name = parse_app_name(self._stream)
        tools.logger.debug(f'-> name: {self.name}')

        if self.name.upper() == 'JFIF':
            self._is_loaded = True
            return

        # Exif or custom APP[2-15]
        byte = tools.read_bytes_strict(self._stream, 1)  # skip one more 0x00 byte ('Exif\0x00\0x00')
        if byte[0] != 0x00:
            raise RuntimeError('unexpected format of APP segment')

        # parse tiff header

        # self._tiff_header = TiffHeader.parse(self._stream)
        # tools.logger.debug(f'-> {self.tiff_header}')



def parse_app_name(stream: IO) -> str:
    name = ''

    while True:
        byte = tools.read_bytes_strict(stream, 1)

        if byte[0] != 0x00:
            break

        name = name + bytes.decode('ascii')

    return name