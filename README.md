JPEG structure and Exif metadata parser.

## JPEG File Structure

![JPEG Structure](docs/jpeg_format.png)

## Requirements

* Python >= 3.7
* No extra dependencies


## Logging

### JPEG-file segments enumeration

```python
import logging
from jparse import JpegMetaParser

logging.basicConfig(format='[%(name)s][%(levelname)s]: %(message)s', level=logging.DEBUG)


with open('image.jpg', 'rb') as f:
        parser = JpegMetaParser(f)
```
output:
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
```


## References

* [Exif Format v2](https://www.exif.org/Exif2-2.PDF)
* [ExifLibrary for .NET](https://www.codeproject.com/Articles/43665/ExifLibrary-for-NET)
* [The Metadata in JPEG files](https://dev.exiv2.org/projects/exiv2/wiki/The_Metadata_in_JPEG_files)
* [Manufacturer-specific Tags](https://exiftool.org/TagNames/JPEG.html)