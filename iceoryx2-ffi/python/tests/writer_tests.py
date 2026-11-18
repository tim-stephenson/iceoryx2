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

from ctypes import c_int32, c_int64, c_uint8, c_uint32, c_uint64

import iceoryx2 as iox2
import pytest

service_types = [iox2.ServiceType.Ipc, iox2.ServiceType.Local]


@pytest.mark.parametrize("service_type", service_types)
def test_writer_id_from_same_port_is_equal(
    service_type: iox2.ServiceType,
) -> None:
    config = iox2.testing.generate_isolated_config()
    node = iox2.NodeBuilder.new().config(config).create(service_type)
    service_name = iox2.testing.generate_service_name()
    key = c_uint64(0)
    value = c_uint8(0)
    service = (
        node.service_builder(service_name)
        .blackboard_creator(c_uint64)
        .add(key, value)
        .create()
    )

    writer = service.writer_builder().create()
    writer_id = writer.id

    assert writer.id.value == writer_id.value


@pytest.mark.parametrize("service_type", service_types)
def test_handle_can_be_acquired_for_existing_key_value_pair(
    service_type: iox2.ServiceType,
) -> None:
    config = iox2.testing.generate_isolated_config()
    node = iox2.NodeBuilder.new().config(config).create(service_type)
    service_name = iox2.testing.generate_service_name()
    key = c_uint64(0)
    value = c_uint64(0)
    service = (
        node.service_builder(service_name)
        .blackboard_creator(c_uint64)
        .add(key, value)
        .create()
    )

    writer = service.writer_builder().create()
    try:
        writer.entry(key, c_uint64)

    except iox2.EntryHandleMutError:
        assert False


@pytest.mark.parametrize("service_type", service_types)
def test_handle_cannot_be_acquired_for_non_existing_key(
    service_type: iox2.ServiceType,
) -> None:
    config = iox2.testing.generate_isolated_config()
    node = iox2.NodeBuilder.new().config(config).create(service_type)
    service_name = iox2.testing.generate_service_name()
    key = c_uint64(0)
    value = c_uint64(0)
    service = (
        node.service_builder(service_name)
        .blackboard_creator(c_uint64)
        .add(key, value)
        .create()
    )

    writer = service.writer_builder().create()
    invalid_key = c_uint64(9)
    with pytest.raises(iox2.EntryHandleMutError):
        writer.entry(invalid_key, c_uint64)


@pytest.mark.parametrize("service_type", service_types)
def test_handle_cannot_be_acquired_for_wrong_value_type(
    service_type: iox2.ServiceType,
) -> None:
    config = iox2.testing.generate_isolated_config()
    node = iox2.NodeBuilder.new().config(config).create(service_type)
    service_name = iox2.testing.generate_service_name()
    key = c_uint64(0)
    value = c_uint64(0)
    service = (
        node.service_builder(service_name)
        .blackboard_creator(c_uint64)
        .add(key, value)
        .create()
    )

    writer = service.writer_builder().create()
    with pytest.raises(iox2.EntryHandleMutError):
        writer.entry(key, c_int64)


@pytest.mark.parametrize("service_type", service_types)
def test_entry_handle_mut_cannot_be_acquired_twice(
    service_type: iox2.ServiceType,
) -> None:
    config = iox2.testing.generate_isolated_config()
    node = iox2.NodeBuilder.new().config(config).create(service_type)
    service_name = iox2.testing.generate_service_name()
    key = c_uint64(0)
    value = c_uint64(0)
    service = (
        node.service_builder(service_name)
        .blackboard_creator(c_uint64)
        .add(key, value)
        .create()
    )

    writer = service.writer_builder().create()
    entry_handle_mut = writer.entry(key, c_uint64)
    with pytest.raises(iox2.EntryHandleMutError):
        writer.entry(key, c_uint64)

    entry_handle_mut.delete()
    try:
        writer.entry(key, c_uint64)
    except iox2.EntryHandleMutError:
        assert False


