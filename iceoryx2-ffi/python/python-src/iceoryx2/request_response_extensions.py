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

"""Strong type safe extensions for the request-response messaging pattern."""

import ctypes
from typing import Any, get_args, get_origin, overload

import flatbuffers

from ._iceoryx2 import *
from .flatbuffer import Flatbuffer
from .slice import Slice

__all__: list[str] = []


def request_payload(self: Any) -> Any:
    """
    Returns the payload of the request.

    It is a `Slice` when the payload type is a `Slice`, otherwise a `ctypes.POINTER` to the
    payload type.
    """
    assert self.__request_payload_type_details is not None
    if get_origin(self.__request_payload_type_details) is Slice:
        (contained_type,) = get_args(self.__request_payload_type_details)
        return Slice(self.payload_ptr, self.__slice_len, contained_type, owner=self)

    ptr = ctypes.cast(
        self.payload_ptr, ctypes.POINTER(self.__request_payload_type_details)
    )
    ptr._iox2_owner = self
    return ptr


def response_payload(self: Any) -> Any:
    """
    Returns the payload of the response.

    It is a `Slice` when the payload type is a `Slice`, otherwise a `ctypes.POINTER` to the
    payload type.
    """
    assert self.__response_payload_type_details is not None
    if get_origin(self.__response_payload_type_details) is Slice:
        (contained_type,) = get_args(self.__response_payload_type_details)
        return Slice(self.payload_ptr, self.__slice_len, contained_type, owner=self)

    ptr = ctypes.cast(
        self.payload_ptr, ctypes.POINTER(self.__response_payload_type_details)
    )
    ptr._iox2_owner = self
    return ptr


def request_header(self: Any) -> Any:
    """Returns a `ctypes.POINTER` to the request header."""
    assert self.__request_header_type_details is not None
    ptr = ctypes.cast(
        self.user_header_ptr, ctypes.POINTER(self.__request_header_type_details)
    )
    ptr._iox2_owner = self
    return ptr


def response_header(self: Any) -> Any:
    """Returns a `ctypes.POINTER` to the response header."""
    assert self.__response_header_type_details is not None
    ptr = ctypes.cast(
        self.user_header_ptr,
        ctypes.POINTER(self.__response_header_type_details),
    )
    ptr._iox2_owner = self
    return ptr


def request_payload_bytes(self: Any) -> Slice[ctypes.c_uint8]:
    """
    Returns the serialized flatbuffer data as bytes.

    Only available when the payload type is a `Flatbuffer`.
    """
    assert self.__request_payload_type_details is not None
    assert get_origin(self.__request_payload_type_details) is Flatbuffer

    number_of_elements = self.header.number_of_elements
    offset = self.header.payload_offset
    return Slice(
        self.payload_ptr + offset,
        number_of_elements - offset,
        ctypes.c_uint8,
        owner=self,
    )


def response_payload_bytes(self: Any) -> Slice[ctypes.c_uint8]:
    """
    Returns the serialized flatbuffer data as bytes.

    Only available when the payload type is a `Flatbuffer`.
    """
    assert self.__response_payload_type_details is not None
    assert get_origin(self.__response_payload_type_details) is Flatbuffer

    number_of_elements = self.header.number_of_elements
    offset = self.header.payload_offset
    return Slice(
        self.payload_ptr + offset,
        number_of_elements - offset,
        ctypes.c_uint8,
        owner=self,
    )


def request_payload_root(self: Any) -> Any:
    """
    Returns the root of the flatbuffer.

    Only available when the payload type is a `Flatbuffer`.
    """
    assert self.__request_payload_type_details is not None
    assert get_origin(self.__request_payload_type_details) is Flatbuffer

    (PayloadType,) = get_args(self.__request_payload_type_details)

    payload_bytes = self.payload_bytes()
    view = payload_bytes.as_memory_view()
    n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, view, 0)

    data = PayloadType()
    data.Init(view, n)
    return data


def response_payload_root(self: Any) -> Any:
    """
    Returns the root of the flatbuffer.

    Only available when the payload type is a `Flatbuffer`.
    """
    assert self.__response_payload_type_details is not None
    assert get_origin(self.__response_payload_type_details) is Flatbuffer

    (PayloadType,) = get_args(self.__response_payload_type_details)

    payload_bytes = self.payload_bytes()
    view = payload_bytes.as_memory_view()
    n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, view, 0)

    data = PayloadType()
    data.Init(view, n)
    return data


_request_mut_uninit_dict: dict[int, flatbuffers.Builder] = {}


