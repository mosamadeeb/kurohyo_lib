from typing import Dict

from ..util import BinaryReader, BrStruct
from .kh_enums import KHMateMaterialFlag
from .khfile import KHFile, KHString


class KHImag(KHFile):
    def __br_read__(self, br: BinaryReader):
        texture_count = br.read_uint16()

        self.textures: Dict[int, KHImagTexture] = {
            texture.hash: texture
            for texture in br.read_struct(KHImagTexture, texture_count)
        }


class KHImagTexture(BrStruct):
    def __br_read__(self, br: BinaryReader):
        flags = KHMateMaterialFlag(br.read_uint16())
        self.hash = br.read_uint32()
        self.name: str = br.read_struct(KHString).data
