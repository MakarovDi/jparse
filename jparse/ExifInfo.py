from typing import Optional, Union, Iterable
from fractions import Fraction

from jparse.IFD import IFD
from jparse.IfdField import ValueType
from jparse.log import logger
from jparse.TagPath import TagPath


class ExifInfo:
    """
    Exif Standard Information.
    https://www.kodak.com/global/plugins/acrobat/en/service/digCam/exifStandard2.pdf
    """

    @property
    def image_width(self) -> Optional[int]:
        return self._parser.get_tag_value(TagPath(app_name='APP1', ifd_number=0,  tag_id=0x100))

    @property
    def image_height(self) -> Optional[int]:
        return self._parser.get_tag_value(TagPath(app_name='APP1', ifd_number=0,  tag_id=0x101))

    @property
    def bits_per_sample(self) -> Optional[int]:
        return self._parser.get_tag_value(TagPath(app_name='APP1', ifd_number=0, tag_id=0x102))

    @property
    def compression(self) -> Optional[int]:
        return self._parser.get_tag_value(TagPath(app_name='APP1', ifd_number=0, tag_id=0x103))

    @property
    def photometric_interpretation(self) -> Optional[int]:
        return self._parser.get_tag_value(TagPath(app_name='APP1', ifd_number=0, tag_id=0x106))

    @property
    def orientation(self) -> Optional[int]:
        return self._parser.get_tag_value(TagPath(app_name='APP1', ifd_number=0, tag_id=0x112))

    @property
    def samples_per_pixel(self) -> Optional[int]:
        return self._parser.get_tag_value(TagPath(app_name='APP1', ifd_number=0, tag_id=0x115))

    @property
    def planar_configuration(self) -> Optional[int]:
        return self._parser.get_tag_value(TagPath(app_name='APP1', ifd_number=0, tag_id=0x11C))

    @property
    def ycbcr_sub_sampling(self) -> Optional[int]:
        return self._parser.get_tag_value(TagPath(app_name='APP1', ifd_number=0, tag_id=0x212))

    @property
    def ycbcr_sub_positioning(self) -> Optional[int]:
        return self._parser.get_tag_value(TagPath(app_name='APP1', ifd_number=0, tag_id=0x213))

    @property
    def x_resolution(self) -> Optional[Fraction]:
        return self._parser.get_tag_value(TagPath(app_name='APP1', ifd_number=0, tag_id=0x11A))

    @property
    def y_resolution(self) -> Optional[Fraction]:
        return self._parser.get_tag_value(TagPath(app_name='APP1', ifd_number=0, tag_id=0x11B))

    @property
    def resolution_unit(self) -> Optional[int]:
        return self._parser.get_tag_value(TagPath(app_name='APP1', ifd_number=0, tag_id=0x128))

    @property
    def whitepoint(self) -> Optional[list[Fraction]]:
        return self._parser.get_tag_value(TagPath(app_name='APP1', ifd_number=0, tag_id=0x13E))

    @property
    def primary_chromaticities(self) -> Optional[list[Fraction]]:
        return self._parser.get_tag_value(TagPath(app_name='APP1', ifd_number=0, tag_id=0x13F))

    @property
    def ycbcr_coefficients(self) -> Optional[list[Fraction]]:
        return self._parser.get_tag_value(TagPath(app_name='APP1', ifd_number=0, tag_id=0x211))

    @property
    def reference_black_white(self) -> Optional[list[Fraction]]:
        return self._parser.get_tag_value(TagPath(app_name='APP1', ifd_number=0, tag_id=0x214))

    @property
    def datetime(self) -> Optional[str]:
        return self._parser.get_tag_value(TagPath(app_name='APP1', ifd_number=0, tag_id=0x132))

    @property
    def image_description(self) -> Optional[str]:
        return self._parser.get_tag_value(TagPath(app_name='APP1', ifd_number=0, tag_id=0x10E))

    @property
    def make(self) -> Optional[str]:
        return self._parser.get_tag_value(TagPath(app_name='APP1', ifd_number=0, tag_id=0x10F))

    @property
    def model(self) -> Optional[str]:
        return self._parser.get_tag_value(TagPath(app_name='APP1', ifd_number=0, tag_id=0x110))

    @property
    def software(self) -> Optional[str]:
        return self._parser.get_tag_value(TagPath(app_name='APP1', ifd_number=0, tag_id=0x131))

    @property
    def artist(self) -> Optional[str]:
        return self._parser.get_tag_value(TagPath(app_name='APP1', ifd_number=0, tag_id=0x13B))

    @property
    def copyright(self) -> Optional[str]:
        return self._parser.get_tag_value(TagPath(app_name='APP1', ifd_number=0, tag_id=0x8298))

    @property
    def exif_ifd_offset(self) -> Optional[int]:
        return self._parser.get_tag_value(TagPath(app_name='APP1', ifd_number=0, tag_id=0x8769))

    @property
    def gps_ifd_offset(self) -> Optional[int]:
        return self._parser.get_tag_value(TagPath(app_name='APP1', ifd_number=0, tag_id=0x8825))

    @property
    def interop_ifd_offset(self) -> Optional[int]:
        return self._parser.get_tag_value(TagPath(app_name='APP1', ifd_number=0, tag_id=0xA005))

    # Exif Sub IFD fields

    @property
    def exif_version(self) -> Optional[str]:
        version = get_sub_ifd_tag_value(tag=0x9000, ifd=self._exif_sub_ifd())
        if version is None: return None
        assert isinstance(version, Iterable)
        return ''.join(map(chr, version))

    @property
    def flashpix_version(self) -> Optional[str]:
        version = get_sub_ifd_tag_value(tag=0xA000, ifd=self._exif_sub_ifd())
        if version is None: return None
        assert isinstance(version, Iterable)
        return ''.join(map(chr, version))

    @property
    def color_space(self) -> Optional[int]:
        return get_sub_ifd_tag_value(tag=0xA001, ifd=self._exif_sub_ifd())

    @property
    def components_config(self) -> Optional[tuple[int]]:
        return get_sub_ifd_tag_value(tag=0x9101, ifd=self._exif_sub_ifd())

    @property
    def compressed_bpp(self) -> Optional[Fraction]:
        return get_sub_ifd_tag_value(tag=0x9102, ifd=self._exif_sub_ifd())

    @property
    def pixel_x_dimension(self) -> Optional[int]:
        return get_sub_ifd_tag_value(tag=0xA002, ifd=self._exif_sub_ifd())

    @property
    def pixel_y_dimension(self) -> Optional[int]:
        return get_sub_ifd_tag_value(tag=0xA003, ifd=self._exif_sub_ifd())

    @property
    def marker_note(self) -> Optional[ValueType]:
        return get_sub_ifd_tag_value(tag=0x927C, ifd=self._exif_sub_ifd())

    @property
    def user_comment(self) -> Optional[str]:
        return get_sub_ifd_tag_value(tag=0x9286, ifd=self._exif_sub_ifd())

    @property
    def related_sound_file(self) -> Optional[str]:
        return get_sub_ifd_tag_value(tag=0xA004, ifd=self._exif_sub_ifd())

    @property
    def datetime_original(self) -> Optional[str]:
        return get_sub_ifd_tag_value(tag=0x9001, ifd=self._exif_sub_ifd())

    @property
    def datetime_digitized(self) -> Optional[str]:
        return get_sub_ifd_tag_value(tag=0x9004, ifd=self._exif_sub_ifd())

    @property
    def sub_sec_time(self) -> Optional[str]:
        return get_sub_ifd_tag_value(tag=0x9290, ifd=self._exif_sub_ifd())

    @property
    def sub_sec_time_original(self) -> Optional[str]:
        return get_sub_ifd_tag_value(tag=0x9291, ifd=self._exif_sub_ifd())

    @property
    def sub_sec_time_digitized(self) -> Optional[str]:
        return get_sub_ifd_tag_value(tag=0x9292, ifd=self._exif_sub_ifd())

    @property
    def image_unique_id(self) -> Optional[str]:
        return get_sub_ifd_tag_value(tag=0xA420, ifd=self._exif_sub_ifd())

    @property
    def exposure_time(self) -> Optional[Fraction]:
        return get_sub_ifd_tag_value(tag=0x829A, ifd=self._exif_sub_ifd())

    @property
    def f_number(self) -> Optional[Fraction]:
        return get_sub_ifd_tag_value(tag=0x829D, ifd=self._exif_sub_ifd())

    @property
    def exposure_program(self) -> Optional[int]:
        return get_sub_ifd_tag_value(tag=0x8822, ifd=self._exif_sub_ifd())

    @property
    def spectral_sensitivity(self) -> Optional[str]:
        return get_sub_ifd_tag_value(tag=0x8824, ifd=self._exif_sub_ifd())

    @property
    def iso_speed(self) -> Optional[int]:
        return get_sub_ifd_tag_value(tag=0x8827, ifd=self._exif_sub_ifd())

    @property
    def oecf(self) -> Optional[ValueType]:
        return get_sub_ifd_tag_value(tag=0x8828, ifd=self._exif_sub_ifd())

    @property
    def shutter_speed(self) -> Optional[Fraction]:
        return get_sub_ifd_tag_value(tag=0x9201, ifd=self._exif_sub_ifd())

    @property
    def aperture_value(self) -> Optional[Fraction]:
        return get_sub_ifd_tag_value(tag=0x9202, ifd=self._exif_sub_ifd())

    @property
    def brightness_value(self) -> Optional[Fraction]:
        return get_sub_ifd_tag_value(tag=0x9203, ifd=self._exif_sub_ifd())

    @property
    def exposure_bias_value(self) -> Optional[Fraction]:
        return get_sub_ifd_tag_value(tag=0x9204, ifd=self._exif_sub_ifd())

    @property
    def max_aperture_value(self) -> Optional[Fraction]:
        return get_sub_ifd_tag_value(tag=0x9205, ifd=self._exif_sub_ifd())

    @property
    def subject_distance(self) -> Optional[Fraction]:
        return get_sub_ifd_tag_value(tag=0x9206, ifd=self._exif_sub_ifd())

    @property
    def metering_mode(self) -> Optional[int]:
        return get_sub_ifd_tag_value(tag=0x9207, ifd=self._exif_sub_ifd())

    @property
    def light_source(self) -> Optional[int]:
        return get_sub_ifd_tag_value(tag=0x9208, ifd=self._exif_sub_ifd())

    @property
    def flash(self) -> Optional[int]:
        return get_sub_ifd_tag_value(tag=0x9209, ifd=self._exif_sub_ifd())

    @property
    def focal_length(self) -> Optional[Fraction]:
        return get_sub_ifd_tag_value(tag=0x920A, ifd=self._exif_sub_ifd())

    @property
    def subject_area(self) -> Optional[int]:
        return get_sub_ifd_tag_value(tag=0x9214, ifd=self._exif_sub_ifd())

    @property
    def flash_energy(self) -> Optional[Fraction]:
        return get_sub_ifd_tag_value(tag=0xA20B, ifd=self._exif_sub_ifd())

    @property
    def spatial_frequency_response(self) -> Optional[ValueType]:
        return get_sub_ifd_tag_value(tag=0xA20C, ifd=self._exif_sub_ifd())

    @property
    def focal_plane_x_resolution(self) -> Optional[Fraction]:
        return get_sub_ifd_tag_value(tag=0xA20E, ifd=self._exif_sub_ifd())

    @property
    def focal_plane_y_resolution(self) -> Optional[Fraction]:
        return get_sub_ifd_tag_value(tag=0xA20F, ifd=self._exif_sub_ifd())

    @property
    def focal_plane_resolution_unit(self) -> Optional[int]:
        return get_sub_ifd_tag_value(tag=0xA210, ifd=self._exif_sub_ifd())

    @property
    def subject_location(self) -> Optional[int]:
        return get_sub_ifd_tag_value(tag=0xA214, ifd=self._exif_sub_ifd())

    @property
    def exposure_index(self) -> Optional[Fraction]:
        return get_sub_ifd_tag_value(tag=0xA215, ifd=self._exif_sub_ifd())

    @property
    def sensing_method(self) -> Optional[int]:
        return get_sub_ifd_tag_value(tag=0xA217, ifd=self._exif_sub_ifd())

    @property
    def file_source(self) -> Optional[ValueType]:
        return get_sub_ifd_tag_value(tag=0xA300, ifd=self._exif_sub_ifd())

    @property
    def scene_type(self) -> Optional[ValueType]:
        return get_sub_ifd_tag_value(tag=0xA301, ifd=self._exif_sub_ifd())

    @property
    def cfa_pattern(self) -> Optional[ValueType]:
        return get_sub_ifd_tag_value(tag=0xA302, ifd=self._exif_sub_ifd())

    @property
    def custom_rendered(self) -> Optional[int]:
        return get_sub_ifd_tag_value(tag=0xA401, ifd=self._exif_sub_ifd())

    @property
    def exposure_mode(self) -> Optional[int]:
        return get_sub_ifd_tag_value(tag=0xA402, ifd=self._exif_sub_ifd())

    @property
    def white_balance(self) -> Optional[int]:
        return get_sub_ifd_tag_value(tag=0xA403, ifd=self._exif_sub_ifd())

    @property
    def digital_zoom_ratio(self) -> Optional[Fraction]:
        return get_sub_ifd_tag_value(tag=0xA404, ifd=self._exif_sub_ifd())

    @property
    def focal_length_35mm(self) -> Optional[int]:
        return get_sub_ifd_tag_value(tag=0xA405, ifd=self._exif_sub_ifd())

    @property
    def scene_capture_type(self) -> Optional[int]:
        return get_sub_ifd_tag_value(tag=0xA406, ifd=self._exif_sub_ifd())

    @property
    def gain_control(self) -> Optional[Fraction]:
        return get_sub_ifd_tag_value(tag=0xA407, ifd=self._exif_sub_ifd())

    @property
    def contrast(self) -> Optional[int]:
        return get_sub_ifd_tag_value(tag=0xA408, ifd=self._exif_sub_ifd())

    @property
    def saturation(self) -> Optional[int]:
        return get_sub_ifd_tag_value(tag=0xA409, ifd=self._exif_sub_ifd())

    @property
    def sharpness(self) -> Optional[int]:
        return get_sub_ifd_tag_value(tag=0xA40A, ifd=self._exif_sub_ifd())

    @property
    def device_setting_description(self) -> Optional[Fraction]:
        return get_sub_ifd_tag_value(tag=0xA40B, ifd=self._exif_sub_ifd())

    @property
    def subject_distance_range(self) -> Optional[int]:
        return get_sub_ifd_tag_value(tag=0xA40C, ifd=self._exif_sub_ifd())


    @property
    def is_available(self) -> bool:
        app1 = self._parser.get_segment('APP1')
        if app1 is None:
            return False

        if app1.name.upper() != 'EXIF':
            return False

        ifd0 = app1.ifd(0)
        if ifd0 is None:
            return False

        return True


    def __init__(self, parser):
        from jparse.JpegMetaParser import JpegMetaParser
        self._parser: JpegMetaParser = parser

        # _exif_sub_ifd() private fields
        self.__exif_sub_ifd = None
        self.__exif_sub_ifd_loaded = False


    def __str__(self) -> str:
        result = f'Exif Info:\n'
        for attr in self.__dir__():
            if attr[0] == '_': continue
            if attr == 'is_available': continue

            value = getattr(self, attr)
            if value is None: continue

            if isinstance(value, Fraction):
                value = float(value)

            result += f'\t{attr:28s}: {value}\n'
        return result


    def _exif_sub_ifd(self) -> Union[IFD, None]:
        if self.__exif_sub_ifd_loaded:
            return self.__exif_sub_ifd

        if self.exif_ifd_offset is None:
            return None

        # note: if self.exif_ifd_offset != None then IFD1 and APP1.tiff_header also exists
        tiff_header = self._parser['APP1'].tiff_header
        exif_sub_ifd_offset = self.exif_ifd_offset + tiff_header.offset

        self._parser.stream.seek(exif_sub_ifd_offset)
        self.__exif_sub_ifd = IFD.parse(stream=self._parser.stream, tiff_header=tiff_header, index=0x8769)
        logger.debug(f'Exif subIFD: {self.__exif_sub_ifd}')

        self.__exif_sub_ifd_loaded = True
        return self.__exif_sub_ifd


def get_sub_ifd_tag_value(tag: int, ifd: Union[IFD, None]) -> Union[ValueType, None]:
    if ifd is None:
        return None

    field = ifd.get_field(tag=tag)
    if field is None:
        return None

    return field.value