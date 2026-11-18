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

//! The access to the payload, the user header and the flatbuffer builder that the samples,
//! requests and responses share, and the access to the values and keys of a blackboard.

use std::sync::Mutex;

use pyo3::exceptions::PyAttributeError;
use pyo3::prelude::*;
use pyo3::sync::PyOnceLock;
use pyo3::types::{PyByteArray, PyBytes, PyDict, PyModule};

use crate::python_types::{self, PayloadKind, ensure};
use crate::type_storage::TypeStorage;

static CTYPES: PyOnceLock<Py<PyModule>> = PyOnceLock::new();
static SLICE: PyOnceLock<Py<PyAny>> = PyOnceLock::new();
static FLATBUFFERS_BUILDER: PyOnceLock<Py<PyAny>> = PyOnceLock::new();
static BLACKBOARD_KEY: PyOnceLock<Py<PyAny>> = PyOnceLock::new();
static BLACKBOARD_VALUE: PyOnceLock<Py<PyAny>> = PyOnceLock::new();

fn ctypes(py: Python<'_>) -> PyResult<Bound<'_, PyModule>> {
    CTYPES
        .get_or_try_init(py, || py.import("ctypes").map(Bound::unbind))
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

/// Defines a Python object that is returned as it is but is annotated in the type stubs with
/// the given type hint instead of `Any`.
macro_rules! python_object_with_type_hint {
    ($(#[$doc:meta])* $name:ident = $type_hint:expr) => {
        $(#[$doc])*
        pub struct $name(pub(crate) Py<PyAny>);

        impl<'py> IntoPyObject<'py> for $name {
            type Target = PyAny;
            type Output = Bound<'py, PyAny>;
            type Error = std::convert::Infallible;

            #[cfg(feature = "experimental-inspect")]
            const OUTPUT_TYPE: pyo3::inspect::PyStaticExpr = $type_hint;

            fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
                Ok(self.0.into_bound(py))
            }
        }
    };
}

python_object_with_type_hint!(
    /// An `iceoryx2.Slice[ctypes.c_uint8]`.
    ByteSlice = pyo3::type_hint_subscript!(
        pyo3::type_hint_identifier!("iceoryx2.slice", "Slice"),
        pyo3::type_hint_identifier!("ctypes", "c_uint8")
    )
);

python_object_with_type_hint!(
    /// A `flatbuffers.Builder`.
    FlatbufferBuilder = pyo3::type_hint_identifier!("flatbuffers", "Builder")
);

python_object_with_type_hint!(
    /// An `iceoryx2.BlackboardValue`.
    BlackboardValue = pyo3::type_hint_identifier!("iceoryx2.blackboard_extensions", "BlackboardValue")
);

python_object_with_type_hint!(
    /// A `list[iceoryx2.BlackboardKey]`.
    BlackboardKeys = pyo3::type_hint_subscript!(
        pyo3::type_hint_identifier!("builtins", "list"),
        pyo3::type_hint_identifier!("iceoryx2.blackboard_extensions", "BlackboardKey")
    )
);

/// `ctypes.cast(address, ctypes.POINTER(target_type))`. When an `owner` is given, the pointer
/// keeps it alive, so that the memory it points to stays valid.
fn pointer<'py>(
    py: Python<'py>,
    address: usize,
    target_type: Option<&Py<PyAny>>,
    owner: Option<&Bound<'py, PyAny>>,
) -> PyResult<Bound<'py, PyAny>> {
    ensure(target_type.is_some(), "the type is not defined")?;
    let target_type = target_type.expect("checked above");
    let ctypes = ctypes(py)?;
    let pointer_type = ctypes.call_method1("POINTER", (target_type,))?;
    let pointer = ctypes.call_method1("cast", (address, pointer_type))?;
    if let Some(owner) = owner {
        pointer.setattr("_iox2_owner", owner)?;
    }
    Ok(pointer)
}

/// `iceoryx2.Slice(address, number_of_elements, element_type, owner=owner)`
fn slice<'py>(
    owner: &Bound<'py, PyAny>,
    address: usize,
    number_of_elements: usize,
    element_type: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let py = owner.py();
    let kwargs = PyDict::new(py);
    kwargs.set_item("owner", owner)?;
    attribute(py, &SLICE, "iceoryx2.slice", "Slice")?
        .call((address, number_of_elements, element_type), Some(&kwargs))
}

fn payload_kind<'py>(
    py: Python<'py>,
    payload_type: &TypeStorage,
) -> PyResult<Option<(PayloadKind, Bound<'py, PyAny>)>> {
    payload_type
        .value
        .as_ref()
        .map(|t| python_types::split_payload_type(t.bind(py)))
        .transpose()
}

