from typing import List, Tuple

from mathutils import Vector, Euler

from ..util import BinaryReader, BrStruct
from .common import read_short_float, read_short_float_vector, read_vector, write_short_float, write_short_float_vector, write_vector
from .kh_enums import KHPoseChannelFlag, KHPoseFlag
from .khfile import KHFile, KHString


class KHPose(KHFile):
    name: str

    # Gets overridden when writing
    pose_flags: KHPoseFlag
    end_frame: float

    bones: List['KHPoseBone']

    def __br_read__(self, br: BinaryReader):
        self.name: str = br.read_struct(KHString).data

        self.pose_flags = KHPoseFlag(br.read_uint16())
        bone_count = br.read_uint16()

        data_size = br.read_uint32()
        self.end_frame = br.read_float()

        self.bones = br.read_struct(KHPoseBone, bone_count, self.pose_flags)

    def __br_write__(self, br: BinaryReader):
        br.write_struct(KHString(), self.name)

        # Setup flags
        # KHPoseFlag.SHORT_FLOATS is not used as it would require a different calculation for data_size
        self.pose_flags = KHPoseFlag.POSE
        if len(self.bones) == 1 and self.bones[0].is_camera():
            self.pose_flags |= KHPoseFlag.CAMERA

        br.write_uint16(self.pose_flags)
        br.write_uint16(len(self.bones))

        # Calculate end frame
        self.end_frame = 0
        for b in self.bones:
            for c in (b.camera_fov, b.camera_roll, *b.camera_focus, *b.scale, *b.rotation, *b.location):
                if c and c.keyframes:
                    self.end_frame = max(self.end_frame, c.keyframes[-1].frame)

        # Data size
        data_size_pos = br.pos()
        br.write_uint32(0)
        br.write_float(self.end_frame)

        br.write_struct(self.bones, self.pose_flags)

        # Size of data for allocation purposes
        # Equals size of all nodes without the KHString structs (length + string)
        # If KHPoseFlag.SHORT_FLOATS is used, then (possibly) each short float should count as a normal float (4 bytes)
        data_size = br.pos() - (data_size_pos + 8)

        for bone in self.bones:
            data_size -= 2 + len(bone.name)

        with br.seek_to(data_size_pos):
            br.write_uint32(data_size)


