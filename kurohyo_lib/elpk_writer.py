from typing import List

from .structure import KHFile, KHFILE_TYPE_TO_MAGIC
from .util import BinaryReader, Endian


def write_elpk_page(elpk_page_files: List[KHFile]) -> bytearray:
    br = BinaryReader(endianness=Endian.LITTLE)

    for file in elpk_page_files:
        if magic := KHFILE_TYPE_TO_MAGIC.get(type(file)):
            br.write_str_fixed(magic, 4)
            br.write_struct(file)
        else:
            raise KeyError(f'Unknown KHFile type: {type(file)}')

    # Ending magic
    br.write_str('end ')

    return br.buffer()
