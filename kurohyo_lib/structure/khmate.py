from typing import Tuple

from ..util import BinaryReader, BrStruct
from .kh_enums import KHMateMaterialFlag
from .khfile import KHFile, KHString


class KHMate(KHFile):
    materials: Tuple['KHMateMaterial']

    def __br_read__(self, br: BinaryReader):
        material_count = br.read_uint16()
        self.materials = br.read_struct(KHMateMaterial, material_count)


class KHMateMaterial(BrStruct):
    groups: Tuple['KHMateGroup']

    def __br_read__(self, br: BinaryReader):
        flags = KHMateMaterialFlag(br.read_uint16())
        self.name: str = br.read_struct(KHString).data
        self.shader_hash = br.read_uint32()

        self.unk_floats = br.read_float(2)

        # This count is fixed
        self.groups = br.read_struct(KHMateGroup, 5)


class KHMateGroup(BrStruct):
    textures: Tuple['KHMateTexture']

    def __br_read__(self, br: BinaryReader):
        texture_count = br.read_uint16()
        self.textures = br.read_struct(KHMateTexture, texture_count)


class KHMateTexture(BrStruct):
    def __br_read__(self, br: BinaryReader):
        flags = KHMateMaterialFlag(br.read_uint16())
        self.is_texture = KHMateMaterialFlag.IS_TEXTURE in flags
        self.hash = br.read_uint32()
