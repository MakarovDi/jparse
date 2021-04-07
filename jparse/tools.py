import logging
from typing import IO

logger = logging.getLogger('jparse')


def read_bytes_strict(stream: IO, count: int) -> bytes:
    data = stream.read(count)

    if len(data) != count:
        raise RuntimeError('unexpected end of stream')
    
    return data