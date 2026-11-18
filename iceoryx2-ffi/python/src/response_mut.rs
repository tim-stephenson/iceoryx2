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
use iceoryx2::service::marker::{CustomHeaderMarker, CustomPayloadMarker};
use iceoryx2_log::fatal_panic;
use pyo3::prelude::*;

use crate::{
    error::SendError, parc::Parc, response_header::ResponseHeader, type_storage::TypeStorage,
};

type IpcResponseMut = iceoryx2::response_mut::ResponseMut<
    crate::IpcService,
    [CustomPayloadMarker],
    CustomHeaderMarker,
>;
type LocalResponseMut = iceoryx2::response_mut::ResponseMut<
    crate::LocalService,
    [CustomPayloadMarker],
    CustomHeaderMarker,
>;

pub(crate) enum ResponseMutType {
    Ipc(Option<IpcResponseMut>),
    Local(Option<LocalResponseMut>),
}

#[pyclass]
pub struct ResponseMut {
    pub(crate) value: Parc<ResponseMutType>,
    pub(crate) response_payload_type_details: TypeStorage,
    pub(crate) response_header_type_details: TypeStorage,
}

#[pymethods]
impl ResponseMut {
    #[getter]
    /// Returns a reference to the `ResponseHeader`.
    pub fn header(&self) -> ResponseHeader {
        match &*self.value.lock() {
            ResponseMutType::Ipc(Some(v)) => ResponseHeader(*v.header()),
            ResponseMutType::Local(Some(v)) => ResponseHeader(*v.header()),
            _ => fatal_panic!(from "ResponseMut::header()",
                    "Accessing a released response mut."),
        }
    }

    #[getter]
    /// Returns the address of the user header of the response as an `int`.
    /// `ResponseMut.user_header` provides typed access.
    pub fn user_header_ptr(&self) -> usize {
        match &mut *self.value.lock() {
            ResponseMutType::Ipc(Some(v)) => {
                (v.user_header_mut() as *mut CustomHeaderMarker) as usize
            }
            ResponseMutType::Local(Some(v)) => {
                (v.user_header_mut() as *mut CustomHeaderMarker) as usize
            }
            _ => fatal_panic!(from "ResponseMut::user_header_ptr()",
                    "Accessing a released response mut."),
        }
    }

    #[getter]
    /// Returns the address of the payload of the response as an `int`.
    /// `ResponseMut.payload` provides typed access.
    pub fn payload_ptr(&self) -> usize {
        match &mut *self.value.lock() {
            ResponseMutType::Ipc(Some(v)) => v.payload_mut().as_mut_ptr() as usize,
            ResponseMutType::Local(Some(v)) => v.payload_mut().as_mut_ptr() as usize,
            _ => fatal_panic!(from "ResponseMut::payload_ptr()",
                    "Accessing a released response mut."),
        }
    }

    /// Releases the `ResponseMut`.
    ///
    /// After this call the `ResponseMut` is no longer usable!
    pub fn delete(&mut self) {
        match &mut *self.value.lock() {
            ResponseMutType::Ipc(v) => {
                v.take();
            }
            ResponseMutType::Local(v) => {
                v.take();
            }
        }
    }

    /// Sends a `ResponseMut` to the corresponding `PendingResponse` of the
    /// `Client`.
    pub fn send(&self) -> PyResult<()> {
        match &mut *self.value.lock() {
            ResponseMutType::Ipc(v) => {
                let response = v.take().unwrap();
                Ok(response
                    .send()
                    .map_err(|e| SendError::new_err(format!("{e:?}")))?)
            }
            ResponseMutType::Local(v) => {
                let response = v.take().unwrap();
                Ok(response
                    .send()
                    .map_err(|e| SendError::new_err(format!("{e:?}")))?)
            }
        }
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
            Some(this.header().number_of_elements()),
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

    /// Returns the serialized flatbuffer data as bytes.
    ///
    /// Only available when the payload type is a `Flatbuffer`.
    pub fn payload_bytes(slf: &Bound<'_, Self>) -> PyResult<payload_access::ByteSlice> {
        let this = slf.borrow();
        let header = this.header();
        payload_access::payload_bytes(
            slf.as_any(),
            &this.response_payload_type_details,
            this.payload_ptr(),
            header.number_of_elements(),
            header.payload_offset(),
        )
    }

    /// Returns the root of the flatbuffer.
    ///
    /// Only available when the payload type is a `Flatbuffer`.
    pub fn payload_root(slf: &Bound<'_, Self>) -> PyResult<Py<PyAny>> {
        let this = slf.borrow();
        let header = this.header();
        payload_access::payload_root(
            slf.as_any(),
            &this.response_payload_type_details,
            this.payload_ptr(),
            header.number_of_elements(),
            header.payload_offset(),
        )
    }
}