/// The payload of `owner`: a `Slice` when the payload type is a `Slice`, otherwise a
/// `ctypes.POINTER` to the payload type. `slice_len` is `None` when `owner` does not provide
/// the number of elements of a `Slice` payload.
pub(crate) fn payload<'py>(
    owner: &Bound<'py, PyAny>,
    payload_type: &TypeStorage,
    payload_ptr: usize,
    slice_len: Option<usize>,
) -> PyResult<Py<PyAny>> {
    let py = owner.py();
    ensure(
        payload_type.value.is_some(),
        "the payload type is not defined",
    )?;
    if let Some((PayloadKind::Slice, element_type)) = payload_kind(py, payload_type)? {
        let Some(slice_len) = slice_len else {
            return Err(PyAttributeError::new_err(format!(
                "'{}' does not provide the length of a `Slice` payload",
                owner.get_type().name()?
            )));
        };
        return Ok(slice(owner, payload_ptr, slice_len, &element_type)?.unbind());
    }
    Ok(pointer(py, payload_ptr, payload_type.value.as_ref(), Some(owner))?.unbind())
}

/// A `ctypes.POINTER` to the user header of `owner`.
pub(crate) fn user_header(
    owner: &Bound<'_, PyAny>,
    user_header_type: &TypeStorage,
    user_header_ptr: usize,
) -> PyResult<Py<PyAny>> {
    Ok(pointer(
        owner.py(),
        user_header_ptr,
        user_header_type.value.as_ref(),
        Some(owner),
    )?
    .unbind())
}

fn ensure_flatbuffer<'py>(
    py: Python<'py>,
    payload_type: &TypeStorage,
) -> PyResult<Bound<'py, PyAny>> {
    match payload_kind(py, payload_type)? {
        Some((PayloadKind::Flatbuffer, flatbuffer_type)) => Ok(flatbuffer_type),
        _ => Err(pyo3::exceptions::PyAssertionError::new_err(
            "only available when the payload type is a `Flatbuffer`",
        )),
    }
}

/// The serialized flatbuffer of `owner` as `Slice` of bytes.
pub(crate) fn payload_bytes(
    owner: &Bound<'_, PyAny>,
    payload_type: &TypeStorage,
    payload_ptr: usize,
    number_of_elements: u64,
    payload_offset: u64,
) -> PyResult<ByteSlice> {
    let py = owner.py();
    ensure_flatbuffer(py, payload_type)?;
    let c_uint8 = ctypes(py)?.getattr("c_uint8")?;
    let offset = payload_offset as usize;
    Ok(ByteSlice(
        slice(
            owner,
            payload_ptr + offset,
            number_of_elements as usize - offset,
            &c_uint8,
        )?
        .unbind(),
    ))
}

/// The root object of the serialized flatbuffer of `owner`.
pub(crate) fn payload_root(
    owner: &Bound<'_, PyAny>,
    payload_type: &TypeStorage,
    payload_ptr: usize,
    number_of_elements: u64,
    payload_offset: u64,
) -> PyResult<Py<PyAny>> {
    let py = owner.py();
    let flatbuffer_type = ensure_flatbuffer(py, payload_type)?;
    let bytes = payload_bytes(
        owner,
        payload_type,
        payload_ptr,
        number_of_elements,
        payload_offset,
    )?;
    let view = bytes.0.bind(py).call_method0("as_memory_view")?;
    // the serialized flatbuffer starts with the little-endian `uoffset` of its root object
    let offset = payload_offset as usize;
    ensure(
        number_of_elements as usize >= offset + 4,
        "the flatbuffer is shorter than its root offset",
    )?;
    // SAFETY: the 4 bytes are part of the payload of `owner`, as checked above
    let root_offset =
        u32::from_le_bytes(unsafe { ((payload_ptr + offset) as *const [u8; 4]).read_unaligned() });
    let root = flatbuffer_type.call0()?;
    root.call_method1("Init", (view, root_offset))?;
    Ok(root.unbind())
}

/// The `flatbuffers.Builder` of an uninitialized payload. It is created on first access and
/// released when the payload is initialized or dropped.
#[derive(Default)]
pub(crate) struct FlatbufferBuilderCell(Mutex<Option<Py<PyAny>>>);

impl FlatbufferBuilderCell {
    /// Returns the builder, creating it with an initial size of `available_payload_memory`.
    pub(crate) fn get_or_create(
        &self,
        py: Python<'_>,
        available_payload_memory: impl FnOnce() -> usize,
    ) -> PyResult<FlatbufferBuilder> {
        let mut builder = self.0.lock().expect("the builder lock is never poisoned");
        if let Some(builder) = &*builder {
            return Ok(FlatbufferBuilder(builder.clone_ref(py)));
        }
        let created = attribute(py, &FLATBUFFERS_BUILDER, "flatbuffers", "Builder")?
            .call1((available_payload_memory(),))?
            .unbind();
        *builder = Some(created.clone_ref(py));
        Ok(FlatbufferBuilder(created))
    }

