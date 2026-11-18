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

use crate::pending_response::PendingResponse;
use crate::python_types::{self, PayloadKind, ensure};
use iceoryx2::service::marker::{CustomHeaderMarker, CustomPayloadMarker};
use iceoryx2_log::fatal_panic;
use pyo3::prelude::*;

use crate::{
    backpressure_strategy::BackpressureStrategy,
    error::LoanError,
    parc::Parc,
    port_name::PortName,
    request_mut_uninit::{RequestMutUninit, RequestMutUninitType},
    type_storage::TypeStorage,
    unique_client_id::UniqueClientId,
};

type IpcClient = iceoryx2::port::client::Client<
    crate::IpcService,
    [CustomPayloadMarker],
    CustomHeaderMarker,
    [CustomPayloadMarker],
    CustomHeaderMarker,
>;
type LocalClient = iceoryx2::port::client::Client<
    crate::LocalService,
    [CustomPayloadMarker],
    CustomHeaderMarker,
    [CustomPayloadMarker],
    CustomHeaderMarker,
>;

pub(crate) enum ClientType {
    Ipc(Option<IpcClient>),
    Local(Option<LocalClient>),
}

#[pyclass]
/// Represents the receiving endpoint of an event based communication.
pub struct Client {
    pub(crate) value: Parc<ClientType>,
    pub(crate) request_payload_type_details: TypeStorage,
    pub(crate) response_payload_type_details: TypeStorage,
    pub(crate) request_header_type_details: TypeStorage,
    pub(crate) response_header_type_details: TypeStorage,
}

#[pymethods]
impl Client {
    #[getter]
    /// Returns the `UniqueClientId` of the `Client`
    pub fn id(&self) -> UniqueClientId {
        match &*self.value.lock() {
            ClientType::Ipc(Some(v)) => UniqueClientId(v.id()),
            ClientType::Local(Some(v)) => UniqueClientId(v.id()),
            _ => fatal_panic!(from "Client::id()", "Accessing a released client."),
        }
    }

    #[getter]
    /// Returns the `PortName` of the `Client`
    pub fn name(&self) -> PortName {
        match &*self.value.lock() {
            ClientType::Ipc(Some(v)) => PortName(*v.name()),
            ClientType::Local(Some(v)) => PortName(*v.name()),
            _ => fatal_panic!(from "Client::name()",
                              "Accessing a released client."),
        }
    }

    /// Releases the `Client`.
    ///
    /// After this call the `Client` is no longer usable!
    pub fn delete(&mut self) {
        match &mut *self.value.lock() {
            ClientType::Ipc(v) => {
                v.take();
            }
            ClientType::Local(v) => {
                v.take();
            }
        }
    }

    #[getter]
    /// Returns the strategy the `Client` follows when a `RequestMut` cannot be delivered
    /// if the `Server`'s buffer is full.
    pub fn backpressure_strategy(&self) -> BackpressureStrategy {
        match &*self.value.lock() {
            ClientType::Ipc(Some(v)) => v.backpressure_strategy().into(),
            ClientType::Local(Some(v)) => v.backpressure_strategy().into(),
            _ => {
                fatal_panic!(from "Client::backpressure_strategy()",
                    "Accessing a released client.")
            }
        }
    }

    /// Returns the maximum initial slice length configured for this `Client`.
    pub fn initial_max_slice_len(&self) -> usize {
        match &*self.value.lock() {
            ClientType::Ipc(Some(v)) => v.initial_max_slice_len(),
            ClientType::Local(Some(v)) => v.initial_max_slice_len(),
            _ => {
                fatal_panic!(from "Client::initial_max_slice_len()",
                    "Accessing a released client.")
            }
        }
    }

    #[getter]
    /// Returns the maximum amount of active requests the `Client` can send.
    pub fn max_active_requests(&self) -> usize {
        match &*self.value.lock() {
            ClientType::Ipc(Some(v)) => v.max_active_requests(),
            ClientType::Local(Some(v)) => v.max_active_requests(),
            _ => fatal_panic!(from "Client::max_active_requests()", "Accessing a released client."),
        }
    }

