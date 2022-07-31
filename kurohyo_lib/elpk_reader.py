import gzip
from typing import Union

from .structure import Elpk
from .util import BinaryReader


def read_elpk(file: Union[str, bytearray]) -> Elpk:
    """Reads an ELPK file and returns an Elpk object.
    If the file has Gzip compression, it will be decompressed before reading.
    :param file: Path to file as a string, or bytes-like object containing the file
    :return: An Elpk object.
    """

    if isinstance(file, str):
        with open(file, 'rb') as f:
            file_bytes = f.read()
    else:
        file_bytes = file

    # Gzip magic
    if file_bytes[:2] == b'\x1f\x8b':
        file_bytes = gzip.decompress(file_bytes)

    with BinaryReader(file_bytes) as br:
        elpk: Elpk = br.read_struct(Elpk)

    return elpk