    fn take(&self) -> Option<Py<PyAny>> {
        self.0
            .lock()
            .expect("the builder lock is never poisoned")
            .take()
    }
}

/// Initializes an uninitialized payload. A `Flatbuffer` payload requires the `root` of the
/// flatbuffer that was created with the builder of `builder`, all other payloads must not
/// provide one.
///
/// * `assume_init` - labels the payload as initialized
/// * `assume_init_flatbuffer` - copies the serialized flatbuffer `(buffer_ptr, buffer_len,
///   payload_offset)` into the payload and labels it as initialized
pub(crate) fn assume_init<T>(
    py: Python<'_>,
    payload_type: &TypeStorage,
    builder: &FlatbufferBuilderCell,
    available_payload_memory: impl FnOnce() -> usize,
    root: Option<&Bound<'_, PyAny>>,
    assume_init: impl FnOnce() -> T,
    assume_init_flatbuffer: impl FnOnce(usize, usize, usize) -> PyResult<T>,
) -> PyResult<T> {
    let is_flatbuffer = matches!(
        payload_kind(py, payload_type)?,
        Some((PayloadKind::Flatbuffer, _))
    );
    ensure(
        is_flatbuffer == root.is_some(),
        "a `Flatbuffer` payload requires the root of the flatbuffer, all other payloads none",
    )?;
    let Some(root) = root else {
        return Ok(assume_init());
    };

    let flatbuffer_builder = builder.get_or_create(py, available_payload_memory)?;
    let flatbuffer_builder = flatbuffer_builder.0.bind(py);
    flatbuffer_builder.call_method1("Finish", (root,))?;
    let payload_offset: usize = flatbuffer_builder.call_method0("Head")?.extract()?;
    let buffer = flatbuffer_builder.getattr("Bytes")?;
    let buffer = buffer.cast::<PyByteArray>()?;
    // the buffer is only read while the GIL is held and no Python code runs, so it cannot be
    // resized or released in between
    let initialized = assume_init_flatbuffer(buffer.data() as usize, buffer.len(), payload_offset)?;
    builder.take();
    Ok(initialized)
}

/// An `iceoryx2.BlackboardValue` with a copy of the `value_size` bytes at `value_ptr`.
pub(crate) fn blackboard_value(
    py: Python<'_>,
    value_ptr: usize,
    value_type: Option<&Py<PyAny>>,
    generation_counter: u64,
) -> PyResult<BlackboardValue> {
    ensure(value_type.is_some(), "the value type is not defined")?;
    let value_size = python_types::sizeof(value_type.expect("checked above").bind(py))?;
    let data = copy_bytes(py, value_ptr, value_size);
    Ok(BlackboardValue(
        attribute(
            py,
            &BLACKBOARD_VALUE,
            "iceoryx2.blackboard_extensions",
            "BlackboardValue",
        )?
        .call1((data, generation_counter))?
        .unbind(),
    ))
}

/// The `iceoryx2.BlackboardKey`s with a copy of the bytes of each key at `key_ptrs`.
pub(crate) fn blackboard_keys(
    py: Python<'_>,
    key_ptrs: &[usize],
    key_type: Option<&Py<PyAny>>,
) -> PyResult<BlackboardKeys> {
    ensure(key_type.is_some(), "the key type is not defined")?;
    let key_size = python_types::sizeof(key_type.expect("checked above").bind(py))?;
    let blackboard_key = attribute(
        py,
        &BLACKBOARD_KEY,
        "iceoryx2.blackboard_extensions",
        "BlackboardKey",
    )?;
    let keys = key_ptrs
        .iter()
        .map(|key_ptr| blackboard_key.call1((copy_bytes(py, *key_ptr, key_size),)))
        .collect::<PyResult<Vec<_>>>()?;
    Ok(BlackboardKeys(
        pyo3::types::PyList::new(py, keys)?.into_any().unbind(),
    ))
}

/// A `ctypes.POINTER` to the value that is written in place, without keeping an owner alive.
pub(crate) fn value_pointer(
    py: Python<'_>,
    value_ptr: usize,
    value_type: Option<&Py<PyAny>>,
) -> PyResult<Py<PyAny>> {
    Ok(pointer(py, value_ptr, value_type, None)?.unbind())
}

fn copy_bytes(py: Python<'_>, address: usize, size: usize) -> Bound<'_, PyBytes> {
    // SAFETY: `address` points to `size` readable bytes of a blackboard key or value
    PyBytes::new(py, unsafe {
        core::slice::from_raw_parts(address as *const u8, size)
    })
}
