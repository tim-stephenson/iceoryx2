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
    parc::Parc,
    response_header::ResponseHeader,
    response_mut::{ResponseMut, ResponseMutType},
    type_storage::TypeStorage,
};

type IpcResponseMutUninit = iceoryx2::response_mut_uninit::ResponseMutUninit<
    crate::IpcService,
    [MaybeUninit<CustomPayloadMarker>],
    CustomHeaderMarker,
>;
type LocalResponseMutUninit = iceoryx2::response_mut_uninit::ResponseMutUninit<
    crate::LocalService,
    [MaybeUninit<CustomPayloadMarker>],
    CustomHeaderMarker,
>;

pub(crate) enum ResponseMutUninitType {
    Ipc(Option<IpcResponseMutUninit>),
    Local(Option<LocalResponseMutUninit>),
}

#[pyclass]
/// Acquired by an `ActiveRequest` with
///  * `ActiveRequest.loan_uninit`,
///  * `ActiveRequest.loan_slice_uninit`,
///  * `ActiveRequest.loan_flatbuffer`
///
/// It stores the uninitialized payload of the response. It must be initialized and converted
/// into a `ResponseMut` with `ResponseMutUninit.write_payload` or
/// `ResponseMutUninit.assume_init` before it can be sent. Otherwise the loaned memory is
/// released when going out of scope.
pub struct ResponseMutUninit {
    pub(crate) value: Parc<ResponseMutUninitType>,
    pub(crate) response_payload_type_details: TypeStorage,
    pub(crate) response_header_type_details: TypeStorage,
    pub(crate) builder: payload_access::FlatbufferBuilderCell,
}

#[pymethods]
impl ResponseMutUninit {
    #[getter]
    /// Returns a reference to the `ResponseHeader`.
    pub fn header(&self) -> ResponseHeader {
        match &*self.value.lock() {
            ResponseMutUninitType::Ipc(Some(v)) => ResponseHeader(*v.header()),
            ResponseMutUninitType::Local(Some(v)) => ResponseHeader(*v.header()),
            _ => fatal_panic!(from "ResponseMutUninit::header()",
                    "Accessing a released response mut uninit."),
        }
    }

    #[getter]
    /// Returns the address of the user header of the response as an `int`.
    /// `ResponseMutUninit.user_header` provides typed access.
    pub fn user_header_ptr(&self) -> usize {
        match &mut *self.value.lock() {
            ResponseMutUninitType::Ipc(Some(v)) => {
                (v.user_header_mut() as *mut CustomHeaderMarker) as usize
            }
            ResponseMutUninitType::Local(Some(v)) => {
                (v.user_header_mut() as *mut CustomHeaderMarker) as usize
            }
            _ => fatal_panic!(from "ResponseMutUninit::user_header_ptr()",
                    "Accessing a released response mut uninit."),
        }
    }

    #[getter]
    /// Returns the address of the payload of the response as an `int`.
    /// `ResponseMutUninit.payload` provides typed access.
    pub fn payload_ptr(&self) -> usize {
        match &mut *self.value.lock() {
            ResponseMutUninitType::Ipc(Some(v)) => v.payload_mut().as_mut_ptr() as usize,
            ResponseMutUninitType::Local(Some(v)) => v.payload_mut().as_mut_ptr() as usize,
            _ => fatal_panic!(from "ResponseMutUninit::payload_ptr()",
                    "Accessing a released response mut uninit."),
        }
    }

    /// Releases the `ResponseMutUninit`.
    ///
    /// After this call the `ResponseMutUninit` is no longer usable!
    pub fn delete(&mut self) {
        match &mut *self.value.lock() {
            ResponseMutUninitType::Ipc(v) => {
                v.take();
            }
            ResponseMutUninitType::Local(v) => {
                v.take();
            }
        }
    }

    /// Writes the provided value into the response and returns the initialized `ResponseMut`.
    pub fn write_payload(&self, t: &Bound<'_, PyAny>) -> PyResult<ResponseMut> {
        ensure(
            self.response_payload_type_details.kind != PayloadKind::Flatbuffer,
            "`write_payload()` is not available for `Flatbuffer` payloads",
        )?;
        python_types::copy_value(
            t,
            self.response_payload_type_details.value.as_ref(),
            self.payload_ptr(),
        )?;
        Ok(self.__assume_init())
    }