def flatbuffer_builder_request(self: RequestMutUninit) -> flatbuffers.Builder:
    """Returns the flatbuffer builder to produce the data that shall be sent."""
    key = id(self)
    builder = _request_mut_uninit_dict.get(key)
    if builder is None:
        builder = flatbuffers.Builder(self.__available_payload_memory)
        _request_mut_uninit_dict[key] = builder
    return builder


_response_mut_uninit_dict: dict[int, flatbuffers.Builder] = {}


def flatbuffer_builder_response(self: ResponseMutUninit) -> flatbuffers.Builder:
    """Returns the flatbuffer builder to produce the data that shall be sent."""
    key = id(self)
    builder = _response_mut_uninit_dict.get(key)
    if builder is None:
        builder = flatbuffers.Builder(self.__available_payload_memory)
        _response_mut_uninit_dict[key] = builder
    return builder


@overload
def assume_init_request(self: RequestMutUninit) -> RequestMut: ...  # noqa: E704
@overload
def assume_init_request(  # noqa: E704
    self: RequestMutUninit, root: int
) -> RequestMut: ...


def assume_init_request(self: RequestMutUninit, root=None) -> RequestMut:
    """
    Extracts the value of the uninitialized payload and labels the `RequestMutUninit` as initialized `RequestMut`.

    After this call the `RequestMutUninit` is no longer usable!
    """
    origin = get_origin(self.__request_payload_type_details)
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

    initialized_request = self.__assume_init_flatbuffer(
        buffer_ptr, buffer_len, payload_offset
    )
    _request_mut_uninit_dict.pop(id(self), None)
    return initialized_request


@overload
def assume_init_response(self: ResponseMutUninit) -> ResponseMut: ...  # noqa: E704
@overload
def assume_init_response(  # noqa: E704
    self: ResponseMutUninit, root: int
) -> ResponseMut: ...


def assume_init_response(self: ResponseMutUninit, root=None) -> ResponseMut:
    """
    Extracts the value of the uninitialized payload and labels the `ResponseMutUninit` as initialized `ResponseMut`.

    After this call the `ResponseMutUninit` is no longer usable!
    """
    origin = get_origin(self.__response_payload_type_details)
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

    initialized_response = self.__assume_init_flatbuffer(
        buffer_ptr, buffer_len, payload_offset
    )
    _response_mut_uninit_dict.pop(id(self), None)
    return initialized_response


_request_mut_uninit_del_original = getattr(RequestMutUninit, "__del__", None)


def _request_mut_uninit_del(self: RequestMutUninit) -> None:
    _request_mut_uninit_dict.pop(id(self), None)
    if _request_mut_uninit_del_original is not None:
        _request_mut_uninit_del_original(self)


_response_mut_uninit_del_original = getattr(ResponseMutUninit, "__del__", None)


def _response_mut_uninit_del(self: ResponseMutUninit) -> None:
    _response_mut_uninit_dict.pop(id(self), None)
    if _response_mut_uninit_del_original is not None:
        _response_mut_uninit_del_original(self)


ActiveRequest.payload = request_payload
ActiveRequest.user_header = request_header
ActiveRequest.payload_bytes = request_payload_bytes
ActiveRequest.payload_root = request_payload_root


PendingResponse.payload = request_payload
PendingResponse.user_header = request_header
PendingResponse.payload_bytes = request_payload_bytes
PendingResponse.payload_root = request_payload_root

RequestMut.payload = request_payload
RequestMut.user_header = request_header
RequestMut.payload_bytes = request_payload_bytes
RequestMut.payload_root = request_payload_root

RequestMutUninit.payload = request_payload
RequestMutUninit.user_header = request_header
RequestMutUninit.flatbuffer_builder = flatbuffer_builder_request
RequestMutUninit.assume_init = assume_init_request
RequestMutUninit.__del__ = _request_mut_uninit_del

Response.payload = response_payload
Response.user_header = response_header
Response.payload_bytes = response_payload_bytes
Response.payload_root = response_payload_root

ResponseMut.payload = response_payload
ResponseMut.user_header = response_header
ResponseMut.payload_bytes = response_payload_bytes
ResponseMut.payload_root = response_payload_root

ResponseMutUninit.payload = response_payload
ResponseMutUninit.user_header = response_header
ResponseMutUninit.flatbuffer_builder = flatbuffer_builder_response
ResponseMutUninit.assume_init = assume_init_response
ResponseMutUninit.__del__ = _response_mut_uninit_del
