from typing import List, Optional

from mathutils import Euler, Vector

from ..util import BinaryReader, BrStruct
from .common import read_vector
from .kh_enums import KHModeModelFlag, KHModeNodeFlag, KHModeVertexFlag
from .khfile import KHFile, KHString


class KHMode(KHFile):
    root_node: 'KHModeNode'

    def __br_read__(self, br: BinaryReader):
        self.root_node = br.read_struct(KHModeNode)


def read_strips(br: BinaryReader, count):
    faces = list()

    if count < 3:
        raise Exception('Could not read strips - insufficient strip count')

    strips = iter(br.read_uint16(count))

    try:
        change_dir = False
        f1, f2 = next(strips), next(strips)

        while True:
            f3 = next(strips)

            # This does not filter degenerate faces
            faces.append((f1, f3, f2) if change_dir else (f1, f2, f3))

            f1 = f2
            f2 = f3
            change_dir = not change_dir

    except StopIteration:
        pass

    return faces


class KHModeNode(BrStruct):
    meshes: Optional[List['KHModeMesh']]

    def __br_read__(self, br: BinaryReader):
        flags = KHModeNodeFlag(br.read_uint16())
        self.name: str = br.read_struct(KHString).data

        # Unsure what this does, but it does not affect the struct reading
        self.model_flags = KHModeModelFlag(br.read_uint32())

        self.is_clone = KHModeNodeFlag.CLONE in flags
        if self.is_clone:
            self.instance_scale = read_vector(br)
            self.instance_rotation = Euler(read_vector(br)[:])
            self.instance_location = read_vector(br)

            self.cloned_node_name: str = br.read_struct(KHString).data

        self.is_skinned = KHModeNodeFlag.UNSKINNED not in flags
        self.has_model = KHModeNodeFlag.SKINNED in flags or not self.is_skinned
        if self.has_model:
            unk_float = br.read_float()
            unk_byte = br.read_uint8()

            self.bounding_box_points = read_vector(br, 2)

            mesh_count = br.read_uint16() if self.is_skinned else 1
            self.meshes = br.read_struct(KHModeMesh, mesh_count, self.is_skinned)

            self.material_name: str = br.read_struct(KHString).data

        child_count = br.read_uint16()
        self.children = br.read_struct(KHModeNode, child_count)

    def merge_meshes(self) -> 'KHModeMesh':
        if not self.has_model:
            return None

        new_mesh = KHModeMesh()

        new_mesh.vertex_flags = 0
        new_mesh.bone_hashes = list()
        new_mesh.vertices = list()
        new_mesh.faces = list()

        offset = 0
        for mesh in self.meshes:
            # Not sure if ORing the flags is a good idea, but they should generally be the same
            new_mesh.vertex_flags |= mesh.vertex_flags
            new_mesh.bone_hashes.extend(mesh.bone_hashes or [])
            new_mesh.vertices.extend(mesh.vertices)
            new_mesh.faces.extend(map(lambda f: tuple(map(lambda x: x + offset, f)), mesh.faces))

            offset += len(mesh.vertices)

        return new_mesh


class KHModeMesh(BrStruct):
    vertices: List['KHModeVertex']

    def __br_read__(self, br: BinaryReader, is_skinned):
        self.bone_hashes = None

        if is_skinned:
            bone_count = br.read_uint16()

            # FNV0 hash with prime 0x811C9DC5
            self.bone_hashes = br.read_uint32(bone_count)

        triangle_count = br.read_uint16()
        self.faces = list(map(lambda _: br.read_uint16(3), range(triangle_count)))

        self.vertex_flags = KHModeVertexFlag(br.read_uint32())
        vertex_count = br.read_uint16()
        self.vertices = br.read_struct(KHModeVertex, vertex_count, self.bone_hashes, self.vertex_flags)

        has_strips = br.read_uint16() != 0

        if has_strips:
            strip_count = br.read_uint16()
            self.faces.extend(read_strips(br, strip_count))


class KHModeVertex(BrStruct):
    def __br_read__(self, br: BinaryReader, bone_hashes, flags: KHModeVertexFlag):
        weight_count = 1
        if KHModeVertexFlag.HAS_4_WEIGHTS in flags:
            weight_count += 4
        if KHModeVertexFlag.HAS_2_WEIGHTS in flags:
            weight_count += 2
        if KHModeVertexFlag.HAS_1_WEIGHT in flags:
            weight_count += 1

        self.weights = br.read_float(weight_count) if KHModeVertexFlag.HAS_WEIGHTS in flags else None
        self.bone_hashes = tuple(bone_hashes) if bone_hashes else None

        self.uv = None
        if KHModeVertexFlag.HAS_UV_SHORT in flags:
            self.uv = tuple(map(lambda x: float(x) / 0x7FFF, br.read_uint16(2)))
        elif KHModeVertexFlag.HAS_UV_FLOAT in flags:
            self.uv = br.read_float(2)

        self.color = None
        if KHModeVertexFlag.HAS_COLOR_RGBA in flags:
            self.color = br.read_uint8(4)
        elif KHModeVertexFlag.HAS_COLOR_UNK in flags:
            # NOTE: Unsure if this being read correctly
            color = br.read_uint16()
            color = ((color >> 12) & 0xF, (color >> 8) & 0xF, (color >> 4) & 0xF, color & 0xF)
            self.color = tuple(map(lambda c: c * 17, color))

            # # Just skip color since we don't know how it's read
            # br.read_uint16()

        self.normal = None
        if KHModeVertexFlag.HAS_NORMAL in flags:
            self.normal = Vector(tuple(map(lambda x: float(x) / 0x7FFF, br.read_int16(3))))

            if KHModeVertexFlag.HAS_COLOR_UNK not in flags:
                # Padding
                br.read_int16()

        self.location = read_vector(br) if KHModeVertexFlag.HAS_LOCATION in flags else None