    /// Returns the payload of the response.
    ///
    /// It is a `Slice` when the payload type is a `Slice`, otherwise a `ctypes.POINTER` to the
    /// payload type.
    pub fn payload(slf: &Bound<'_, Self>) -> PyResult<Py<PyAny>> {
        let this = slf.borrow();
        payload_access::payload(
            slf.as_any(),
            &this.response_payload_type_details,
            this.payload_ptr(),
            Some(this.__slice_len()),
        )
    }

    /// Returns a `ctypes.POINTER` to the response header.
    pub fn user_header(slf: &Bound<'_, Self>) -> PyResult<Py<PyAny>> {
        let this = slf.borrow();
        payload_access::user_header(
            slf.as_any(),
            &this.response_header_type_details,
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

    /// Extracts the value of the uninitialized payload and labels the `ResponseMutUninit` as initialized `ResponseMut`.
    ///
    /// After this call the `ResponseMutUninit` is no longer usable!
    #[pyo3(signature = (root = None))]
    pub fn assume_init(
        &self,
        py: Python<'_>,
        root: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<ResponseMut> {
        payload_access::assume_init(
            py,
            &self.response_payload_type_details,
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
impl ResponseMutUninit {
    pub fn __slice_len(&self) -> usize {
        match &*self.value.lock() {
            ResponseMutUninitType::Ipc(Some(v)) => v.payload().len(),
            ResponseMutUninitType::Local(Some(v)) => v.payload().len(),
            _ => fatal_panic!(from "ResponseMutUninit::__slice_len()",
                "Accessing a released response."),
        }
    }

    pub fn __available_payload_memory(&self) -> usize {
        match &*self.value.lock() {
            ResponseMutUninitType::Ipc(Some(v)) => v.__internal_available_payload_memory(),
            ResponseMutUninitType::Local(Some(v)) => v.__internal_available_payload_memory(),
            _ => fatal_panic!(from "ResponseMutUninit::__available_payload_memory()",
                              "Accessing a released response."),
        }
    }

    pub fn __assume_init_flatbuffer(
        &self,
        buffer_ptr: usize,
        buffer_len: usize,
        payload_offset: usize,
    ) -> PyResult<ResponseMut> {
        let payload_ptr = (buffer_ptr + payload_offset) as *const u8;
        let payload_len = buffer_len - payload_offset;
        match &mut *self.value.lock() {
            ResponseMutUninitType::Ipc(v) => {
                let mut response = v.take().unwrap();
                let mut memory_buffer = response.__internal_create_resizable_memory();
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

                response.__internal_finish_serialized(unsafe {
                    memory_buffer.as_ptr().add(payload_offset)
                });
                Ok(ResponseMut {
                    value: Parc::new(ResponseMutType::Ipc(Some(unsafe {
                        response.assume_init()
                    }))),
                    response_header_type_details: self.response_header_type_details.clone(),
                    response_payload_type_details: self.response_payload_type_details.clone(),
                })
            }
            ResponseMutUninitType::Local(v) => {
                let mut response = v.take().unwrap();
                let mut memory_buffer = response.__internal_create_resizable_memory();
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

                response.__internal_finish_serialized(unsafe {
                    memory_buffer.as_ptr().add(payload_offset)
                });
                Ok(ResponseMut {
                    value: Parc::new(ResponseMutType::Local(Some(unsafe {
                        response.assume_init()
                    }))),
                    response_header_type_details: self.response_header_type_details.clone(),
                    response_payload_type_details: self.response_payload_type_details.clone(),
                })
            }
        }
    }

    pub fn __assume_init(&self) -> ResponseMut {
        match &mut *self.value.lock() {
            ResponseMutUninitType::Ipc(v) => {
                let response = v.take().unwrap();
                ResponseMut {
                    value: Parc::new(ResponseMutType::Ipc(Some(unsafe {
                        response.assume_init()
                    }))),
                    response_header_type_details: self.response_header_type_details.clone(),
                    response_payload_type_details: self.response_payload_type_details.clone(),
                }
            }
            ResponseMutUninitType::Local(v) => {
                let response = v.take().unwrap();
                ResponseMut {
                    value: Parc::new(ResponseMutType::Local(Some(unsafe {
                        response.assume_init()
                    }))),
                    response_header_type_details: self.response_header_type_details.clone(),
                    response_payload_type_details: self.response_payload_type_details.clone(),
                }
            }
        }
    }
}
