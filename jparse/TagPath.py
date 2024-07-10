from typing import NamedTuple


class TagPath(NamedTuple):
    app_name  : str
    ifd_number: int
    tag_id    : int