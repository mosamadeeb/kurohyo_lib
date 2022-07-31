from ..util import BinaryReader, BrStruct


class KHString(BrStruct):
    def __br_read__(self, br: BinaryReader):
        length = br.read_uint16()
        self.data = br.read_str(length)


class KHFile(BrStruct):
    pass
