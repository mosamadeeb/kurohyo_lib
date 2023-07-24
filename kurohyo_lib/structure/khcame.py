from typing import List

from mathutils import Vector

from ..util import BinaryReader, BrStruct
from .common import read_vector, write_vector
from .khfile import KHFile, KHString


class KHCame(KHFile):
    nodes: List['KHCameNode']

    def __br_read__(self, br: BinaryReader):
        node_count = br.read_uint16()
        self.nodes = br.read_struct(KHCameNode, node_count)

    def __br_write__(self, br: BinaryReader):
        br.write_uint16(len(self.nodes))
        br.write_struct(self.nodes)


class KHCameNode(BrStruct):
    name: str

    initial_location: Vector
    initial_focus_point: Vector
    initial_roll_degrees: float
    initial_fov_degrees: float

    clip_start: float
    clip_end: float

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

    def __br_write__(self, br: BinaryReader):
        # flags
        br.write_uint16(0x800)
        br.write_struct(KHString(), self.name)

        # camera_flags
        br.write_uint32(1)

        write_vector(br, self.initial_location)
        write_vector(br, self.initial_focus_point)
        br.write_float(self.initial_roll_degrees)
        br.write_float(self.initial_fov_degrees)
        br.write_float(self.clip_start)
        br.write_float(self.clip_end)
