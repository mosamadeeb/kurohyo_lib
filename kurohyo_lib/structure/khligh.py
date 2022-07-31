from ..util import BinaryReader, BrStruct
from .khfile import KHFile, KHString


class KHLigh(KHFile):
    def __br_read__(self, br: BinaryReader):
        node_count = br.read_uint16()

        self.nodes = br.read_struct(KHLighNode, node_count)


class KHLighNode(BrStruct):
    def __br_read__(self, br: BinaryReader):
        flags = br.read_uint16()
        self.name: str = br.read_struct(KHString).data

        unk_count = br.read_uint32()

        self.unk_floats0 = br.read_float(3)
        self.unk_bytes = br.read_uint8(13)
        self.unk_floats1 = br.read_float(5)
