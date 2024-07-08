# jparse

[![python](https://img.shields.io/badge/Python-3.7-blue?logo=python&logoColor=white)](https://docs.python.org/3/whatsnew/3.7.html)
[![license](https://img.shields.io/badge/License-BSD%203--Clause-green)](https://choosealicense.com/licenses/mit/)

JPEG structure and Exif metadata parsing library.

## JPEG File Structure

<img src='docs/jpeg_format.png' width='600'>

## Requirements

* Python >= 3.7
* No extra dependencies


## Install

```
pip install "jparse @ git+https://github.com/MakarovDi/jparse.git@master"
```

## Examples

### Reading TAG value

```python
from jparse import JpegMetaParser, TagPath

tag_image_width = TagPath(app_name='APP1', ifd_number=0, tag_id=0x0100)
tag_date_time = TagPath(app_name='APP1', ifd_number=0, tag_id=0x0132)

with open('image.jpg', 'rb') as f:
    parser = JpegMetaParser(f)

    image_width = parser.get_tag_value(tag_image_width)
    date_time = parser.get_tag_value(tag_date_time)

print(f'Image Width: {image_width}')
print(f'DateTime: {date_time}')
```

Output:
```
Image Width: 4096
DateTime: 2021:03:29 21:27:04
```

### Listing Segments

```python
from jparse import JpegMetaParser

with open('image.jpg', 'rb') as f:
    parser = JpegMetaParser(f)
    
    for seg in parser:
        print(seg)
```

Output:
```
APP1 - Exif - offset: 0x00000002, 33288 bytes
APP0 - JFIF - offset: 0x00036680, 18 bytes
```

### Listing IFD's fields

```python
from jparse import JpegMetaParser

with open('image.jpg', 'rb') as f:
    parser = JpegMetaParser(f)
    
    app1 = parser['APP1'] # select segment
    ifd1 = app1.ifd[1] # select IFD

    # pring all tags and values
    for tag_id, field in ifd1.fields.items():
        print(f'TAG 0x{tag_id:04X}: {field.value}')
```

Output:
```
TAG 0x0100: 512
TAG 0x0101: 384
TAG 0x0103: 6
TAG 0x0112: 0
TAG 0x011A: 72
TAG 0x011B: 72
...
```


## Debug Logging

```python
import logging
from jparse import JpegMetaParser

logging.basicConfig(format='[%(name)s][%(levelname)s]: %(message)s', level=logging.DEBUG)


with open('image.jpg', 'rb') as f:
    parser = JpegMetaParser(f)
    app1 = parser['APP1']
    app1.load()
```

Output:
```
[jparse][DEBUG]: 0x00000000 -> SOI  : 2 bytes
[jparse][DEBUG]: 0x00000002 -> APP1 : 30251 bytes
[jparse][DEBUG]: 0x0000762D -> APP7 : 47240 bytes
[jparse][DEBUG]: 0x00012EB5 -> APP8 : 55790 bytes
[jparse][DEBUG]: 0x000208A3 -> APP9 : 43434 bytes
[jparse][DEBUG]: 0x0002B24D -> APP10: 43094 bytes
[jparse][DEBUG]: 0x00035AA3 -> APP0 : 18 bytes
[jparse][DEBUG]: 0x00035AB5 -> DQT  : 69 bytes
[jparse][DEBUG]: 0x00035AFA -> DQT  : 69 bytes
[jparse][DEBUG]: 0x00035B3F -> SOF0 : 19 bytes
[jparse][DEBUG]: 0x00035B52 -> DHT  : 33 bytes
[jparse][DEBUG]: 0x00035B73 -> DHT  : 183 bytes
[jparse][DEBUG]: 0x00035C2A -> DHT  : 33 bytes
[jparse][DEBUG]: 0x00035C4B -> DHT  : 183 bytes
[jparse][DEBUG]: 0x00035D02 -> DRI  : 6 bytes
[jparse][DEBUG]: 0x00035D08 -> SOS  : 14 bytes
[jparse][DEBUG]: [APP1] segment loading...
[jparse][DEBUG]: -> name: Exif
[jparse][DEBUG]: -> TiffHeader(byte_order=<ByteOrder.BIG_ENDIAN: 1>, ifd0_offset=8)
[jparse][DEBUG]: -> IDF #0, offset=0x00000014
[jparse][DEBUG]: 		Field[0x0100]:     <FieldType.Short: 3>, count=1  , size=12, field_offset=0x00000016, value_offset=0x0000001E
[jparse][DEBUG]: 		Field[0x0101]:     <FieldType.Short: 3>, count=1  , size=12, field_offset=0x00000022, value_offset=0x0000002A
[jparse][DEBUG]: 		Field[0x0102]:     <FieldType.Short: 3>, count=3  , size=20, field_offset=0x0000002E, value_offset=0x000000EA
[jparse][DEBUG]: 		Field[0x010F]:     <FieldType.ASCII: 2>, count=8  , size=20, field_offset=0x0000003A, value_offset=0x000000C2
[jparse][DEBUG]: 		Field[0x0110]:     <FieldType.ASCII: 2>, count=8  , size=20, field_offset=0x00000046, value_offset=0x000000CA
[jparse][DEBUG]: 		Field[0x0112]:     <FieldType.Short: 3>, count=1  , size=12, field_offset=0x00000052, value_offset=0x0000005A
[jparse][DEBUG]: 		Field[0x011A]:  <FieldType.Rational: 5>, count=1  , size=20, field_offset=0x0000005E, value_offset=0x000000D2
[jparse][DEBUG]: 		Field[0x011B]:  <FieldType.Rational: 5>, count=1  , size=20, field_offset=0x0000006A, value_offset=0x000000DA
[jparse][DEBUG]: 		Field[0x0128]:     <FieldType.Short: 3>, count=1  , size=12, field_offset=0x00000076, value_offset=0x0000007E
[jparse][DEBUG]: 		Field[0x0131]:     <FieldType.ASCII: 2>, count=8  , size=20, field_offset=0x00000082, value_offset=0x000000E2
[jparse][DEBUG]: 		Field[0x0132]:     <FieldType.ASCII: 2>, count=20 , size=32, field_offset=0x0000008E, value_offset=0x000000F0
[jparse][DEBUG]: 		Field[0x0213]:     <FieldType.Short: 3>, count=1  , size=12, field_offset=0x0000009A, value_offset=0x000000A2
[jparse][DEBUG]: 		Field[0x8769]:      <FieldType.Long: 4>, count=1  , size=12, field_offset=0x000000A6, value_offset=0x000000AE
[jparse][DEBUG]: 		Field[0xA40B]: <FieldType.Undefined: 7>, count=4  , size=12, field_offset=0x000000B2, value_offset=0x000000BA
[jparse][DEBUG]: -> IDF #1, offset=0x000004BC
[jparse][DEBUG]: 		Field[0x0100]:     <FieldType.Short: 3>, count=1  , size=12, field_offset=0x000004BE, value_offset=0x000004C6
[jparse][DEBUG]: 		Field[0x0101]:     <FieldType.Short: 3>, count=1  , size=12, field_offset=0x000004CA, value_offset=0x000004D2
[jparse][DEBUG]: 		Field[0x0103]:     <FieldType.Short: 3>, count=1  , size=12, field_offset=0x000004D6, value_offset=0x000004DE
[jparse][DEBUG]: 		Field[0x0112]:     <FieldType.Short: 3>, count=1  , size=12, field_offset=0x000004E2, value_offset=0x000004EA
[jparse][DEBUG]: 		Field[0x011A]:  <FieldType.Rational: 5>, count=1  , size=20, field_offset=0x000004EE, value_offset=0x0000052E
[jparse][DEBUG]: 		Field[0x011B]:  <FieldType.Rational: 5>, count=1  , size=20, field_offset=0x000004FA, value_offset=0x00000536
[jparse][DEBUG]: 		Field[0x0128]:     <FieldType.Short: 3>, count=1  , size=12, field_offset=0x00000506, value_offset=0x0000050E
[jparse][DEBUG]: 		Field[0x0201]:      <FieldType.Long: 4>, count=1  , size=12, field_offset=0x00000512, value_offset=0x0000051A
[jparse][DEBUG]: 		Field[0x0202]:      <FieldType.Long: 4>, count=1  , size=12, field_offset=0x0000051E, value_offset=0x00000526
...
```

## License

This software is licensed under the `BSD-3-Clause` license.  
See the [LICENSE](LICENSE) file for details.

## Links

* [Description of Exif file format](https://www.media.mit.edu/pia/Research/deepview/exif.html)
* [Exif Format v2](https://www.kodak.com/global/plugins/acrobat/en/service/digCam/exifStandard2.pdf)
* [ExifLibrary for .NET](https://www.codeproject.com/Articles/43665/ExifLibrary-for-NET)
* [The Metadata in JPEG files](https://dev.exiv2.org/projects/exiv2/wiki/The_Metadata_in_JPEG_files)
* [Manufacturer-specific Tags](https://exiftool.org/TagNames/JPEG.html)