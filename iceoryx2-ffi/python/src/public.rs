// Copyright (c) 2026 Contributors to the Eclipse Foundation
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
use pyo3::pyclass::PyClass;
use pyo3::pyclass_init::PyClassInitializer;

/// Return-type wrapper for classes that are extended on the Python side
/// (see `python-src/iceoryx2/*_extensions.py`).
///
/// At runtime it is converted exactly like `T`. In the generated type stubs
/// the return type is annotated as `iceoryx2.<T>` instead of the bare `<T>`
/// of the `_iceoryx2` stub, so that type checkers and language servers
/// resolve it to the public class including the Python-side methods.
pub struct Public<T>(pub T);

impl<'py, T> IntoPyObject<'py> for Public<T>
where
    T: PyClass + Into<PyClassInitializer<T>>,
{
    type Target = T;
    type Output = Bound<'py, T>;
    type Error = PyErr;

    #[cfg(feature = "experimental-inspect")]
    const OUTPUT_TYPE: pyo3::inspect::PyStaticExpr = pyo3::inspect::PyStaticExpr::Attribute {
        value: &pyo3::inspect::PyStaticExpr::Name { id: "iceoryx2" },
        attr: <T as PyClass>::NAME,
    };

    fn into_pyobject(self, py: Python<'py>) -> PyResult<Self::Output> {
        Bound::new(py, self.0)
    }
}
