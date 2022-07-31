from typing import List

from ..util import BinaryReader, BrStruct
from .khfile import KHFile, KHString


class KHSkel(KHFile):
    def __br_read__(self, br: BinaryReader):
        self.root_bone: KHSkelBone = br.read_struct(KHSkelBone)


class KHSkelBone(BrStruct):
    children: List['KHSkelBone']

    def __br_read__(self, br: BinaryReader):
        flags = br.read_uint16()
        self.name: str = br.read_struct(KHString).data

        value_count = br.read_uint32()

        if value_count != 1:
            raise Exception(f'Unexpected value for KHSkelBone value count ({value_count}) for bone \"{self.name}\"')

        child_count = br.read_uint16()
        self.children = br.read_struct(KHSkelBone, child_count)
