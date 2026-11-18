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

"""Strong type safe extensions for the blackboard messaging pattern."""

import ctypes
from typing import Any, Callable

__all__ = ["BlackboardKey", "BlackboardValue"]


def get_key_cmp_func(
    key_type_details: Any,
) -> Callable[[ctypes.c_uint64, ctypes.c_uint64], bool]:
    """Returns a callable for comparing keys."""

    def key_cmp(lhs: ctypes.c_uint64, rhs: ctypes.c_uint64) -> bool:
        lhs_key = ctypes.cast(lhs, ctypes.POINTER(key_type_details)).contents
        rhs_key = ctypes.cast(rhs, ctypes.POINTER(key_type_details)).contents
        if isinstance(lhs_key, ctypes.Structure):
            return lhs_key == rhs_key
        return lhs_key.value == rhs_key.value

    return key_cmp


class BlackboardKey:
    """A wrapper class for the keys returned by `PortFactoryBlackboard.list_keys()`."""

    def __init__(self, data: bytes):
        """Initializes `BlackboardKey` from bytes."""
        self.data = data

    def decode_as(self, ct_type):
        """Interpret the raw bytes as a ctypes type."""
        return ct_type.from_buffer_copy(self.data)


class BlackboardValue:
    """A wrapper class for the value returned by `EntryHandle.get()`."""

    def __init__(self, data: bytes, generation_counter: ctypes.c_uint64):
        """Initializes `BlackboardValue` from bytes."""
        self.data = data
        self.size = len(data)
        self._generation_counter = generation_counter

    def decode_as(self, ct_type):
        """Interpret the raw bytes as a ctypes type."""
        return ct_type.from_buffer_copy(self.data)
