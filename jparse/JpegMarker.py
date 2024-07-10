from typing import Union


class JpegMarker:
    MARKER_SIZE: int = 2  # bytes
    LENGTH_SIZE: int = 2  # bytes
    START: int = 0xFF

    @property
    def signature(self) -> int:
        return self._signature

    @property
    def name(self) -> str:
        return self._name

    @property
    def info(self) -> str:
        return self._info

    @property
    def is_mask(self) -> bool:
        return self._is_mask


    def __init__(self, signature: int,
                       name     : str,
                       info     : str,
                       is_mask  : bool=False):
        self._signature = signature
        self._name = name
        self._info = info
        self._is_mask = is_mask


    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(marker=0x{self.signature:04X}, ' \
                                         f'name={repr(self.name)}, '        \
                                         f'is_mask={self.is_mask})'

    def __str__(self) -> str:
        return f'{self.name}[0x{self.signature:04X}]'


    def __eq__(self, other: Union[int, 'JpegMarker']) -> bool:
        if isinstance(other, JpegMarker):
            return self.signature == other.signature
        elif type(other) == int:
            return self.signature == other
        else:
            raise RuntimeError(f'unsupported type {type(other)}')


    def copy(self) -> 'JpegMarker':
        return JpegMarker(signature=self.signature,
                          name=self.name,
                          info=self.info,
                          is_mask=self.is_mask)


    def extract_index(self, signature: int) -> int:
        index_mask = self.signature & 0xF
        return signature & index_mask

    def check_mask(self, signature: int) -> bool:
        assert self.is_mask, 'format of the marker must be a mask for this action'
        index_mask = self.signature & 0xF
        segment_mask = ~index_mask
        return signature & segment_mask == self.signature & segment_mask

    def set_index(self, index: int):
        assert self.is_mask, 'index can be set only for masked markers'
        assert 0 <= index <= (self.signature & 0xF), 'index is out of range'

        self._name = f'{self.name}{index}'
        self._signature = (self.signature & 0xFFF0) + index
        self._is_mask = False


    @classmethod
    def detect(cls, signature: int) -> 'JpegMarker':
        if (signature >> 8) != JpegMarker.START:
            raise RuntimeError(f'invalid signature: 0x{signature:04X}')

        marker = SIGNATURE_TO_MARKER_MAPPING.get(signature)
        if marker is not None:
            return marker

        # check for custom APP0-APP15
        if APPn.check_mask(signature):
            app_marker = APPn.copy()
            app_marker.set_index(index=APPn.extract_index(signature))
            return app_marker

        # check for RST0-RST7
        if RSTn.check_mask(signature):
            rst_marker = RSTn.copy()
            rst_marker.set_index(index=RSTn.extract_index(signature))
            return rst_marker

        return JpegMarker(signature=signature,
                          name=f'UNK[0x{signature:04X}]',
                          info='Unknown')


SOI = JpegMarker(signature=0xFFD8, name='SOI', info='Start of Image')
EOI = JpegMarker(signature=0xFFD9, name='EOI', info='End of Image')
SOF0 = JpegMarker(signature=0xFFC0, name='SOF0', info='Start of Frame (Baseline)')
SOF2 = JpegMarker(signature=0xFFC2, name='SOF2', info='Start of Frame (Progressive)')
DHT = JpegMarker(signature=0xFFC4, name='DHT', info='Define Huffman Table(s)')
DQT = JpegMarker(signature=0xFFDB, name='DQT', info='Define Quantization Table(s)')
DRI = JpegMarker(signature=0xFFDD, name='DRI', info='Define Restart Interval')
SOS = JpegMarker(signature=0xFFDA, name='SOS', info='Start of Scan')
COM = JpegMarker(signature=0xFFFE, name='COM', info='Comment')

RSTn = JpegMarker(signature=0xFFD7, name='RST', is_mask=True, info='Restart')
APPn = JpegMarker(signature=0xFFEF, name='APP', is_mask=True, info='Application-specific')

APP0 = JpegMarker(signature=0xFFE0, name='APP0', is_mask=False, info='JFIF Segment')
APP1 = JpegMarker(signature=0xFFE1, name='APP1', is_mask=False, info='Exif Attribute Information')
APP2 = JpegMarker(signature=0xFFE2, name='APP2', is_mask=False, info='Exif extended data')


SIGNATURE_TO_MARKER_MAPPING = {
    SOI.signature : SOI,
    EOI.signature : EOI,
    SOF0.signature: SOF0,
    SOF2.signature: SOF2,
    DHT.signature : DHT,
    DQT.signature : DQT,
    DRI.signature : DRI,
    SOS.signature : SOS,
    APP0.signature: APP0,
    APP1.signature: APP1,
    APP2.signature: APP2,
}