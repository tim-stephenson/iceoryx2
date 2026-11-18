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

use crate::payload_access;
use crate::python_types::{self, PayloadKind, ensure};
use core::mem::MaybeUninit;

use iceoryx2::service::marker::{CustomHeaderMarker, CustomPayloadMarker};
use iceoryx2_log::fatal_panic;
use pyo3::prelude::*;

use crate::{
    error::AllocationGrowError,
    header_publish_subscribe::HeaderPublishSubscribe,
    parc::Parc,
    sample_mut::{SampleMut, SampleMutType},
    type_storage::TypeStorage,
};

pub(crate) enum SampleMutUninitType {
    Ipc(
        Option<
            iceoryx2::sample_mut_uninit::SampleMutUninit<
                crate::IpcService,
                [MaybeUninit<CustomPayloadMarker>],
                CustomHeaderMarker,
            >,
        >,
    ),
    Local(
        Option<
            iceoryx2::sample_mut_uninit::SampleMutUninit<
                crate::LocalService,
                [MaybeUninit<CustomPayloadMarker>],
                CustomHeaderMarker,
            >,
        >,
    ),
}

#[pyclass]
/// Acquired by a `Publisher` via
///  * `Publisher.loan_uninit`,
///  * `Publisher.loan_slice_uninit`,
///  * `Publisher.loan_flatbuffer`
///
/// It stores the uninitialized payload. It must be initialized and converted into a
/// `SampleMut` with `SampleMutUninit.write_payload` or `SampleMutUninit.assume_init`
/// before it can be sent. Otherwise the loaned memory is released when going out of scope.
pub struct SampleMutUninit {
    pub(crate) value: Parc<SampleMutUninitType>,
    pub(crate) payload_type_details: TypeStorage,
    pub(crate) user_header_type_details: TypeStorage,
    pub(crate) builder: payload_access::FlatbufferBuilderCell,
}

#[pymethods]
impl SampleMutUninit {
    #[getter]
    /// Returns the `HeaderPublishSubscribe` of the `Sample`.
    pub fn header(&self) -> HeaderPublishSubscribe {
        match &*self.value.lock() {
            SampleMutUninitType::Ipc(Some(v)) => HeaderPublishSubscribe(*v.header()),
            SampleMutUninitType::Local(Some(v)) => HeaderPublishSubscribe(*v.header()),
            _ => fatal_panic!(from "SampleMutUninit::header()",
                "Accessing a released sample."),
        }
    }

    #[getter]
    /// Returns the address of the user header as an `int`.
    /// `SampleMutUninit.user_header` provides typed access.
    pub fn user_header_ptr(&self) -> usize {
        match &mut *self.value.lock() {
            SampleMutUninitType::Ipc(Some(v)) => {
                (v.user_header_mut() as *mut CustomHeaderMarker) as usize
            }
            SampleMutUninitType::Local(Some(v)) => {
                (v.user_header_mut() as *mut CustomHeaderMarker) as usize
            }
            _ => fatal_panic!(from "SampleMutUninit::user_header_ptr()",
                "Accessing a released sample."),
        }
    }

    #[getter]
    /// Returns the address of the payload as an `int`.
    /// `SampleMutUninit.payload` provides typed access.
    pub fn payload_ptr(&self) -> usize {
        match &mut *self.value.lock() {
            SampleMutUninitType::Ipc(Some(v)) => (v.payload_mut().as_mut_ptr()) as usize,
            SampleMutUninitType::Local(Some(v)) => (v.payload_mut().as_mut_ptr()) as usize,
            _ => fatal_panic!(from "SampleMutUninit::payload_ptr()",
                "Accessing a released sample."),
        }
    }

    /// Releases the `SampleMutUninit`.
    ///
    /// After this call the `SampleMutUninit` is no longer usable!
    pub fn delete(&mut self) {
        match &mut *self.value.lock() {
            SampleMutUninitType::Ipc(v) => {
                v.take();
            }
            SampleMutUninitType::Local(v) => {
                v.take();
            }
        }
    }

    /// Shortens the payload to its first `number_of_elements` elements, so that only those are
    /// sent.
    ///
    /// It has no effect when `number_of_elements` is not smaller than the current number of
    /// elements. Fails when it is called for data types which are not a slice.
    pub fn truncate(&self, number_of_elements: usize) -> PyResult<()> {
        ensure(
            self.payload_type_details.kind == PayloadKind::Slice,
            "`truncate()` requires a `Slice` payload",
        )?;
        self.truncate_unchecked(number_of_elements);
        Ok(())
    }

    /// Writes the provided value into the sample and returns the initialized `SampleMut`.
    pub fn write_payload(&self, t: &Bound<'_, PyAny>) -> PyResult<SampleMut> {
        ensure(
            self.payload_type_details.kind != PayloadKind::Flatbuffer,
            "`write_payload()` is not available for `Flatbuffer` payloads",
        )?;
        python_types::copy_value(
            t,
            self.payload_type_details.value.as_ref(),
            self.payload_ptr(),
        )?;
        Ok(self.__assume_init())
    }

    /// Returns the payload.
    ///
    /// It is a `Slice` when the payload type is a `Slice`, otherwise a `ctypes.POINTER` to the
    /// payload type.
    pub fn payload(slf: &Bound<'_, Self>) -> PyResult<Py<PyAny>> {
        let this = slf.borrow();
        payload_access::payload(
            slf.as_any(),
            &this.payload_type_details,
            this.payload_ptr(),
            Some(this.__slice_len()),
        )
    }

