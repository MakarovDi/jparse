# v0.2.0 - ??.07.2024

##### New
* maximally lazy `AppSegment` -> `x3` speed up.
* `BSD-3-Clause` license added.

##### Changed
* `[JpegMetaParser]` property `app_segments` returns names only. Use `[]` or `get_segment()` to access `*Segment` object. 
* `AppSegment.ifd` was changed from `tuple` to function (to avoid loading of all `IFDs`). 


##### Fixed


# v0.1.1 - 29.08.2021

##### New
* `setup.py` added 


# v0.1.0 - 09.04.2021

Initial version