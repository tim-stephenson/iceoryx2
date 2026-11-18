# Copyright (c) 2026 Contributors to the Eclipse Foundation
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

"""Pins how the payload, the user header and the flatbuffer builder are accessed."""

# The tests cover the samples, requests and responses: the types that are
# returned, the memory they refer to, how long they keep it alive and when
# they fail.

import ctypes
import gc
import tracemalloc
from typing import Any, Callable

# fmt: off
import flatbuffers
import iceoryx2 as iox2
import pytest
from flatbuffer_types.Helper import (create_bounded_data,
                                     create_unbounded_data, get_schema_file)
from Testing.BoundedData import BoundedData
from Testing.UnboundedData import UnboundedData

# fmt: on

PAYLOAD_VALUE = 7
HEADER_VALUE = 5
SLICE_LEN = 3
SLICE_ELEMENT = ctypes.c_uint8
FLATBUFFER_DATA = 123
RESERVED_MEMORY = 4096


class Payload(ctypes.Structure):
    _fields_ = [("value", ctypes.c_uint64)]


class Header(ctypes.Structure):
    _fields_ = [("value", ctypes.c_uint32)]


# creates the samples, requests and responses of one payload kind
class Objects:
    def __init__(
        self,
        kind: str,
        with_header: bool = True,
        max_borrowed_samples: int = 2,
        slice_element: type = SLICE_ELEMENT,
    ) -> None:
        """Creates the services and ports for the payload `kind`."""
        self.kind = kind
        self.slice_element = slice_element
        self.with_header = with_header
        config = iox2.testing.generate_isolated_config()
        self.node = iox2.NodeBuilder.new().config(config).create(iox2.ServiceType.Local)

        pubsub = self.node.service_builder(
            iox2.testing.generate_service_name()
        ).publish_subscribe(self._payload_type(UnboundedData))
        pubsub = pubsub.subscriber_max_borrowed_samples(
            max_borrowed_samples
        ).subscriber_max_buffer_size(4)
        rr = self.node.service_builder(
            iox2.testing.generate_service_name()
        ).request_response(
            self._payload_type(BoundedData), self._payload_type(UnboundedData)
        )
        if kind == "flatbuffer":
            pubsub = pubsub.flatbuffer_schema_path(
                get_schema_file("unbounded_data.bfbs")
            )
            rr = rr.request_flatbuffer_schema_path(
                get_schema_file("bounded_data.bfbs")
            ).response_flatbuffer_schema_path(get_schema_file("unbounded_data.bfbs"))
        if with_header:
            pubsub = pubsub.user_header(Header)
            rr = rr.request_header(Header).response_header(Header)
        self.pubsub = pubsub.create()
        self.rr = rr.create()

        publisher = self.pubsub.publisher_builder().max_loaned_samples(8)
        client = self.rr.client_builder()
        server = self.rr.server_builder()
        if kind == "slice":
            publisher = publisher.initial_max_slice_len(SLICE_LEN)
            client = client.initial_max_slice_len(SLICE_LEN)
            server = server.initial_max_slice_len(SLICE_LEN)
        if kind == "flatbuffer":
            publisher = publisher.initial_reserved_memory(RESERVED_MEMORY)
            client = client.initial_reserved_memory(RESERVED_MEMORY)
            server = server.initial_reserved_memory(RESERVED_MEMORY)
        self.publisher = publisher.create()
        self.subscriber = self.pubsub.subscriber_builder().create()
        self.client = client.create()
        self.server = server.create()

    def _payload_type(self, flatbuffer_type: type) -> Any:
        if self.kind == "slice":
            return iox2.Slice[self.slice_element]
        if self.kind == "flatbuffer":
            return iox2.Flatbuffer[flatbuffer_type]
        return Payload

    def _loan(self, port: Any) -> Any:
        if self.kind == "slice":
            return port.loan_slice_uninit(SLICE_LEN)
        if self.kind == "flatbuffer":
            return port.loan_flatbuffer()
        return port.loan_uninit()

    def _init(self, uninit: Any, create_data: Callable[[Any, int], int]) -> Any:
        if self.with_header:
            uninit.user_header().contents.value = HEADER_VALUE
        if self.kind == "slice":
            for i in range(SLICE_LEN):
                uninit.payload()[i] = PAYLOAD_VALUE + i
            return uninit.assume_init()
        if self.kind == "flatbuffer":
            root = create_data(uninit.flatbuffer_builder(), FLATBUFFER_DATA)
            return uninit.assume_init(root)
        uninit.payload().contents.value = PAYLOAD_VALUE
        return uninit.assume_init()

    def sample_mut_uninit(self) -> Any:
        return self._loan(self.publisher)

    def sample_mut(self) -> Any:
        return self._init(self.sample_mut_uninit(), create_unbounded_data)

    def sample(self) -> Any:
        self.sample_mut().send()
        return self.subscriber.receive()

    def request_mut_uninit(self) -> Any:
        return self._loan(self.client)

    def request_mut(self) -> Any:
        return self._init(self.request_mut_uninit(), create_bounded_data)

    def pending_response(self) -> Any:
        self._pending = self.request_mut().send()
        return self._pending

    def active_request(self) -> Any:
        self._pending = self.pending_response()
        return self.server.receive()

    def response_mut_uninit(self) -> Any:
        self._active = self.active_request()
        return self._loan(self._active)

    def response_mut(self) -> Any:
        return self._init(self.response_mut_uninit(), create_unbounded_data)

    def response(self) -> Any:
        self.response_mut().send()
        return self._pending.receive()


