# Copyright (c) 2025 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache Software License 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0, or the MIT license
# which is available at https://opensource.org/licenses/MIT.
#
# SPDX-License-Identifier: Apache-2.0 OR MIT

"""Strong type safe extensions for the publish-subscribe messaging pattern."""

from __future__ import annotations

import ctypes
import typing
from typing import Any, get_args, get_origin, overload

import flatbuffers

from ._extend import extends
from ._iceoryx2 import *
from .flatbuffer import Flatbuffer
from .slice import Slice

# isort: off
if typing.TYPE_CHECKING:
    from ._iceoryx2 import Sample as _Sample
    from ._iceoryx2 import SampleMut as _SampleMut
    from ._iceoryx2 import SampleMutUninit as _SampleMutUninit
else:
    _Sample = object
    _SampleMut = object
    _SampleMutUninit = object
# isort: on

__all__ = [
    "Sample",
    "SampleMut",
    "SampleMutUninit",
]


def payload_bytes(self: Any) -> Slice[ctypes.c_uint8]:
    """
    Returns the serialized flatbuffer data as bytes.

    Only available when the payload type is a `Flatbuffer`.
    """
    assert self.__payload_type_details is not None
    assert get_origin(self.__payload_type_details) is Flatbuffer

    number_of_elements = self.header.number_of_elements
    offset = self.header.payload_offset
    return Slice(
        self.payload_ptr + offset,
        number_of_elements - offset,
        ctypes.c_uint8,
        owner=self,
    )


def payload_root(self: Any) -> Any:
    """
    Returns the root of the flatbuffer.

    Only available when the payload type is a `Flatbuffer`.
    """
    assert self.__payload_type_details is not None
    assert get_origin(self.__payload_type_details) is Flatbuffer

    (PayloadType,) = get_args(self.__payload_type_details)

    payload_bytes = self.payload_bytes()
    view = payload_bytes.as_memory_view()
    n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, view, 0)

    data = PayloadType()
    data.Init(view, n)
    return data


def payload(self: Any) -> Any:
    """
    Returns the payload.

    It is a `Slice` when the payload type is a `Slice`, otherwise a `ctypes.POINTER` to the
    payload type.
    """
    assert self.__payload_type_details is not None
    if get_origin(self.__payload_type_details) is Slice:
        (contained_type,) = get_args(self.__payload_type_details)
        return Slice(self.payload_ptr, self.__slice_len, contained_type, owner=self)

    ptr = ctypes.cast(self.payload_ptr, ctypes.POINTER(self.__payload_type_details))
    ptr._iox2_owner = self  # type: ignore[attr-defined]
    return ptr


def user_header(self: Any) -> Any:
    """Returns a `ctypes.POINTER` to the user header."""
    assert self.__user_header_type_details is not None
    ptr = ctypes.cast(
        self.user_header_ptr, ctypes.POINTER(self.__user_header_type_details)
    )
    ptr._iox2_owner = self  # type: ignore[attr-defined]
    return ptr


_sample_mut_uninit_dict: dict[int, flatbuffers.Builder] = {}


def flatbuffer_builder(self: SampleMutUninit) -> flatbuffers.Builder:
    """Returns the flatbuffer builder to produce the data that shall be sent."""
    key = id(self)
    builder = _sample_mut_uninit_dict.get(key)
    if builder is None:
        builder = flatbuffers.Builder(self.__available_payload_memory)
        _sample_mut_uninit_dict[key] = builder
    return builder


@overload
def assume_init(self: SampleMutUninit) -> SampleMut: ...  # noqa: E704


@overload
def assume_init(self: SampleMutUninit, root: int) -> SampleMut: ...  # noqa: E704


def assume_init(self: SampleMutUninit, root=None) -> SampleMut:
    """
    Extracts the value of the uninitialized payload and labels the `SampleMutUninit` as initialized `SampleMut`.

    After this call the `SampleMutUninit` is no longer usable.
    """
    origin = get_origin(self.__payload_type_details)
    assert (origin is Flatbuffer and root is not None) or (
        origin is not Flatbuffer and root is None
    )

    if root is None:
        return self.__assume_init()

    builder = self.flatbuffer_builder()
    builder.Finish(root)

    payload_offset = builder.Head()
    buffer_len = len(builder.Bytes)
    base_view = (ctypes.c_ubyte * buffer_len).from_buffer(builder.Bytes)
    buffer_ptr = ctypes.addressof(base_view)

    initialized_sample = self.__assume_init_flatbuffer(
        buffer_ptr, buffer_len, payload_offset
    )
    _sample_mut_uninit_dict.pop(id(self), None)
    return initialized_sample


_sample_mut_uninit_del_original = getattr(SampleMutUninit, "__del__", None)  # type: ignore[used-before-def]


def _sample_mut_uninit_del(self: SampleMutUninit) -> None:
    _sample_mut_uninit_dict.pop(id(self), None)
    if _sample_mut_uninit_del_original is not None:
        _sample_mut_uninit_del_original(self)


@extends
class Sample(_Sample):  # type: ignore[misc]
    """Python-side extension of the Rust `Sample`."""

    payload = payload
    user_header = user_header
    payload_bytes = payload_bytes
    payload_root = payload_root


@extends
class SampleMut(_SampleMut):  # type: ignore[misc]
    """Python-side extension of the Rust `SampleMut`."""

    payload = payload
    user_header = user_header
    payload_bytes = payload_bytes
    payload_root = payload_root


@extends
class SampleMutUninit(_SampleMutUninit):  # type: ignore[misc]
    """Python-side extension of the Rust `SampleMutUninit`."""

    payload = payload
    user_header = user_header
    flatbuffer_builder = flatbuffer_builder
    assume_init = assume_init
    __del__ = _sample_mut_uninit_del
