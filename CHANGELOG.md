# v0.2.0 - 11.07.2024

##### New
* `x3` speed up via lazy loading.
* `[JpegMetaParser]` exif info parsing (`APP1`).
* `[JpegMetaParser]` indexing support for segments: e.g. `parser['APP1']`.
* `[JpegMetaParser]` iterator support: `for segment in parser: ...`.
* `[JpegMetaParser]` support for `len()` function: `len(parser)` -> number of segments.
* `[AppSegment]` indexing support: e.g. `ifd = segment[2]`.
* `[AppSegment]` iterator support: `for ifd in segment: ...`.
* `[IFD]` indexing support for IFD: e.g. `ifd[0x101]`.
* `[IFD]` support for `len()` function: `len(ifd)` -> number of IFD's fields.
* `[IFD]` iterator support: `for field in ifd: ...`.
* `BSD-3-Clause` license added.

##### Changed
* `[JpegMetaParser]` property `app_segments` returns names only. Use `[]` or `get_segment()` to access `*Segment` object. 
* `AppSegment.ifd` was changed from `tuple` to function (to avoid loading of all `IFDs`). 
* `Segments` and `IFDs` are maximally lazy. 

##### Fixed
* skip `APP2` parsing because it doesn't contain any `IFDs` usually.


# v0.1.1 - 29.08.2021

##### New
* `setup.py` added 


# v0.1.0 - 09.04.2021

Initial version