from enum import IntFlag


class FlagEnum(IntFlag):
    def __contains__(self, other) -> bool:
        if isinstance(other, (int, IntFlag)):
            return (self & other) == other

        return super().__contains__(other)

    def __len__(self) -> int:
        return len([x for x in bin(self) if x == '1'])


class KHMateMaterialFlag(FlagEnum):
    IS_TEXTURE = 0x0405


class KHMigBlockFlag(FlagEnum):
    ROOT_BLOCK = 0x02
    PICTURE_BLOCK = 0x03
    IMAGE_BLOCK = 0x04
    PALETTE_BLOCK = 0x05
    INFO_BLOCK = 0xFF


# https://www.psdevwiki.com/ps3/Graphic_Image_Map_(GIM)
class KHMigImageFormatFlag(FlagEnum):
    RGBA5650 = 0x00
    RGBA5551 = 0x01
    RGBA4444 = 0x02
    RGBA8888 = 0x03
    INDEX4 = 0x04
    INDEX8 = 0x05
    INDEX16 = 0x06
    INDEX32 = 0x07
    DXT1 = 0x08
    DXT3 = 0x09
    DXT5 = 0x0A
    DXT1EXT = 0x0108
    DXT3EXT = 0x0109
    DXT5EXT = 0x010A


class KHModeNodeFlag(FlagEnum):
    SKINNED = 0x08
    CLONE = 0x04
    UNSKINNED = 0x03


class KHModeModelFlag(FlagEnum):
    IS_DUALFACE = 0x40
    HAS_ALPHA_BLACK_UNK = 0x20
    HAS_ALPHA_BLACK = 0x13  # == HAS_ALPHA & 0x10
    HAS_ALPHA_BLEND = 0x0B  # == HAS_ALPHA & 0x08
    HAS_ALPHA = 0x03


class KHModeVertexFlag(FlagEnum):
    HAS_4_WEIGHTS = 0x10000
    HAS_2_WEIGHTS = 0x8000
    HAS_1_WEIGHT = 0x4000

    HAS_WEIGHTS = 0x0400
    HAS_UV_SHORT = 0x0200
    HAS_LOCATION = 0x0180
    HAS_NORMAL = 0x40

    HAS_COLOR_UNK = 0x18
    HAS_COLOR_RGBA = 0x1F
    HAS_UV_FLOAT = 0x03


class KHPoseFlag(FlagEnum):
    SHORT_FLOATS = 0x8000
    CAMERA = 0x0003
    POSE = 0x0001


class KHPoseChannelFlag(FlagEnum):
    SCALE_X = CAMERA_ROLL = 0x0100
    SCALE_Y = CAMERA_FOV = 0x80
    SCALE_Z = CAMERA_UNK = 0x40    # This might not actually be used for camera

    # Focus point for camera, otherwise rotation
    ROTATION_X = FOCUS_X = 0x20
    ROTATION_Y = FOCUS_Y = 0x10
    ROTATION_Z = FOCUS_Z = 0x08
    LOCATION_X = 0x04
    LOCATION_Y = 0x02
    LOCATION_Z = 0x01