UNINITIALIZED = ["sample_mut_uninit", "request_mut_uninit", "response_mut_uninit"]
INITIALIZED = [
    "sample_mut",
    "sample",
    "request_mut",
    "pending_response",
    "active_request",
    "response_mut",
    "response",
]
ALL = UNINITIALIZED + INITIALIZED
# the flatbuffer type of the payload that `payload_root()` returns
ROOT_TYPE = {
    "sample_mut": UnboundedData,
    "sample": UnboundedData,
    "request_mut": BoundedData,
    "pending_response": BoundedData,
    "active_request": BoundedData,
    "response_mut": UnboundedData,
    "response": UnboundedData,
}
INITIALIZED_TYPE = {
    "sample_mut_uninit": "SampleMut",
    "request_mut_uninit": "RequestMut",
    "response_mut_uninit": "ResponseMut",
}


def root_value(root: Any) -> int:
    if isinstance(root, BoundedData):
        return root.Data()
    return root.Entries(0).Data1()


@pytest.mark.parametrize("name", ALL)
def test_payload_of_fixed_size_type_points_to_the_payload(name: str) -> None:
    objects = Objects("fixed_size")
    sut = getattr(objects, name)()

    payload = sut.payload()

    assert isinstance(payload, ctypes.POINTER(Payload))
    assert ctypes.addressof(payload.contents) == sut.payload_ptr
    if name in INITIALIZED:
        assert payload.contents.value == PAYLOAD_VALUE


@pytest.mark.parametrize("name", ALL)
def test_user_header_points_to_the_user_header(name: str) -> None:
    objects = Objects("fixed_size")
    sut = getattr(objects, name)()

    header = sut.user_header()

    assert isinstance(header, ctypes.POINTER(Header))
    assert ctypes.addressof(header.contents) == sut.user_header_ptr
    if name in INITIALIZED:
        assert header.contents.value == HEADER_VALUE


@pytest.mark.parametrize("name", ALL)
def test_user_header_fails_without_user_header_type(name: str) -> None:
    objects = Objects("fixed_size", with_header=False)
    sut = getattr(objects, name)()

    with pytest.raises(AssertionError):
        sut.user_header()


