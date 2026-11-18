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

"""Pins how the values and keys of a blackboard are accessed."""

# The tests cover the types that are returned, the bytes they contain and how
# a value is written in place.

import ctypes
from typing import Any

import iceoryx2 as iox2
import pytest

service_types = [iox2.ServiceType.Ipc, iox2.ServiceType.Local]


class Key(ctypes.Structure):
    _fields_ = [("a", ctypes.c_uint32), ("b", ctypes.c_uint16)]

    def __eq__(self, other: object) -> bool:
        """Compares the fields, which a blackboard key requires."""
        return isinstance(other, Key) and self.a == other.a and self.b == other.b


class Value(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int32), ("y", ctypes.c_double)]


def create_service(
    service_type: iox2.ServiceType, key_type: Any, entries: list
) -> tuple[Any, Any]:
    """Returns the node and the blackboard service with the given entries."""
    config = iox2.testing.generate_isolated_config()
    node = iox2.NodeBuilder.new().config(config).create(service_type)
    creator = node.service_builder(
        iox2.testing.generate_service_name()
    ).blackboard_creator(key_type)
    for key, value in entries:
        creator = creator.add(key, value)
    return node, creator.create()


@pytest.mark.parametrize("service_type", service_types)
@pytest.mark.parametrize(
    "value",
    [ctypes.c_uint64(0xFEDCBA9876543210), ctypes.c_int8(-3), Value(x=-7, y=2.5)],
)
def test_get_returns_a_copy_of_the_value_bytes(
    service_type: iox2.ServiceType, value: Any
) -> None:
    key = ctypes.c_uint64(1)
    _node, service = create_service(service_type, ctypes.c_uint64, [(key, value)])
    reader = service.reader_builder().create()

    result = reader.entry(key, type(value)).get()

    assert isinstance(result, iox2.BlackboardValue)
    assert isinstance(result.data, bytes)
    assert result.data == bytes(value)
    assert result.size == ctypes.sizeof(value)
    assert bytes(result.decode_as(type(value))) == bytes(value)


@pytest.mark.parametrize("service_type", service_types)
def test_get_returns_a_snapshot_that_does_not_change_with_updates(
    service_type: iox2.ServiceType,
) -> None:
    key = ctypes.c_uint64(1)
    _node, service = create_service(
        service_type, ctypes.c_uint64, [(key, ctypes.c_uint64(1))]
    )
    reader = service.reader_builder().create()
    writer = service.writer_builder().create()
    entry_handle = reader.entry(key, ctypes.c_uint64)

    before = entry_handle.get()
    writer.entry(key, ctypes.c_uint64).update_with_copy(ctypes.c_uint64(2))
    after = entry_handle.get()

    assert before.decode_as(ctypes.c_uint64).value == 1
    assert after.decode_as(ctypes.c_uint64).value == 2
    assert entry_handle.is_up_to_date(after)
    assert not entry_handle.is_up_to_date(before)


@pytest.mark.parametrize("service_type", service_types)
@pytest.mark.parametrize(
    "key_type, keys",
    [
        (ctypes.c_uint64, [ctypes.c_uint64(3), ctypes.c_uint64(1 << 40)]),
        (Key, [Key(a=1, b=2), Key(a=0xFFFFFFFF, b=0xFFFF)]),
    ],
)
def test_list_keys_returns_copies_of_all_key_bytes(
    service_type: iox2.ServiceType, key_type: Any, keys: list
) -> None:
    _node, service = create_service(
        service_type, key_type, [(key, ctypes.c_uint8(0)) for key in keys]
    )

    result = service.list_keys()

    assert isinstance(result, list)
    assert all(isinstance(key, iox2.BlackboardKey) for key in result)
    assert all(isinstance(key.data, bytes) for key in result)
    assert all(len(key.data) == ctypes.sizeof(key_type) for key in result)
    assert sorted(key.data for key in result) == sorted(bytes(key) for key in keys)


@pytest.mark.parametrize("service_type", service_types)
def test_value_mut_points_to_the_value_that_is_published_on_update(
    service_type: iox2.ServiceType,
) -> None:
    key = ctypes.c_uint64(1)
    _node, service = create_service(
        service_type, ctypes.c_uint64, [(key, Value(x=0, y=0))]
    )
    reader = service.reader_builder().create()
    writer = service.writer_builder().create()
    entry_value_uninit = writer.entry(key, Value).loan_uninit()

    value = entry_value_uninit.value_mut()
    assert isinstance(value, ctypes.POINTER(Value))
    value.contents.x = 42
    value.contents.y = 4.5
    entry_value_uninit.assume_init_and_update()

    result = reader.entry(key, Value).get().decode_as(Value)
    assert (result.x, result.y) == (42, 4.5)
