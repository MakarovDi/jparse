from typing import IO, Union

from jparse.log import logger
from jparse.JpegMarker import JpegMarker
from jparse.ExifSegment import ExifSegment
from jparse.IFD import IFD


class GenericExifSegment(ExifSegment):
    """
    Lazy generic parser for unknown APPx/Exif segment.
    It tries to load sequential IFDs or a linked list of IFDs.
    Might fail to read IFD if segment contains data except IFDs (e.g. APP1 contains image).
    """

    def __init__(self, marker: JpegMarker, stream: IO, offset: int, size: int):
        super().__init__(marker=marker, stream=stream, offset=offset, size=size)

        # cache for lazy IFD loading
        self.__ifd = []
        self.__next_ifd_offset = None
        self.__end_of_segment = False


    def ifd(self, index: int) -> Union[IFD, None]:
        """
        Load the segment's IFD by index (lazy, only IFD's header not content).
        All IFD with in range [0, index-1] will be also loaded and cached.
        It's not possible to load only one IFD because the offset is unknown.
        If the IFD was loaded during a previous ifd() call, the cached object will be returned.
        If None is returned, the IFD with the specified index is not present in the segment.
        """
        if len(self.__ifd) > index:
            # return IFD from the cache
            return self.__ifd[index]

        # load IFD one by one till index reached or EOF
        index -= len(self.__ifd) - 1
        ifd_next = None
        while index > 0:
            ifd_next = self._load_next_ifd()
            if ifd_next is None:
                return None # end of the segment
            index -= 1

        return ifd_next


    def _load_next_ifd(self) -> Union[IFD, None]:
        """
        Load next IFD from self._next_ifd_offset and update self._next_ifd_offset
        """
        if self.__end_of_segment:
            return None

        if self.tiff_header is None:
            return None

        if self.__next_ifd_offset is None:
            # set offset for the first IFD (can't be empty)
            self.__next_ifd_offset = self.tiff_header.offset + self.tiff_header.ifd0_offset

        ifd_index = len(self.__ifd)

        self._stream.seek(self.__next_ifd_offset)
        logger.debug(f'-> IFD #{ifd_index}, offset=0x{self.__next_ifd_offset:08X}')

        # parse IFD header (without filed value loading)
        ifd_i = IFD.parse(self._stream, tiff_header=self.tiff_header, index=ifd_index)

        # update offset for the next IFD
        if ifd_i.next_ifd_offset > 0:
            # Good case - IFDs organized as a linked list:
            # Link to the next IFD provided in ifd_i.next_ifd_offset
            self.__next_ifd_offset = self.tiff_header.offset + ifd_i.next_ifd_offset
        else:
            # Bad case - sequential IFDs with next_ifd_offset=0:
            # Some cameras put IFDs one by one, sequentially.
            # In this case, an IFD object can't be lazy and must load all fields
            # to estimate IFD size to estimate offset for the next IFD.
            if ifd_i.offset + ifd_i.size() >= self.offset + self.size:
                # the end of the segment is reached
                # note: this check is not 100% reliable because segment can contain
                #       some binary data except IFD (e.g. APP1 has thumbnail image)
                self.__end_of_segment = True

                if ifd_i.offset + ifd_i.size() > self.offset + self.size:
                    raise RuntimeError('smth wrong: IFD size is out of a segment size')
            else:
                self.__next_ifd_offset = ifd_i.offset + ifd_i.size()

        # save to cache
        self.__ifd.append(ifd_i)
        return ifd_i