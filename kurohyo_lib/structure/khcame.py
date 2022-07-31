from ..util import BinaryReader, BrStruct
from .common import read_vector
from .khfile import KHFile, KHString


class KHCame(KHFile):
    def __br_read__(self, br: BinaryReader):
        node_count = br.read_uint16()
        self.nodes = br.read_struct(KHCameNode, node_count)


class KHCameNode(BrStruct):
    def __br_read__(self, br: BinaryReader):
        flags = br.read_uint16()
        self.name: str = br.read_struct(KHString).data

        camera_flags = br.read_uint32()

        self.initial_location = read_vector(br)
        self.initial_focus_point = read_vector(br)
        self.initial_roll_degrees = br.read_float()
        self.initial_fov_degrees = br.read_float()
        self.clip_start = br.read_float()
        self.clip_end = br.read_float()
