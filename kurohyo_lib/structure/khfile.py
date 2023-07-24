from ..util import BinaryReader, BrStruct, Whence


class KHString(BrStruct):
    def __br_read__(self, br: BinaryReader):
        length = br.read_uint16()
        self.data = br.read_str(length)

    def __br_write__(self, br: BinaryReader, data: str):
        br.write_uint16(0)
        length = br.write_str(data)

        with br.seek_to(-(length + 2), whence=Whence.CUR):
            br.write_uint16(length)


class KHFile(BrStruct):
    pass
