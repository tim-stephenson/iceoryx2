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

//! Helpers to work with the Python types (`ctypes`, `Slice[T]`, `Flatbuffer[T]`)
//! that users provide as payload, header, key and value types.

use pyo3::exceptions::PyAssertionError;
use pyo3::prelude::*;
use pyo3::sync::PyOnceLock;
use pyo3::types::PyModule;

use crate::type_detail::TypeDetail;
use crate::type_name::TypeName;
use crate::type_variant::TypeVariant;

/// How a payload type is transmitted, derived from the Python type the user provided.
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub enum PayloadKind {
    /// A fixed size ctypes type.
    #[default]
    FixedSize,
    /// A `Slice[T]` of a ctypes type.
    Slice,
    /// A `Flatbuffer[T]` of a generated flatbuffer type.
    Flatbuffer,
}

static CTYPES: PyOnceLock<Py<PyModule>> = PyOnceLock::new();
static TYPING: PyOnceLock<Py<PyModule>> = PyOnceLock::new();
static SLICE: PyOnceLock<Py<PyAny>> = PyOnceLock::new();
static FLATBUFFER: PyOnceLock<Py<PyAny>> = PyOnceLock::new();
static GET_TYPE_NAME: PyOnceLock<Py<PyAny>> = PyOnceLock::new();
static GET_KEY_CMP_FUNC: PyOnceLock<Py<PyAny>> = PyOnceLock::new();

fn module<'py>(
    py: Python<'py>,
    cell: &'static PyOnceLock<Py<PyModule>>,
    name: &str,
) -> PyResult<Bound<'py, PyModule>> {
    cell.get_or_try_init(py, || py.import(name).map(Bound::unbind))
        .map(|m| m.bind(py).clone())
}

fn attribute<'py>(
    py: Python<'py>,
    cell: &'static PyOnceLock<Py<PyAny>>,
    module: &str,
    name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    cell.get_or_try_init(py, || py.import(module)?.getattr(name).map(Bound::unbind))
        .map(|a| a.bind(py).clone())
}

/// Raises an `AssertionError` with `message` when `condition` does not hold.
pub(crate) fn ensure(condition: bool, message: &str) -> PyResult<()> {
    if condition {
        Ok(())
    } else {
        Err(PyAssertionError::new_err(message.to_string()))
    }
}

/// `ctypes.sizeof(value)`
pub(crate) fn sizeof(value: &Bound<'_, PyAny>) -> PyResult<usize> {
    module(value.py(), &CTYPES, "ctypes")?
        .call_method1("sizeof", (value,))?
        .extract()
}

/// `ctypes.alignment(value)`
pub(crate) fn alignment(value: &Bound<'_, PyAny>) -> PyResult<usize> {
    module(value.py(), &CTYPES, "ctypes")?
        .call_method1("alignment", (value,))?
        .extract()
}

/// `ctypes.addressof(value)`
pub(crate) fn addressof(value: &Bound<'_, PyAny>) -> PyResult<usize> {
    module(value.py(), &CTYPES, "ctypes")?
        .call_method1("addressof", (value,))?
        .extract()
}

/// `iceoryx2.type_name.get_type_name(value)`
pub(crate) fn type_name(value: &Bound<'_, PyAny>) -> PyResult<String> {
    attribute(
        value.py(),
        &GET_TYPE_NAME,
        "iceoryx2.type_name",
        "get_type_name",
    )?
    .call1((value,))?
    .extract()
}

/// `iceoryx2.blackboard_extensions.get_key_cmp_func(key)`, the Python callable that compares
/// two keys of type `key` stored at the given addresses.
pub(crate) fn key_eq_cmp_func(key: &Bound<'_, PyAny>) -> PyResult<Py<PyAny>> {
    attribute(
        key.py(),
        &GET_KEY_CMP_FUNC,
        "iceoryx2.blackboard_extensions",
        "get_key_cmp_func",
    )?
    .call1((key,))
    .map(Bound::unbind)
}

