from enum import IntEnum, auto


class FieldType(IntEnum):
    Byte      = 1  # uint8
    ASCII     = 2  # null-terminated byte array
    Short     = 3  # uint16
    Long      = 4  # uint32
    Rational  = 5  # 2 x uint32
    SByte     = 6  # int8
    Undefined = 7  # byte array
    SShort    = 8  # int16
    SLong     = 9  # int32
    SRational = 10 # 2 x int32
    Float     = 11 # float
    Double    = 12 # double
    Unknown   = auto()

    @property
    def byte_count(self) -> int:
        return { FieldType.Byte     : 1,
                 FieldType.ASCII    : 1,
                 FieldType.Short    : 2,
                 FieldType.Long     : 4,
                 FieldType.Rational : 8,
                 FieldType.SByte    : 1,
                 FieldType.Undefined: 1,
                 FieldType.SShort   : 2,
                 FieldType.SLong    : 4,
                 FieldType.SRational: 8,
                 FieldType.Float    : 4,
                 FieldType.Double   : 8,
                 FieldType.Unknown  : 0 }[self]