@pytest.mark.parametrize("name", ALL)
@pytest.mark.parametrize(
    "element_type", [ctypes.c_uint8, ctypes.c_uint32, ctypes.c_uint64]
)
def test_payload_of_slice_type_is_a_slice_over_the_payload_elements(
    name: str, element_type: Any
) -> None:
    objects = Objects("slice", slice_element=element_type)
    sut = getattr(objects, name)()

    payload = sut.payload()

    assert isinstance(payload, iox2.Slice)
    assert payload.contained_type is element_type
    assert payload.len() == SLICE_LEN
    assert payload.as_ptr() == sut.payload_ptr
    assert payload.as_memory_view().nbytes == SLICE_LEN * ctypes.sizeof(element_type)
    if name in INITIALIZED:
        assert [payload[i] for i in range(SLICE_LEN)] == [
            PAYLOAD_VALUE + i for i in range(SLICE_LEN)
        ]

    with pytest.raises(IndexError):
        _ = payload[SLICE_LEN]
    with pytest.raises(IndexError):
        payload[SLICE_LEN] = 0


@pytest.mark.parametrize("name", ALL)
def test_payload_fails_for_flatbuffer_type(name: str) -> None:
    objects = Objects("flatbuffer")
    sut = getattr(objects, name)()

    with pytest.raises(TypeError):
        sut.payload()


@pytest.mark.parametrize("name", INITIALIZED)
def test_payload_bytes_is_a_byte_slice_over_the_serialized_flatbuffer(
    name: str,
) -> None:
    objects = Objects("flatbuffer")
    sut = getattr(objects, name)()

    payload_bytes = sut.payload_bytes()

    offset = sut.header.payload_offset
    assert isinstance(payload_bytes, iox2.Slice)
    assert payload_bytes.contained_type is ctypes.c_uint8
    assert payload_bytes.as_ptr() == sut.payload_ptr + offset
    assert payload_bytes.len() == sut.header.number_of_elements - offset

    root = ROOT_TYPE[name].GetRootAs(bytes(payload_bytes.as_memory_view()), 0)
    assert root_value(root) == FLATBUFFER_DATA


@pytest.mark.parametrize("name", INITIALIZED)
def test_payload_root_is_the_root_of_the_flatbuffer(name: str) -> None:
    objects = Objects("flatbuffer")
    sut = getattr(objects, name)()

    root = sut.payload_root()

    assert isinstance(root, ROOT_TYPE[name])
    assert root_value(root) == FLATBUFFER_DATA


@pytest.mark.parametrize("name", INITIALIZED)
@pytest.mark.parametrize("kind", ["fixed_size", "slice"])
def test_flatbuffer_payload_access_fails_for_non_flatbuffer_type(
    name: str, kind: str
) -> None:
    objects = Objects(kind)
    sut = getattr(objects, name)()

    with pytest.raises(AssertionError):
        sut.payload_bytes()

    with pytest.raises(AssertionError):
        sut.payload_root()


@pytest.mark.parametrize("name", UNINITIALIZED)
def test_flatbuffer_payload_access_is_not_available_before_initialization(
    name: str,
) -> None:
    objects = Objects("flatbuffer")
    sut = getattr(objects, name)()

    assert not hasattr(sut, "payload_bytes")
    assert not hasattr(sut, "payload_root")


@pytest.mark.parametrize("name", UNINITIALIZED)
@pytest.mark.parametrize("kind", ["fixed_size", "flatbuffer"])
def test_flatbuffer_builder_is_created_once_per_uninitialized_payload(
    name: str, kind: str
) -> None:
    objects = Objects(kind)
    sut = getattr(objects, name)()
    other = getattr(objects, name)()

    builder = sut.flatbuffer_builder()

    assert isinstance(builder, flatbuffers.Builder)
    assert sut.flatbuffer_builder() is builder
    assert other.flatbuffer_builder() is not builder


@pytest.mark.parametrize("name", UNINITIALIZED)
@pytest.mark.parametrize("kind", ["fixed_size", "slice"])
def test_assume_init_without_root_initializes_non_flatbuffer_payload(
    name: str, kind: str
) -> None:
    objects = Objects(kind)
    sut = getattr(objects, name)()

    initialized = sut.assume_init()

    assert type(initialized).__name__ == INITIALIZED_TYPE[name]


