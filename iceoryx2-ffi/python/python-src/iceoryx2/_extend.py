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

"""
Attaches Python-side methods to the classes implemented in Rust.

The classes of the `_iceoryx2` extension module cannot be subclassed at runtime, so
the extension modules write their additions as a class that, for type checkers only,
derives from the Rust class:

    if TYPE_CHECKING:
        from ._iceoryx2 import Publisher as _Publisher
    else:
        _Publisher = object

    @extends
    class Publisher(_Publisher):
        send_copy = send_copy

For type checkers and language servers `extends` is the identity, so `Publisher`
is the Rust class plus the Python-side methods. The Rust stubs refer to the
public `iceoryx2.Publisher` (see `src/public.rs`), so objects returned from Rust
have these methods as well. At runtime `extends` attaches the members to the
Rust class and returns it, so `iceoryx2.Publisher is iceoryx2._iceoryx2.Publisher`.
"""

from typing import TypeVar

from . import _iceoryx2

_C = TypeVar("_C", bound=type)

# special methods that are attached as well; all other dunders belong to the
# extension class itself (`__module__`, `__doc__`, `__dict__`, ...)
_ATTACHED_DUNDERS = frozenset({"__del__"})


def _is_attached(name: str) -> bool:
    is_dunder = name.startswith("__") and name.endswith("__")
    return not is_dunder or name in _ATTACHED_DUNDERS


def extends(extension: _C) -> _C:
    """Attaches the members of `extension` to the Rust class with the same name and returns it."""
    rust_class = getattr(_iceoryx2, extension.__name__)
    for name, member in vars(extension).items():
        if _is_attached(name):
            setattr(rust_class, name, member)
    return rust_class
