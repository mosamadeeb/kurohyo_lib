from typing import Dict

from mathutils import Euler

from ..util import BinaryReader, BrStruct
from .common import read_vector
from .khfile import KHFile, KHString


class KHBase(KHFile):
    def __br_read__(self, br: BinaryReader):
        self.name: str = br.read_struct(KHString).data
        bone_count = br.read_uint16()

        bone: KHBaseBone
        self.bones: Dict[str, KHBaseBone] = dict()
        for _ in range(bone_count):
            bone = br.read_struct(KHBaseBone)
            self.bones[bone.name] = bone

    def update(self, other: 'KHBase'):
        for name, bone in other.bones.items():
            if name in self.bones:
                self.bones[name].update(bone)


class KHBaseBone(BrStruct):
    def __br_read__(self, br: BinaryReader):
        flags = br.read_uint16()
        self.name: str = br.read_struct(KHString).data

        self.scale = read_vector(br)
        self.rotation = Euler(read_vector(br)[:])
        self.location = read_vector(br)

    def update(self, other: 'KHBaseBone'):
        self.scale.cross(other.scale)
        self.rotation += other.rotation
        self.location += other.location