@pytest.mark.parametrize("name", UNINITIALIZED)
@pytest.mark.parametrize("kind", ["fixed_size", "slice"])
def test_assume_init_with_root_fails_for_non_flatbuffer_type(
    name: str, kind: str
) -> None:
    objects = Objects(kind)
    sut = getattr(objects, name)()

    with pytest.raises(AssertionError):
        sut.assume_init(0)


@pytest.mark.parametrize("name", UNINITIALIZED)
def test_assume_init_without_root_fails_for_flatbuffer_type(name: str) -> None:
    objects = Objects("flatbuffer")
    sut = getattr(objects, name)()

    with pytest.raises(AssertionError):
        sut.assume_init()


@pytest.mark.parametrize("name", UNINITIALIZED)
def test_assume_init_with_root_serializes_the_flatbuffer(name: str) -> None:
    objects = Objects("flatbuffer")
    sut = getattr(objects, name)()
    create_data = (
        create_bounded_data if name == "request_mut_uninit" else create_unbounded_data
    )

    initialized = sut.assume_init(
        create_data(sut.flatbuffer_builder(), FLATBUFFER_DATA)
    )

    assert type(initialized).__name__ == INITIALIZED_TYPE[name]
    assert root_value(initialized.payload_root()) == FLATBUFFER_DATA


def traced_memory_growth(action: Callable[[], None], repetitions: int) -> int:
    gc.collect()
    tracemalloc.start()
    try:
        before = tracemalloc.get_traced_memory()[0]
        for _ in range(repetitions):
            action()
        gc.collect()
        return tracemalloc.get_traced_memory()[0] - before
    finally:
        tracemalloc.stop()


@pytest.mark.parametrize("name", UNINITIALIZED)
def test_flatbuffer_builder_is_released_with_its_uninitialized_payload(
    name: str,
) -> None:
    objects = Objects("flatbuffer")
    repetitions = 50

    def loan_build_and_drop() -> None:
        sut = getattr(objects, name)()
        sut.flatbuffer_builder()

    growth = traced_memory_growth(loan_build_and_drop, repetitions)

    # every builder reserves RESERVED_MEMORY bytes, so a retained builder per
    # loan would grow the memory by repetitions * RESERVED_MEMORY
    assert growth < repetitions * RESERVED_MEMORY // 2


@pytest.mark.parametrize("name", UNINITIALIZED)
def test_flatbuffer_builder_is_released_when_the_payload_is_initialized(
    name: str,
) -> None:
    objects = Objects("flatbuffer")
    repetitions = 50
    create_data = (
        create_bounded_data if name == "request_mut_uninit" else create_unbounded_data
    )

    def loan_build_and_initialize() -> None:
        sut = getattr(objects, name)()
        sut.assume_init(create_data(sut.flatbuffer_builder(), FLATBUFFER_DATA))

    growth = traced_memory_growth(loan_build_and_initialize, repetitions)

    assert growth < repetitions * RESERVED_MEMORY // 2


@pytest.mark.parametrize(
    "kind, accessor",
    [
        ("fixed_size", "payload"),
        ("fixed_size", "user_header"),
        ("slice", "payload"),
        ("flatbuffer", "payload_bytes"),
    ],
)
def test_accessed_payload_keeps_the_received_sample_borrowed(
    kind: str, accessor: str
) -> None:
    objects = Objects(kind, max_borrowed_samples=1)
    objects.sample_mut().send()
    objects.sample_mut().send()

    sample = objects.subscriber.receive()
    held = getattr(sample, accessor)()
    del sample
    gc.collect()

    with pytest.raises(Exception) as exc_info:
        objects.subscriber.receive()
    assert "ExceedsMaxBorrows" in str(exc_info.value)

    del held
    gc.collect()

    assert objects.subscriber.receive() is not None
