from itertools import chain
from math import ceil

from ..util import BinaryReader, BrStruct, Whence
from .kh_enums import KHMigBlockFlag, KHMigImageFormatFlag


# Unswizzle algorithm from here:
# https://github.com/nickworonekin/puyotools/blob/a949eb452e4743b94517ca08e720759cc0381a25/src/PuyoTools.Core/Textures/Gim/GimTextureDecoder.cs#L333
def unswizzle(data, width, height):
    result = list()

    row_blocks = width // 16

    for y in range(height):
        for x in range(width):
            block_x = x // 16
            block_y = y // 8

            block_index = block_x + (block_y * row_blocks)
            block_address = (block_index * 16 * 8)

            result.append(data[block_address + (x - (block_x * 16)) + ((y - (block_y * 8)) * 16)])
    return result


def round_up(value, multiple):
    if (value % multiple) == 0:
        return value

    return value + (multiple - (value % multiple))


class KHMig(BrStruct):
    def __br_read__(self, br: BinaryReader) -> None:
        mig_end = None

        palette_data = image_data = None

        br.seek(0xC, Whence.CUR)
        while True:
            block_start = br.pos()

            block_id = KHMigBlockFlag(br.read_uint16(2)[0])
            block_size = br.read_uint32()
            next_block_rel_offset = br.read_uint32()
            block_data_offset = br.read_uint32()

            # Go to data start
            br.seek(block_start + block_data_offset, Whence.BEGIN)

            if block_id == KHMigBlockFlag.ROOT_BLOCK:
                mig_end = block_start + block_size
            elif block_id in (KHMigBlockFlag.IMAGE_BLOCK, KHMigBlockFlag.PALETTE_BLOCK):
                data_start = block_start + 0x10

                frame_start_rel_offset = br.read_uint16(2)[0]
                image_format = KHMigImageFormatFlag(br.read_uint16())
                pixel_order = br.read_uint16()

                width, height = br.read_uint16(2)
                _, width_align, height_align = br.read_uint16(3)

                pixels_per_row = width
                pixel_per_column = height

                if image_format == KHMigImageFormatFlag.RGBA8888:
                    bit_per_pixel = 32
                elif image_format == KHMigImageFormatFlag.INDEX4:
                    bit_per_pixel = 4
                elif image_format == KHMigImageFormatFlag.INDEX8:
                    bit_per_pixel = 8
                else:
                    raise Exception('Unsupported MIG image format')

                stride = int(ceil(float(width) * bit_per_pixel / 8))
                if stride % width_align != 0:
                    stride = round_up(stride, width_align)
                    pixels_per_row = stride * 8 // bit_per_pixel

                if pixel_per_column % height_align != 0:
                    pixel_per_column = round_up(pixel_per_column, height_align)

                br.seek(data_start + 0x1C, Whence.BEGIN)

                data_start_offset, data_end_offset = br.read_uint32(2)
                br.seek(data_start + data_start_offset, Whence.BEGIN)

                data = br.read_uint8(stride * pixel_per_column)

                if br.pos() != (data_start + data_end_offset):
                    raise Exception('Unexpected MIG offset')

                if pixel_order == 1:
                    data = unswizzle(data, stride, pixel_per_column)

                if block_id == KHMigBlockFlag.IMAGE_BLOCK:
                    if image_format == KHMigImageFormatFlag.RGBA8888:
                        image_data = data
                        self.width = width
                        self.height = height
                    elif image_format == KHMigImageFormatFlag.INDEX8:
                        image_data = data
                        self.width = width
                        self.height = height
                    elif image_format == KHMigImageFormatFlag.INDEX4:
                        image_data = list(chain(*map(lambda x: (x >> 4, x & 0xF), data)))
                        self.width = width
                        self.height = height
                else:
                    palette_data = data

            # Go to next block
            br.seek(block_start + next_block_rel_offset, Whence.BEGIN)

            # Root block should be the first block
            if mig_end is None:
                raise Exception('Could not find root block of MIG')

            if br.pos() >= mig_end:
                break

        # Seek to the end of the file to avoid breaking the ELPK page reading
        br.seek(mig_end, Whence.BEGIN)

        if palette_data:
            self.pixels = list(chain(*map(lambda i: palette_data[i * 4: (i + 1) * 4], image_data)))
        else:
            self.pixels = image_data