    /// Loans/allocates memory from the underlying data segment.
    ///
    /// The user has to initialize the payload before it can be sent. On failure it returns
    /// `LoanError` describing the failure.
    pub fn loan_uninit(&self) -> PyResult<RequestMutUninit> {
        ensure(
            self.request_payload_type_details.kind == PayloadKind::FixedSize,
            "`loan_uninit()` is not available for `Slice` or `Flatbuffer` payloads",
        )?;
        self.loan_slice_uninit_unchecked(1)
    }

    /// Loans/allocates memory from the underlying data segment.
    ///
    /// The user has to initialize the payload before it can be sent.
    /// Fails when it is called for data types which are not a slice.
    /// On failure it returns `LoanError` describing the failure.
    pub fn loan_slice_uninit(&self, number_of_elements: usize) -> PyResult<RequestMutUninit> {
        ensure(
            self.request_payload_type_details.kind == PayloadKind::Slice,
            "`loan_slice_uninit()` requires a `Slice` payload",
        )?;
        self.loan_slice_uninit_unchecked(number_of_elements)
    }

    /// Loans/allocates a `RequestMutUninit` from the underlying data segment of the `Client` with
    /// an integrated flatbuffer builder.
    pub fn loan_flatbuffer(&self) -> PyResult<RequestMutUninit> {
        ensure(
            self.request_payload_type_details.kind == PayloadKind::Flatbuffer,
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
    pub fn send_copy(&self, t: &Bound<'_, PyAny>) -> PyResult<PendingResponse> {
        ensure(
            self.request_payload_type_details.kind != PayloadKind::Flatbuffer,
            "`send_copy()` is not available for `Flatbuffer` payloads",
        )?;
        let uninit = self.loan_slice_uninit_unchecked(1)?;
        python_types::copy_value(
            t,
            self.request_payload_type_details.value.as_ref(),
            uninit.payload_ptr(),
        )?;
        uninit.__assume_init().send()
    }
}

// Helpers of the Python-side methods that are no longer part of the Python API.
impl Client {
    /// Loans/allocates a `RequestMutUninit` from the underlying data segment of the `Client`.
    /// The user has to initialize the payload before it can be sent.
    ///
    /// On failure it emits a `LoanError` describing the failure.
    pub(crate) fn loan_slice_uninit_unchecked(
        &self,
        slice_len: usize,
    ) -> PyResult<RequestMutUninit> {
        match &*self.value.lock() {
            ClientType::Ipc(Some(v)) => Ok(RequestMutUninit {
                value: Parc::new(RequestMutUninitType::Ipc(Some(unsafe {
                    v.loan_custom_payload(slice_len)
                        .map_err(|e| LoanError::new_err(format!("{e:?}")))?
                }))),
                request_payload_type_details: self.request_payload_type_details.clone(),
                response_payload_type_details: self.response_payload_type_details.clone(),
                request_header_type_details: self.request_header_type_details.clone(),
                response_header_type_details: self.response_header_type_details.clone(),
                builder: Default::default(),
            }),
            ClientType::Local(Some(v)) => Ok(RequestMutUninit {
                value: Parc::new(RequestMutUninitType::Local(Some(unsafe {
                    v.loan_custom_payload(slice_len)
                        .map_err(|e| LoanError::new_err(format!("{e:?}")))?
                }))),
                request_payload_type_details: self.request_payload_type_details.clone(),
                response_payload_type_details: self.response_payload_type_details.clone(),
                request_header_type_details: self.request_header_type_details.clone(),
                response_header_type_details: self.response_header_type_details.clone(),
                builder: Default::default(),
            }),
            _ => {
                fatal_panic!(from "Client::loan_slice_uninit()",
                    "Accessing a released client.")
            }
        }
    }
}
