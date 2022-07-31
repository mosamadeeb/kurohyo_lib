from typing import List, Tuple

from mathutils import Euler

from ..util import BinaryReader, BrStruct
from .common import read_short_float, read_short_float_vector, read_vector
from .kh_enums import KHPoseChannelFlag, KHPoseFlag
from .khfile import KHFile, KHString


class KHPose(KHFile):
    bones: Tuple['KHPoseBone']

    def __br_read__(self, br: BinaryReader):
        self.name: str = br.read_struct(KHString).data

        self.pose_flags = KHPoseFlag(br.read_uint16())
        bone_count = br.read_uint16()

        data_size = br.read_uint32()
        self.end_frame = br.read_float()

        self.bones = br.read_struct(KHPoseBone, bone_count, self.pose_flags)


class KHPoseBone(BrStruct):
    def __br_read__(self, br: BinaryReader, pose_flags: KHPoseFlag):
        flags = br.read_uint16()
        self.name: str = br.read_struct(KHString).data

        read_vector_func = read_short_float_vector if KHPoseFlag.SHORT_FLOATS in pose_flags else read_vector

        # Rotation is euler in radians
        self.initial_scale = read_vector_func(br)
        self.initial_rotation = Euler(read_vector_func(br)[:])
        self.initial_location = read_vector_func(br)

        pose_bone_flags = br.read_uint32()
        self.channel_flags = KHPoseChannelFlag(br.read_uint16())

        channels = list(br.read_struct(KHPoseChannel, len(self.channel_flags), pose_flags))

        self.scale: List[KHPoseChannel] = list()
        self.rotation: List[KHPoseChannel] = list()
        self.location: List[KHPoseChannel] = list()

        self.camera_roll: KHPoseChannel
        self.camera_fov: KHPoseChannel
        self.camera_focus: List[KHPoseChannel] = list()

        if KHPoseFlag.CAMERA in pose_flags:
            self.camera_roll = channels.pop(0) if KHPoseChannelFlag.CAMERA_ROLL in self.channel_flags else None
            self.camera_fov = channels.pop(0) if KHPoseChannelFlag.CAMERA_FOV in self.channel_flags else None

            # Might be unused, but let's check for it just in case
            camera_unk2 = channels.pop(0) if KHPoseChannelFlag.CAMERA_UNK in self.channel_flags else None

            for channel in (KHPoseChannelFlag.FOCUS_X, KHPoseChannelFlag.FOCUS_Y, KHPoseChannelFlag.FOCUS_Z):
                self.camera_focus.append(channels.pop(0) if channel in self.channel_flags else None)
        else:
            for channel in (KHPoseChannelFlag.SCALE_X, KHPoseChannelFlag.SCALE_Y, KHPoseChannelFlag.SCALE_Z):
                self.scale.append(channels.pop(0) if channel in self.channel_flags else None)

            for channel in (KHPoseChannelFlag.ROTATION_X, KHPoseChannelFlag.ROTATION_Y, KHPoseChannelFlag.ROTATION_Z):
                self.rotation.append(channels.pop(0) if channel in self.channel_flags else None)

        for channel in (KHPoseChannelFlag.LOCATION_X, KHPoseChannelFlag.LOCATION_Y, KHPoseChannelFlag.LOCATION_Z):
            self.location.append(channels.pop(0) if channel in self.channel_flags else None)


class KHPoseChannel(BrStruct):
    keyframes: List['KHPoseKeyframe']

    def __br_read__(self, br: BinaryReader, pose_flags: KHPoseFlag):
        count = br.read_uint32()
        self.keyframes = list(br.read_struct(
            KHPoseKeyframeShort if KHPoseFlag.SHORT_FLOATS in pose_flags else KHPoseKeyframeFloat, count))


class KHPoseKeyframe(BrStruct):
    frame: float
    value: float


class KHPoseKeyframeShort(KHPoseKeyframe):
    def __br_read__(self, br: BinaryReader):
        self.value = read_short_float(br)
        self.frame = br.read_uint16()


class KHPoseKeyframeFloat(KHPoseKeyframe):
    def __br_read__(self, br: BinaryReader):
        self.value, self.frame = br.read_float(2)