class KHPoseBone(BrStruct):
    name: str
    initial_scale: Vector
    initial_rotation: Euler
    initial_location: Vector

    # Gets overridden when writing
    channel_flags: KHPoseChannelFlag

    scale: List['KHPoseChannel']
    rotation: List['KHPoseChannel']
    location: List['KHPoseChannel']

    camera_roll: 'KHPoseChannel'
    camera_fov: 'KHPoseChannel'
    camera_focus: List['KHPoseChannel']

    def __init__(self):
        self.scale = [None] * 3
        self.rotation = [None] * 3
        self.location = [None] * 3

        self.camera_roll = None
        self.camera_fov = None
        self.camera_focus = [None] * 3

    def is_camera(self):
        return self.camera_roll or self.camera_fov or (self.camera_focus and any(self.camera_focus))

    def __br_read__(self, br: BinaryReader, pose_flags: KHPoseFlag):
        flags = br.read_uint16()
        self.name = br.read_struct(KHString).data

        read_vector_func = read_short_float_vector if KHPoseFlag.SHORT_FLOATS in pose_flags else read_vector

        # Rotation is euler in radians
        self.initial_scale = read_vector_func(br)
        self.initial_rotation = Euler(read_vector_func(br)[:])
        self.initial_location = read_vector_func(br)

        pose_bone_flags = br.read_uint32()
        self.channel_flags = KHPoseChannelFlag(br.read_uint16())

        channels = list(br.read_struct(KHPoseChannel, len(self.channel_flags), pose_flags))

        if KHPoseFlag.CAMERA in pose_flags:
            self.camera_roll = channels.pop(0) if KHPoseChannelFlag.CAMERA_ROLL in self.channel_flags else None
            self.camera_fov = channels.pop(0) if KHPoseChannelFlag.CAMERA_FOV in self.channel_flags else None

            # Might be unused, but let's check for it just in case
            camera_unk2 = channels.pop(0) if KHPoseChannelFlag.CAMERA_UNK in self.channel_flags else None

            for i, channel in enumerate((KHPoseChannelFlag.FOCUS_X, KHPoseChannelFlag.FOCUS_Y, KHPoseChannelFlag.FOCUS_Z)):
                self.camera_focus[i] = (channels.pop(0) if channel in self.channel_flags else None)
        else:
            for i, channel in enumerate((KHPoseChannelFlag.SCALE_X, KHPoseChannelFlag.SCALE_Y, KHPoseChannelFlag.SCALE_Z)):
                self.scale[i] = (channels.pop(0) if channel in self.channel_flags else None)

            for i, channel in enumerate((KHPoseChannelFlag.ROTATION_X, KHPoseChannelFlag.ROTATION_Y, KHPoseChannelFlag.ROTATION_Z)):
                self.rotation[i] = (channels.pop(0) if channel in self.channel_flags else None)

        for i, channel in enumerate((KHPoseChannelFlag.LOCATION_X, KHPoseChannelFlag.LOCATION_Y, KHPoseChannelFlag.LOCATION_Z)):
            self.location[i] = (channels.pop(0) if channel in self.channel_flags else None)

    def __br_write__(self, br: BinaryReader, pose_flags: KHPoseFlag):
        # flags
        br.write_uint16(0x0602)
        br.write_struct(KHString(), self.name)

        write_vector_func = write_short_float_vector if KHPoseFlag.SHORT_FLOATS in pose_flags else write_vector

        write_vector_func(br, self.initial_scale)
        write_vector_func(br, Vector(self.initial_rotation))
        write_vector_func(br, self.initial_location)

        channels = list()

        self.channel_flags = 0

        def add_channels(channel_list, channel_flags):
            for i, channel in enumerate(channel_list):
                if channel:
                    channels.append(channel)
                    self.channel_flags |= channel_flags[i]

        if KHPoseFlag.CAMERA in pose_flags:
            if self.camera_roll:
                channels.append(self.camera_roll)
                self.channel_flags |= KHPoseChannelFlag.CAMERA_ROLL
            if self.camera_fov:
                channels.append(self.camera_fov)
                self.channel_flags |= KHPoseChannelFlag.CAMERA_FOV

            # KHPoseChannelFlag.CAMERA_UNK should go here

            add_channels(self.camera_focus, (KHPoseChannelFlag.FOCUS_X,
                         KHPoseChannelFlag.FOCUS_Y, KHPoseChannelFlag.FOCUS_Z))
        else:
            add_channels(self.scale, (KHPoseChannelFlag.SCALE_X, KHPoseChannelFlag.SCALE_Y, KHPoseChannelFlag.SCALE_Z))
            add_channels(self.rotation, (KHPoseChannelFlag.ROTATION_X,
                         KHPoseChannelFlag.ROTATION_Y, KHPoseChannelFlag.ROTATION_Z))

        add_channels(self.location, (KHPoseChannelFlag.LOCATION_X,
                     KHPoseChannelFlag.LOCATION_Y, KHPoseChannelFlag.LOCATION_Z))

        br.write_uint32(2 if (self.channel_flags != 0) else 0)
        br.write_uint16(self.channel_flags)

        br.write_struct(channels, pose_flags)


class KHPoseChannel(BrStruct):
    keyframes: List['KHPoseKeyframe']

    def __init__(self):
        self.keyframes = list()

    def __br_read__(self, br: BinaryReader, pose_flags: KHPoseFlag):
        count = br.read_uint32()
        self.keyframes = list(br.read_struct(
            KHPoseKeyframeShort if KHPoseFlag.SHORT_FLOATS in pose_flags else KHPoseKeyframeFloat, count))

    def __br_write__(self, br: BinaryReader, pose_flags: KHPoseFlag):
        br.write_uint32(len(self.keyframes))
        for kf in self.keyframes:
            br.write_struct(KHPoseKeyframeShort(
                kf) if KHPoseFlag.SHORT_FLOATS in pose_flags else KHPoseKeyframeFloat(kf))


class KHPoseKeyframe(BrStruct):
    frame: float
    value: float

    def __init__(self, kf: 'KHPoseKeyframe' = None):
        if kf:
            self.frame = kf.frame
            self.value = kf.value


class KHPoseKeyframeShort(KHPoseKeyframe):
    def __br_read__(self, br: BinaryReader):
        self.value = read_short_float(br)
        self.frame = br.read_uint16()

    def __br_write__(self, br: BinaryReader):
        write_short_float(br, self.value)
        br.write_uint16(self.frame)


class KHPoseKeyframeFloat(KHPoseKeyframe):
    def __br_read__(self, br: BinaryReader):
        self.value, self.frame = br.read_float(2)

    def __br_write__(self, br: BinaryReader):
        br.write_float(self.value)
        br.write_float(self.frame)
