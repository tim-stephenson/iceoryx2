// Copyright (c) 2025 Contributors to the Eclipse Foundation
//
// See the NOTICE file(s) distributed with this work for additional
// information regarding copyright ownership.
//
// This program and the accompanying materials are made available under the
// terms of the Apache Software License 2.0 which is available at
// https://www.apache.org/licenses/LICENSE-2.0, or the MIT license
// which is available at https://opensource.org/licenses/MIT.
//
// SPDX-License-Identifier: Apache-2.0 OR MIT

use pyo3::prelude::*;

use crate::python_types::PayloadKind;

#[pyclass(from_py_object)]
pub struct TypeStorage {
    pub value: Option<Py<PyAny>>,
    /// How a payload of this type is transmitted. Only meaningful for payload types.
    pub kind: PayloadKind,
}

impl Default for TypeStorage {
    fn default() -> Self {
        Self::new()
    }
}

impl Clone for TypeStorage {
    fn clone(&self) -> Self {
        Self {
            value: self
                .value
                .as_ref()
                .map(|v| Python::attach(|py| v.clone_ref(py))),
            kind: self.kind,
        }
    }
}

impl TypeStorage {
    pub fn new() -> Self {
        Self {
            value: None,
            kind: PayloadKind::FixedSize,
        }
    }

    pub fn with_kind(value: Py<PyAny>, kind: PayloadKind) -> Self {
        Self {
            value: Some(value),
            kind,
        }
    }
}
