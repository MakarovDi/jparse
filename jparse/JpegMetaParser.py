from io import SEEK_CUR
from typing import IO, List, Union, OrderedDict

from jparse import parser
from jparse import endianess
from jparse.log import logger
from jparse.JpegMarker import JpegMarker, SOI, EOI, SOS, APPn
from jparse.JpegSegment import JpegSegment
from jparse.AppSegment import AppSegment
from jparse.ExifSegment import ExifSegment
from jparse.IfdField import ValueType
from jparse.IFD import IFD
from jparse.TagPath import TagPath

from jparse.ExifInfo import ExifInfo



class JpegMetaParser:

    @property
    def exif_info(self) -> ExifInfo:
        return self._exif_info

    @property
    def app_segments(self) -> tuple[str, ...]:
        """
        Names of APP* segments
        """
        return self.segments

    @property
    def segments(self) -> tuple[str, ...]:
        return tuple(self._segments.keys())

    @property
    def image_data_offset(self) -> int:
        return self._sos.offset + self._sos.size

    @property
    def image_data_size(self) -> int:
        if self._eoi is None:
            raise RuntimeError('use JpegMetaParser(estimate_image_size=True, ...)')
        return self._eoi.offset - self._sos.offset - self._sos.size

    @property
    def stream(self) -> IO:
        return self._stream

    def __len__(self) -> int:
        return len(self.segments)

    def __getitem__(self, item: str) ->  Union[ExifSegment, AppSegment]:
        assert type(item) == str, 'item must be a str: e.g parser["APP0"]'
        return self._segments[item.upper()]

    def __iter__(self):
        return iter(self._segments.values())

    def get_segment(self, marker_name: str) -> Union[ExifSegment, AppSegment, None]:
        return self._segments.get(marker_name.upper(), None)


    def __init__(self, stream: IO, estimate_image_size: bool=False):
        if 'r' not in stream.mode or 'b' not in stream.mode:
            raise RuntimeError('IO mode should be "rb"')

        self._stream = stream

        structure = scan_jpeg_structure(stream, include_eoi=estimate_image_size)
        self._structure = structure

        self._sos = None

        # EOI will be available only if the whole file is parsed
        self._eoi = structure[-1] if structure[-1].marker == EOI else None

        self._segments = OrderedDict[str, Union[ExifSegment, AppSegment]]()
        for segment in structure:
            if segment.marker == SOS:
                self._sos = segment
            elif APPn.check_mask(segment.marker.signature):
                assert isinstance(segment, AppSegment)
                self._segments[segment.marker.name.upper()] = segment

        self._exif_info = ExifInfo(parser=self)


    def get_tag_value(self, tag_path: TagPath, default=None) -> Union[ValueType, None]:
        segment = self._segments.get(tag_path.app_name.upper())
        if segment is None:
            logger.debug(f'[get_tag_value] segment "{tag_path.app_name.upper()}" is not found')
            return default

        ifd: IFD = segment.ifd(tag_path.ifd_number)
        if ifd is None:
            logger.debug(f'[get_tag_value] IFD{tag_path.ifd_number} is not found in {tag_path.app_name.upper()}')
            return default

        field = ifd.get_field(tag_path.tag_id)
        if field is None:
            logger.debug(f'[get_tag_value] tag 0x{tag_path.tag_id:04X} is not found in IFD #{tag_path.ifd_number}')
            return default

        return field.value


def scan_jpeg_structure(stream: IO, include_eoi: bool) -> List[JpegSegment]:
    offset = stream.tell()

    parser.read_jpeg_signature(stream)
    segment = JpegSegment.create(marker=SOI, stream=stream, offset=offset, size=JpegMarker.MARKER_SIZE)
    segment.log()
    structure = [ segment ]

    offset += JpegMarker.MARKER_SIZE

    # scan segments

    segment_marker = stream.read(JpegMarker.MARKER_SIZE)
    while len(segment_marker) == JpegMarker.MARKER_SIZE:
        segment_marker = endianess.convert_big_endian(segment_marker)
        segment_marker = JpegMarker.detect(segment_marker)

        if segment_marker == EOI:
            raise RuntimeError('unexpected EOI marker before SOS marker')

        segment_size = parser.read_bytes_strict(stream, JpegMarker.LENGTH_SIZE)
        segment_size = endianess.convert_big_endian(segment_size) + JpegMarker.MARKER_SIZE

        segment = JpegSegment.create(marker=segment_marker, stream=stream, offset=offset, size=segment_size)
        segment.log()
        structure.append(segment)

        offset += segment_size
        stream.seek(segment_size - JpegMarker.MARKER_SIZE - JpegMarker.LENGTH_SIZE, SEEK_CUR)

        if segment_marker == SOS:
            break

        segment_marker = stream.read(JpegMarker.MARKER_SIZE)

    if include_eoi:
        eoi_offset = parser.scan_for_eoi(stream)
        if eoi_offset == 0:
            raise RuntimeError('EOI is not found')

        segment = JpegSegment.create(marker=EOI, stream=stream, offset=offset + eoi_offset, size=JpegMarker.MARKER_SIZE)
        segment.log()
        structure.append(segment)

    return structure