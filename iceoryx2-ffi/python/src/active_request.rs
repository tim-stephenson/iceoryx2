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
use iceoryx2::service::marker::{CustomHeaderMarker, CustomPayloadMarker};
use iceoryx2_log::fatal_panic;
use pyo3::prelude::*;

use crate::{
    error::LoanError,
    parc::Parc,
    request_header::RequestHeader,
    response_mut_uninit::{ResponseMutUninit, ResponseMutUninitType},
    type_storage::TypeStorage,
    unique_client_id::UniqueClientId,
};

type IpcActiveRequest = iceoryx2::active_request::ActiveRequest<
    crate::IpcService,
    [CustomPayloadMarker],
    CustomHeaderMarker,
    [CustomPayloadMarker],
    CustomHeaderMarker,
>;
type LocalActiveRequest = iceoryx2::active_request::ActiveRequest<
    crate::LocalService,
    [CustomPayloadMarker],
    CustomHeaderMarker,
    [CustomPayloadMarker],
    CustomHeaderMarker,
>;

pub(crate) enum ActiveRequestType {
    Ipc(Option<IpcActiveRequest>),
    Local(Option<LocalActiveRequest>),
}

#[pyclass]
/// The `ActiveRequest` represents the object that contains the payload that the `Client` sends to the
/// `Server`.
pub struct ActiveRequest {
    pub(crate) value: Parc<ActiveRequestType>,
    pub(crate) request_payload_type_details: TypeStorage,
    pub(crate) response_payload_type_details: TypeStorage,
    pub(crate) request_header_type_details: TypeStorage,
    pub(crate) response_header_type_details: TypeStorage,
}

#[pymethods]
impl ActiveRequest {
    #[getter]
    /// Returns `True` until the `PendingResponse` goes out of scope on the `Client`'s side
    /// indicating that the `Client` no longer receives the `ResponseMut`.
    pub fn is_connected(&self) -> bool {
        match &*self.value.lock() {
            ActiveRequestType::Ipc(Some(v)) => v.is_connected(),
            ActiveRequestType::Local(Some(v)) => v.is_connected(),
            _ => fatal_panic!(from "ActiveRequest::is_connected()",
                    "Accessing a released active request"),
        }
    }

    #[getter]
    /// Returns the address of the payload of the received `RequestMut` as an `int`.
    /// `ActiveRequest.payload` provides typed access.
    pub fn payload_ptr(&self) -> usize {
        match &*self.value.lock() {
            ActiveRequestType::Ipc(Some(v)) => v.payload().as_ptr() as usize,
            ActiveRequestType::Local(Some(v)) => v.payload().as_ptr() as usize,
            _ => fatal_panic!(from "ActiveRequest::payload_ptr()",
                    "Accessing a released active request"),
        }
    }

    #[getter]
    /// Returns the address of the user_header of the received `RequestMut` as an `int`.
    /// `ActiveRequest.user_header` provides typed access.
    pub fn user_header_ptr(&self) -> usize {
        match &*self.value.lock() {
            ActiveRequestType::Ipc(Some(v)) => {
                (v.user_header() as *const CustomHeaderMarker) as usize
            }
            ActiveRequestType::Local(Some(v)) => {
                (v.user_header() as *const CustomHeaderMarker) as usize
            }
            _ => fatal_panic!(from "ActiveRequest::user_header_ptr()",
                    "Accessing a released active request"),
        }
    }

    #[getter]
    /// Returns the `RequestHeader` of the received `RequestMut`
    pub fn header(&self) -> RequestHeader {
        match &*self.value.lock() {
            ActiveRequestType::Ipc(Some(v)) => RequestHeader(*v.header()),
            ActiveRequestType::Local(Some(v)) => RequestHeader(*v.header()),
            _ => fatal_panic!(from "ActiveRequest::header()",
                    "Accessing a released active request"),
        }
    }

    #[getter]
    /// Returns the `UniqueClientId` of the `Client`
    pub fn origin(&self) -> UniqueClientId {
        match &*self.value.lock() {
            ActiveRequestType::Ipc(Some(v)) => UniqueClientId(v.origin()),
            ActiveRequestType::Local(Some(v)) => UniqueClientId(v.origin()),
            _ => fatal_panic!(from "ActiveRequest::origin()",
                    "Accessing a released active request"),
        }
    }

    #[getter]
    /// Returns `True` if the `Client` wants to gracefully disconnect.
    /// This allows the `Server` to send its last response and then
    /// drop the `ActiveRequest` to signal the `Client` that no more
    /// `ResponseMut` will be sent.
    pub fn has_disconnect_hint(&self) -> bool {
        match &*self.value.lock() {
            ActiveRequestType::Ipc(Some(v)) => v.has_disconnect_hint(),
            ActiveRequestType::Local(Some(v)) => v.has_disconnect_hint(),
            _ => fatal_panic!(from "ActiveRequest::has_requested_graceful_disconnect()",
                    "Accessing a released active request"),
        }
    }

    /// Releases the `ActiveRequest` and terminates the connection.
    ///
    /// After this call the `ActiveRequest` is no longer usable!
    pub fn delete(&mut self) {
        match &mut *self.value.lock() {
            ActiveRequestType::Ipc(v) => {
                v.take();
            }
            ActiveRequestType::Local(v) => {
                v.take();
            }
        }
    }

