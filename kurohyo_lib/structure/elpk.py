from collections import defaultdict
from typing import DefaultDict, List

from ..util import BinaryReader, BrStruct, Whence
from .khbase import KHBase
from .khcame import KHCame
from .khfile import KHFile
from .khimag import KHImag
from .khligh import KHLigh
from .khmate import KHMate
from .khmig import KHMig
from .khmode import KHMode
from .khpose import KHPose
from .khskel import KHSkel

MAGIC_TO_KHFILE_TYPE = {
    'base': KHBase,
    'came': KHCame,
    'imag': KHImag,
    'ligh': KHLigh,
    'mate': KHMate,
    'MIG.': KHMig,
    'mode': KHMode,
    'pose': KHPose,
    'skel': KHSkel,
}

KHFILE_TYPE_TO_MAGIC = dict([(value, key) for key, value in MAGIC_TO_KHFILE_TYPE.items()])

class ElpkPage(BrStruct):
    def __br_read__(self, br: BinaryReader, page_hash, page_size):
        self.page_hash = page_hash
        self.files: DefaultDict[type, List[KHFile]] = defaultdict(list)

        end_offset = br.pos() + page_size

        try:
            while br.pos() < end_offset:
                magic = br.read_str(4)

                if magic == 'end ':
                    break

                file_type = MAGIC_TO_KHFILE_TYPE[magic]
                self.files[file_type].append(br.read_struct(file_type))
        except KeyError:
            print(f'Unsupported file magic: \"{magic}\" - skipping page...')
        except UnicodeDecodeError:
            print(f'Unable to read file magic - skipping page...')


class Elpk(BrStruct):
    def __br_read__(self, br: BinaryReader):
        self.pages: List[ElpkPage] = list()

        try:
            magic = br.read_str(4)
        except:
            raise Exception(f'Unable to read file magic.')

        if magic != 'ELPK':
            # Check if the files are not inside an ELPK container
            if magic in MAGIC_TO_KHFILE_TYPE:
                br.seek(-4, Whence.CUR)
                self.pages.append(br.read_struct(ElpkPage, None, 0, br.size()))
                return

            raise Exception(f'Invalid magic: Expected ELPK, got \"{magic}\"')

        elpk_size = br.read_uint32()
        flags = br.read_uint32()
        padding = br.read_uint32()
        page_count = br.read_uint32()

        for i in range(page_count):
            page_hash = br.read_uint32()
            page_ptr = br.read_uint32()
            page_size = br.read_uint32()

            with br.seek_to(page_ptr):
                try:
                    self.pages.append(br.read_struct(ElpkPage, None, page_hash, page_size))
                except Exception as e:
                    print(e)
                    print(f'Could not read page no. {i} - skipping...')
