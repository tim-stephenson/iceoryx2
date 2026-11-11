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

import ast
import inspect
from pathlib import Path
from types import ModuleType

import iceoryx2 as iox2
from iceoryx2 import _iceoryx2

EXTENSION_MODULES = [
    iox2.publish_subscribe_extensions,
    iox2.request_response_extensions,
    iox2.blackboard_extensions,
]


def extended_classes(module: ModuleType) -> dict[str, list[str]]:
    """Returns the classes decorated with `@extends` in `module` and the names of their members."""
    tree = ast.parse(Path(inspect.getfile(module)).read_text(encoding="utf-8"))
    classes = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and any(
            isinstance(d, ast.Name) and d.id == "extends" for d in node.decorator_list
        ):
            classes[node.name] = [
                target.id
                for stmt in node.body
                if isinstance(stmt, ast.Assign)
                for target in stmt.targets
                if isinstance(target, ast.Name)
            ]
    return classes


def test_extended_classes_are_exported_and_are_the_rust_classes() -> None:
    for module in EXTENSION_MODULES:
        for name in extended_classes(module):
            assert name in module.__all__
            assert getattr(iox2, name) is getattr(_iceoryx2, name)


def test_extended_classes_have_their_python_side_members_attached() -> None:
    for module in EXTENSION_MODULES:
        for name, members in extended_classes(module).items():
            rust_class = getattr(_iceoryx2, name)

            assert members, f"'{name}' has no Python-side members"
            for member in members:
                assert member in vars(rust_class), f"'{name}.{member}' is not attached"
