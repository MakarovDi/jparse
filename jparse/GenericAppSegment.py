from typing import IO, Union

from jparse import parser
from jparse.log import logger
from jparse.JpegMarker import JpegMarker
from jparse.JpegSegment import JpegSegment
from jparse.TiffHeader import TiffHeader
from jparse.ImageFileDirectory import ImageFileDirectory

# TODO: special class for Exif [APP1] segment

class GenericAppSegment(JpegSegment):
    """
    Lazy generic parser for unknown APPx/Exif segment.
    It tries to load IFDs organized as a linked list or sequential IFDs.
    Might fail to read IFD if segment contains data except IFDs (e.g. APP1 contains image).
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

    @property
    def tiff_header(self) -> TiffHeader:
        self.load()
        return self._tiff_header

    def __getitem__(self, item: int) -> Union[ImageFileDirectory, None]:
        assert type(item) == int, 'index must be int'
        return self.ifd(index=item)

    def __iter__(self):
        return AppSegmentIterator(self)


    def __init__(self, marker: JpegMarker, stream: IO, offset: int, size: int):
        super().__init__(marker=marker, stream=stream, offset=offset, size=size)

        self._tiff_header = None
        self._name = None
        self._is_loaded = False

        # cache for lazy IFD loading
        self._ifd = []
        self._next_ifd_offset = None


    def ifd(self, index: int) -> Union[ImageFileDirectory, None]:
        """
        Load the segment's IFD by index (lazy, only IFD's header not content).
        All IFD with in range [0, index-1] will be also loaded and cached.
        It's not possible to load only one IFD because the offset is unknown.
        If the IFD was loaded during a previous ifd() call, the cached object will be returned.
        If None is returned, the IFD with the specified index is not present in the segment.
        """
        self.load()

        if len(self._ifd) > index:
            # return IFD from the cache
            return self._ifd[index]

        # load IFD one by one till index reached or EOF
        index -= len(self._ifd) - 1
        ifd_next = None
        while index > 0:
            ifd_next = self._load_next_ifd()
            if ifd_next is None:
                return None # EOF

            self._ifd.append(ifd_next) # save to cache
            index -= 1

        return ifd_next


    def __str__(self) -> str:
        return f'{self.marker.name} - {self.name} - offset: 0x{self.offset:08X}, {self.size} bytes'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(marker={repr(self.marker)} - {self.name}, offset={self.offset}, size={self.size})'


    def load(self):
        """
        Load segment header without loading the segment content.
        It will be called automatically when the segment property is accessed.
        """
        if self.is_loaded: return

        self._stream.seek(self.offset)

        logger.debug(f'[{self.marker.name}] segment loading...')
        self._stream.seek(self.offset + JpegMarker.MARKER_SIZE + JpegMarker.LENGTH_SIZE)

        self._name = parser.parse_app_name(self._stream)
        logger.debug(f'-> name: {self._name}')

        if self._name.upper() == 'JFIF':
            # do nothing for JFIF - image data
            self._is_loaded = True
            return

        if self._name.upper() != 'EXIF':


        # Exif or custom APP[2-15]
        byte = parser.read_bytes_strict(self._stream, 1)  # skip one more 0x00 byte ('Exif\0x00\0x00')
        if byte[0] != 0x00:
            raise RuntimeError('unexpected format of APP segment')

        self._tiff_header = TiffHeader.parse(self._stream)
        logger.debug(f'-> {self._tiff_header}')

        # set offset for the first IFD (can't be empty)
        self._next_ifd_offset = self._tiff_header.offset + self._tiff_header.ifd0_offset
        self._is_loaded = True


    def _load_next_ifd(self) -> Union[ImageFileDirectory, None]:
        """
        Load next IFD from self._next_ifd_offset and update self._next_ifd_offset
        """
        assert self.is_loaded

        if self._next_ifd_offset is None:
            # end of the segment, no more IFDs
            return None

        self._stream.seek(self._next_ifd_offset)
        logger.debug(f'-> IDF #{len(self._ifd)}, offset=0x{self._next_ifd_offset:08X}')

        # parse IFD header (without filed value loading)
        ifd_i = ImageFileDirectory.parse(self._stream, tiff_header=self._tiff_header)

        # update offset for the next IFD
        if ifd_i.next_ifd_offset > 0:
            # Good case - IFDs organized as a linked list:
            # Link to the next IFD provided in ifd_i.next_ifd_offset
            self._next_ifd_offset = self._tiff_header.offset + ifd_i.next_ifd_offset
        else:
            # Bad case - sequential IFDs with next_ifd_offset=0:
            # Some cameras put IFDs one by one, sequentially.
            # In this case, an IFD object can't be lazy and must load all fields
            # to estimate IFD size to estimate offset for the next IFD.
            if ifd_i.offset + ifd_i.size >= self.offset + self.size:
                # the end of the segment is reached
                # TODO: note: this check is not 100% guarantee, e.g. APP1
                if ifd_i.offset + ifd_i.size > self.offset + self.size:
                    raise RuntimeError('smth wrong: IFD size is out of a segment size')
                self._next_ifd_offset = None
            else:
                self._next_ifd_offset = ifd_i.offset + ifd_i.size

        return ifd_i


class AppSegmentIterator:
    """
    Iterator the AppSegment to enable for-support:

        for idf in app_segment:
            print(idf)

    """

    def __init__(self, segment: GenericAppSegment):
        self._segment = segment
        self._idx = 0

    def __next__(self) -> ImageFileDirectory:
        idf = self._segment.ifd(self._idx)

        if idf is None:
            # reached last IDF inside the segment
            raise StopIteration()

        self._idx += 1

        return idf