    /// Returns a `ctypes.POINTER` to the user header.
    pub fn user_header(slf: &Bound<'_, Self>) -> PyResult<Py<PyAny>> {
        let this = slf.borrow();
        payload_access::user_header(
            slf.as_any(),
            &this.user_header_type_details,
            this.user_header_ptr(),
        )
    }

    /// Returns the flatbuffer builder to produce the data that shall be sent.
    pub fn flatbuffer_builder(
        &self,
        py: Python<'_>,
    ) -> PyResult<payload_access::FlatbufferBuilder> {
        self.builder
            .get_or_create(py, || self.__available_payload_memory())
    }

    /// Extracts the value of the uninitialized payload and labels the `SampleMutUninit` as initialized `SampleMut`.
    ///
    /// After this call the `SampleMutUninit` is no longer usable.
    #[pyo3(signature = (root = None))]
    pub fn assume_init(
        &self,
        py: Python<'_>,
        root: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<SampleMut> {
        payload_access::assume_init(
            py,
            &self.payload_type_details,
            &self.builder,
            || self.__available_payload_memory(),
            root,
            || self.__assume_init(),
            |buffer_ptr, buffer_len, payload_offset| {
                self.__assume_init_flatbuffer(buffer_ptr, buffer_len, payload_offset)
            },
        )
    }
}

// Helpers of the Python-side methods that are no longer part of the Python API.
impl SampleMutUninit {
    pub(crate) fn truncate_unchecked(&self, number_of_elements: usize) {
        match &mut *self.value.lock() {
            SampleMutUninitType::Ipc(Some(v)) => v.truncate(number_of_elements),
            SampleMutUninitType::Local(Some(v)) => v.truncate(number_of_elements),
            _ => fatal_panic!(from "SampleMutUninit::__truncate()",
                "Accessing a released sample."),
        }
    }

    pub fn __slice_len(&self) -> usize {
        match &*self.value.lock() {
            SampleMutUninitType::Ipc(Some(v)) => v.payload().len(),
            SampleMutUninitType::Local(Some(v)) => v.payload().len(),
            _ => fatal_panic!(from "Sample::__slice_len()",
                "Accessing a released sample."),
        }
    }

    pub fn __available_payload_memory(&self) -> usize {
        match &*self.value.lock() {
            SampleMutUninitType::Ipc(Some(v)) => v.__internal_available_payload_memory(),
            SampleMutUninitType::Local(Some(v)) => v.__internal_available_payload_memory(),
            _ => fatal_panic!(from "SampleMutUninit::__available_payload_memory()",
                "Accessing a released sample."),
        }
    }

    pub fn __assume_init_flatbuffer(
        &self,
        buffer_ptr: usize,
        buffer_len: usize,
        payload_offset: usize,
    ) -> PyResult<SampleMut> {
        let payload_ptr = (buffer_ptr + payload_offset) as *const u8;
        let payload_len = buffer_len - payload_offset;
        match &mut *self.value.lock() {
            SampleMutUninitType::Ipc(v) => {
                let mut sample = v.take().unwrap();
                let mut memory_buffer = sample.__internal_create_resizable_memory();
                if memory_buffer.len() < buffer_len {
                    memory_buffer
                        .grow_downwards_with_size(buffer_len, 0)
                        .map_err(|e| AllocationGrowError::new_err(format!("{e:?}")))?
                }
                unsafe {
                    core::ptr::copy(
                        payload_ptr,
                        memory_buffer.as_mut_ptr().add(payload_offset),
                        payload_len,
                    )
                };

                sample.__internal_finish_serialized(unsafe {
                    memory_buffer.as_ptr().add(payload_offset)
                });
                Ok(SampleMut {
                    value: Parc::new(SampleMutType::Ipc(Some(unsafe { sample.assume_init() }))),
                    payload_type_details: self.payload_type_details.clone(),
                    user_header_type_details: self.user_header_type_details.clone(),
                })
            }
            SampleMutUninitType::Local(v) => {
                let mut sample = v.take().unwrap();
                let mut memory_buffer = sample.__internal_create_resizable_memory();
                if memory_buffer.len() < buffer_len {
                    memory_buffer
                        .grow_downwards_with_size(buffer_len, 0)
                        .map_err(|e| AllocationGrowError::new_err(format!("{e:?}")))?
                }
                unsafe {
                    core::ptr::copy(
                        payload_ptr,
                        memory_buffer.as_mut_ptr().add(payload_offset),
                        payload_len,
                    )
                };

                sample.__internal_finish_serialized(unsafe {
                    memory_buffer.as_ptr().add(payload_offset)
                });
                Ok(SampleMut {
                    value: Parc::new(SampleMutType::Local(Some(unsafe { sample.assume_init() }))),
                    payload_type_details: self.payload_type_details.clone(),
                    user_header_type_details: self.user_header_type_details.clone(),
                })
            }
        }
    }

    pub fn __assume_init(&self) -> SampleMut {
        match &mut *self.value.lock() {
            SampleMutUninitType::Ipc(v) => {
                let sample = v.take().unwrap();
                SampleMut {
                    value: Parc::new(SampleMutType::Ipc(Some(unsafe { sample.assume_init() }))),
                    payload_type_details: self.payload_type_details.clone(),
                    user_header_type_details: self.user_header_type_details.clone(),
                }
            }
            SampleMutUninitType::Local(v) => {
                let sample = v.take().unwrap();
                SampleMut {
                    value: Parc::new(SampleMutType::Local(Some(unsafe { sample.assume_init() }))),
                    payload_type_details: self.payload_type_details.clone(),
                    user_header_type_details: self.user_header_type_details.clone(),
                }
            }
        }
    }
}
