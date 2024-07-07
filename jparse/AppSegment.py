from typing import IO, Tuple

from jparse import reader
from jparse.log import logger
from jparse.JpegMarker import JpegMarker
from jparse.JpegSegment import JpegSegment
from jparse.TiffHeader import TiffHeader
from jparse.ImageFileDirectory import ImageFileDirectory

# TODO: special class for JFIF [APP0] segment
# TODO: special class for Exif [APP1] segment

class AppSegment(JpegSegment):

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    @property
    def name(self) -> str:
        if not self.is_loaded:
            # TODO: load only name
            self.load()
        return self._name

    @property
    def tiff_header(self) -> TiffHeader:
        if not self.is_loaded:
            self.load()
        return self._tiff_header

    @property
    def ifd(self) -> Tuple[ImageFileDirectory, ...]:
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
        self._stream.seek(self.offset)

        logger.debug(f'[{self.marker.name}] segment loading...')
        self._stream.seek(self.offset + JpegMarker.MARKER_SIZE + JpegMarker.LENGTH_SIZE)

        self._name = parse_app_name(self._stream)
        logger.debug(f'-> name: {self._name}')

        if self._name.upper() == 'JFIF':
            self._is_loaded = True
            return

        # Exif or custom APP[2-15]
        byte = reader.read_bytes_strict(self._stream, 1)  # skip one more 0x00 byte ('Exif\0x00\0x00')
        if byte[0] != 0x00:
            raise RuntimeError('unexpected format of APP segment')

        # parse tiff header

        self._tiff_header = TiffHeader.parse(self._stream)
        logger.debug(f'-> {self._tiff_header}')

        # parse IFD

        next_ifd_offset = self._tiff_header.offset + self._tiff_header.ifd0_offset
        next_offset_filed_used = False
        ifd = []
        while True:
            self._stream.seek(next_ifd_offset)
            logger.debug(f'-> IDF #{len(ifd)}, offset=0x{next_ifd_offset:08X}')

            ifd_i = ImageFileDirectory.parse(self._stream, tiff_header=self._tiff_header)
            ifd.append(ifd_i)

            if next_offset_filed_used and ifd_i.next_ifd_offset == 0:
                break # the last ifd is reached

            if ifd_i.next_ifd_offset > 0:
                next_ifd_offset = self._tiff_header.offset + ifd_i.next_ifd_offset
                next_offset_filed_used = True
            else:
                assert ifd_i.offset + ifd_i.size <= self.offset + self.size, 'smth wrong with sizes'

                # some camera manufactures put IFDs one by one without next_ifd_offset
                if ifd_i.offset + ifd_i.size == self.offset + self.size:
                    break # the end of the segment is reached

                next_ifd_offset = ifd_i.offset + ifd_i.size

        self._ifd = tuple(ifd)



def parse_app_name(stream: IO) -> str:
    name = ''

    while True:
        byte = reader.read_bytes_strict(stream, 1)

        if byte[0] == 0x00:
            break

        name = name + byte.decode('ascii')

    return name