/// Splits a payload type into its `PayloadKind` and the contained type, e.g.
/// `Slice[c_uint8]` into `(PayloadKind::Slice, c_uint8)`.
pub(crate) fn split_payload_type<'py>(
    value: &Bound<'py, PyAny>,
) -> PyResult<(PayloadKind, Bound<'py, PyAny>)> {
    let py = value.py();
    let typing = module(py, &TYPING, "typing")?;
    let origin = typing.call_method1("get_origin", (value,))?;
    let kind = if origin.is(&attribute(py, &SLICE, "iceoryx2.slice", "Slice")?) {
        PayloadKind::Slice
    } else if origin.is(&attribute(
        py,
        &FLATBUFFER,
        "iceoryx2.flatbuffer",
        "Flatbuffer",
    )?) {
        PayloadKind::Flatbuffer
    } else {
        return Ok((PayloadKind::FixedSize, value.clone()));
    };
    let (contained,): (Bound<'py, PyAny>,) =
        typing.call_method1("get_args", (value,))?.extract()?;
    Ok((kind, contained))
}

fn type_detail(
    variant: TypeVariant,
    name: &str,
    size: usize,
    alignment: usize,
) -> PyResult<TypeDetail> {
    Ok(TypeDetail::new()
        .type_variant(&variant)
        .type_name(&TypeName::new(name)?)
        .size(size)
        .alignment(alignment))
}

/// The `TypeDetail` of a fixed size ctypes type.
pub(crate) fn fixed_size_type_detail(value: &Bound<'_, PyAny>) -> PyResult<TypeDetail> {
    type_detail(
        TypeVariant::FixedSize,
        &type_name(value)?,
        sizeof(value)?,
        alignment(value)?,
    )
}

/// The `TypeDetail` of the unit type `()` that is used when no header is defined.
pub(crate) fn unit_type_detail() -> PyResult<TypeDetail> {
    type_detail(TypeVariant::FixedSize, "()", 0, 1)
}

/// The details of a payload type that are required to create a service.
pub(crate) struct PayloadTypeDetail {
    pub(crate) kind: PayloadKind,
    pub(crate) type_detail: TypeDetail,
    /// The type name of the flatbuffer type for `Flatbuffer[T]` payloads.
    pub(crate) flatbuffer_type_name: Option<String>,
}

/// The `PayloadTypeDetail` of a payload type, a ctypes type, `Slice[T]` or `Flatbuffer[T]`.
pub(crate) fn payload_type_detail(value: &Bound<'_, PyAny>) -> PyResult<PayloadTypeDetail> {
    let (kind, contained) = split_payload_type(value)?;
    Ok(match kind {
        PayloadKind::Flatbuffer => PayloadTypeDetail {
            kind,
            type_detail: type_detail(TypeVariant::FixedSize, "iox2::Flatbuffer", 1, 1)?,
            flatbuffer_type_name: Some(type_name(&contained)?),
        },
        PayloadKind::Slice => PayloadTypeDetail {
            kind,
            type_detail: type_detail(
                TypeVariant::Dynamic,
                &type_name(&contained)?,
                sizeof(&contained)?,
                alignment(&contained)?,
            )?,
            flatbuffer_type_name: None,
        },
        PayloadKind::FixedSize => PayloadTypeDetail {
            kind,
            type_detail: fixed_size_type_detail(value)?,
            flatbuffer_type_name: None,
        },
    })
}

/// Ensures that `value` has the size and alignment of `expected_type`.
pub(crate) fn ensure_layout(
    value: &Bound<'_, PyAny>,
    expected_type: Option<&Py<PyAny>>,
) -> PyResult<usize> {
    let expected_type = expected_type.map(|t| t.bind(value.py()));
    ensure(expected_type.is_some(), "the type is not defined")?;
    let expected_type = expected_type.expect("checked above");
    let size = sizeof(value)?;
    ensure(
        size == sizeof(expected_type)?,
        "the size does not match the type",
    )?;
    ensure(
        alignment(value)? == alignment(expected_type)?,
        "the alignment does not match the type",
    )?;
    Ok(size)
}

/// Copies the ctypes `value` to `destination` after ensuring that it has the size and
/// alignment of `expected_type`.
pub(crate) fn copy_value(
    value: &Bound<'_, PyAny>,
    expected_type: Option<&Py<PyAny>>,
    destination: usize,
) -> PyResult<()> {
    let size = ensure_layout(value, expected_type)?;
    copy_bytes(value, destination, size)
}

/// Copies the `size` bytes of the ctypes `value` to `destination`. The caller must have ensured
/// with `ensure_layout` that `destination` provides memory for `size` bytes.
pub(crate) fn copy_bytes(
    value: &Bound<'_, PyAny>,
    destination: usize,
    size: usize,
) -> PyResult<()> {
    let source = addressof(value)?;
    // SAFETY: `source` points to the `size` bytes of the ctypes `value` and `destination` to
    // memory for `size` bytes loaned from iceoryx2, so both are valid and cannot overlap.
    unsafe {
        core::ptr::copy_nonoverlapping(source as *const u8, destination as *mut u8, size);
    }
    Ok(())
}