@pytest.mark.parametrize("service_type", service_types)
def test_entry_handle_mut_prevents_another_writer(
    service_type: iox2.ServiceType,
) -> None:
    config = iox2.testing.generate_isolated_config()
    node = iox2.NodeBuilder.new().config(config).create(service_type)
    service_name = iox2.testing.generate_service_name()
    key = c_uint8(0)
    value = c_int32(0)
    service = (
        node.service_builder(service_name)
        .blackboard_creator(c_uint8)
        .add(key, value)
        .create()
    )

    writer = service.writer_builder().create()
    _entry_handle_mut = writer.entry(key, c_int32)

    writer.delete()

    with pytest.raises(iox2.WriterCreateError):
        service.writer_builder().create()


@pytest.mark.parametrize("service_type", service_types)
def test_entry_value_can_still_be_used_after_every_previous_service_state_owner_was_dropped(
    service_type: iox2.ServiceType,
) -> None:
    config = iox2.testing.generate_isolated_config()
    node = iox2.NodeBuilder.new().config(config).create(service_type)
    service_name = iox2.testing.generate_service_name()
    key = c_uint64(0)
    value = c_uint32(0)
    service = (
        node.service_builder(service_name)
        .blackboard_creator(c_uint64)
        .add(key, value)
        .create()
    )

    writer = service.writer_builder().create()
    entry_handle_mut = writer.entry(key, c_uint32)
    entry_value_uninit = entry_handle_mut.loan_uninit()

    writer.delete()
    service.delete()

    entry_handle_mut = entry_value_uninit.update_with_copy(c_uint32(333))


@pytest.mark.parametrize("service_type", service_types)
def test_deleting_writer_removes_it_from_the_service(
    service_type: iox2.ServiceType,
) -> None:
    config = iox2.testing.generate_isolated_config()
    node = iox2.NodeBuilder.new().config(config).create(service_type)
    service_name = iox2.testing.generate_service_name()
    key = c_uint64(0)
    value = c_uint32(0)
    service = (
        node.service_builder(service_name)
        .blackboard_creator(c_uint64)
        .add(key, value)
        .create()
    )

    sut = service.writer_builder().create()

    with pytest.raises(iox2.WriterCreateError):
        sut = service.writer_builder().create()

    sut.delete()

    try:
        sut = service.writer_builder().create()
    except iox2.WriterCreateError:
        assert False


LAYOUT_MISMATCHES = [
    (c_uint8(1), "size"),
    ((c_uint8 * 8)(), "alignment"),
]


@pytest.mark.parametrize("service_type", service_types)
@pytest.mark.parametrize("key, reason", LAYOUT_MISMATCHES)
def test_handle_cannot_be_acquired_when_key_layout_does_not_match_key_type(
    service_type: iox2.ServiceType,
    key: c_uint8,
    reason: str,
) -> None:
    config = iox2.testing.generate_isolated_config()
    node = iox2.NodeBuilder.new().config(config).create(service_type)
    service_name = iox2.testing.generate_service_name()
    service = (
        node.service_builder(service_name)
        .blackboard_creator(c_uint64)
        .add(c_uint64(0), c_uint64(0))
        .create()
    )

    writer = service.writer_builder().create()

    with pytest.raises(AssertionError, match=reason):
        writer.entry(key, c_uint64)


@pytest.mark.parametrize("service_type", service_types)
@pytest.mark.parametrize("value, reason", LAYOUT_MISMATCHES)
def test_update_with_copy_fails_when_value_layout_does_not_match_value_type(
    service_type: iox2.ServiceType,
    value: c_uint8,
    reason: str,
) -> None:
    config = iox2.testing.generate_isolated_config()
    node = iox2.NodeBuilder.new().config(config).create(service_type)
    service_name = iox2.testing.generate_service_name()
    key = c_uint64(0)
    service = (
        node.service_builder(service_name)
        .blackboard_creator(c_uint64)
        .add(key, c_uint64(42))
        .create()
    )

    writer = service.writer_builder().create()
    reader = service.reader_builder().create()
    entry_handle_mut = writer.entry(key, c_uint64)

    with pytest.raises(AssertionError, match=reason):
        entry_handle_mut.update_with_copy(value)

    entry_value_uninit = entry_handle_mut.loan_uninit()

    with pytest.raises(AssertionError, match=reason):
        entry_value_uninit.update_with_copy(value)

    entry_handle = reader.entry(key, c_uint64)
    assert entry_handle.get().decode_as(c_uint64).value == 42