    /// Loans/allocates memory from the underlying data segment.
    ///
    /// The user has to initialize the payload before it can be sent. On failure it returns
    /// `LoanError` describing the failure.
    pub fn loan_uninit(&self) -> PyResult<ResponseMutUninit> {
        ensure(
            self.response_payload_type_details.kind == PayloadKind::FixedSize,
            "`loan_uninit()` is not available for `Slice` or `Flatbuffer` payloads",
        )?;
        self.loan_slice_uninit_unchecked(1)
    }

    /// Loans/allocates memory from the underlying data segment.
    ///
    /// The user has to initialize the payload before it can be sent.
    /// Fails when it is called for data types which are not a slice.
    /// On failure it returns `LoanError` describing the failure.
    pub fn loan_slice_uninit(&self, number_of_elements: usize) -> PyResult<ResponseMutUninit> {
        ensure(
            self.response_payload_type_details.kind == PayloadKind::Slice,
            "`loan_slice_uninit()` requires a `Slice` payload",
        )?;
        self.loan_slice_uninit_unchecked(number_of_elements)
    }

    /// Loans/allocates a `ResponseMutUninit` from the underlying data segment of the `Server` with
    /// an integrated flatbuffer builder.
    pub fn loan_flatbuffer(&self) -> PyResult<ResponseMutUninit> {
        ensure(
            self.response_payload_type_details.kind == PayloadKind::Flatbuffer,
            "`loan_flatbuffer()` requires a `Flatbuffer` payload",
        )?;
        // Loaning a slice of 1 byte is exactly what we need here. The flatbuffer builder is
        // in python not zero-copy and completely resides on the heap since they do not have
        // an API to provide a custom allocator.
        //
        // When the data production is finished the payload is grown/resized and the
        // serialized flatbuffer content is copied into it.
        self.loan_slice_uninit_unchecked(1)
    }

    /// Sends a copy of the provided value.
    pub fn send_copy(&self, t: &Bound<'_, PyAny>) -> PyResult<()> {
        ensure(
            self.response_payload_type_details.kind != PayloadKind::Flatbuffer,
            "`send_copy()` is not available for `Flatbuffer` payloads",
        )?;
        let uninit = self.loan_slice_uninit_unchecked(1)?;
        python_types::copy_value(
            t,
            self.response_payload_type_details.value.as_ref(),
            uninit.payload_ptr(),
        )?;
        uninit.__assume_init().send()
    }

    /// Returns the payload of the request.
    ///
    /// It is a `Slice` when the payload type is a `Slice`, otherwise a `ctypes.POINTER` to the
    /// payload type.
    pub fn payload(slf: &Bound<'_, Self>) -> PyResult<Py<PyAny>> {
        let this = slf.borrow();
        payload_access::payload(
            slf.as_any(),
            &this.request_payload_type_details,
            this.payload_ptr(),
            Some(this.__slice_len()),
        )
    }

    /// Returns a `ctypes.POINTER` to the request header.
    pub fn user_header(slf: &Bound<'_, Self>) -> PyResult<Py<PyAny>> {
        let this = slf.borrow();
        payload_access::user_header(
            slf.as_any(),
            &this.request_header_type_details,
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
            &this.request_payload_type_details,
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
            &this.request_payload_type_details,
            this.payload_ptr(),
            header.number_of_elements(),
            header.payload_offset(),
        )
    }
}

// Helpers of the Python-side methods that are no longer part of the Python API.
impl ActiveRequest {
    /// Loans/allocates a `ResponseMutUninit` from the underlying data segment of the
    /// `Server`. The user has to initialize the payload before it can be sent.
    ///
    /// On failure it emits `LoanError` describing the failure.
    pub(crate) fn loan_slice_uninit_unchecked(
        &self,
        slice_len: usize,
    ) -> PyResult<ResponseMutUninit> {
        match &*self.value.lock() {
            ActiveRequestType::Ipc(Some(v)) => Ok(ResponseMutUninit {
                value: Parc::new(ResponseMutUninitType::Ipc(Some(unsafe {
                    v.loan_custom_payload(slice_len)
                        .map_err(|e| LoanError::new_err(format!("{e:?}")))?
                }))),
                response_header_type_details: self.response_header_type_details.clone(),
                response_payload_type_details: self.response_payload_type_details.clone(),
                builder: Default::default(),
            }),
            ActiveRequestType::Local(Some(v)) => Ok(ResponseMutUninit {
                value: Parc::new(ResponseMutUninitType::Local(Some(unsafe {
                    v.loan_custom_payload(slice_len)
                        .map_err(|e| LoanError::new_err(format!("{e:?}")))?
                }))),
                response_header_type_details: self.response_header_type_details.clone(),
                response_payload_type_details: self.response_payload_type_details.clone(),
                builder: Default::default(),
            }),
            _ => fatal_panic!(from "ActiveRequest::loan_slice_uninit()",
                    "Accessing a released active request"),
        }
    }

    pub fn __slice_len(&self) -> usize {
        match &*self.value.lock() {
            ActiveRequestType::Ipc(Some(v)) => v.payload().len(),
            ActiveRequestType::Local(Some(v)) => v.payload().len(),
            _ => fatal_panic!(from "RequestMutUninit::__slice_len()",
                "Accessing a released request."),
        }
    }
}
