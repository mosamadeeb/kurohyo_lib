from typing import List, Union
from mathutils import Vector

from ..util import BinaryReader


def hash_fnv0(string):
    max_size = 2**32
    prime = 0x811C9DC5

    result = 0
    for c in string:
        result = (result * prime) % max_size
        result ^= ord(c)

    return result


def read_short_float(br: BinaryReader, count=None):
    val = br.read_int16(count)
    return (val / 1023.0) if count is None else tuple(map(lambda x: x / 1023.0, val))


def write_short_float(br: BinaryReader, value):
    values = (
        int(value * 1023)
        if not br.is_iterable(value)
        else list(map(lambda val: int(val * 1023), value))
    )
    br.write_int16(values)


def read_short_float_vector(br: BinaryReader, count=None):
    if count is None:
        return Vector(read_short_float(br, 3))

    return tuple(map(Vector, [read_short_float(br, 3) for _ in range(count)]))


def write_short_float_vector(br: BinaryReader, value: Union[Vector, List[Vector]]):
    if br.is_iterable(value):
        for val in value:
            write_short_float(br, list(val.xyz))
    else:
        write_short_float(br, list(value.xyz))


def read_vector(br: BinaryReader, count=None):
    if count is None:
        return Vector(br.read_float(3))

    return tuple(map(Vector, [br.read_float(3) for _ in range(count)]))


def write_vector(br: BinaryReader, value: Union[Vector, List[Vector]]):
    if br.is_iterable(value):
        for val in value:
            br.write_float(list(val.xyz))
    else:
        br.write_float(list(value.xyz))
