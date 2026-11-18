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

use crate::python_types::{self, PayloadKind, ensure};
use iceoryx2::{
    port::update_connections::UpdateConnections,
    service::marker::{CustomHeaderMarker, CustomPayloadMarker},
};
use iceoryx2_log::fatal_panic;
use pyo3::prelude::*;

use crate::{
    backpressure_strategy::BackpressureStrategy,
    error::{ConnectionFailure, LoanError},
    parc::Parc,
    port_name::PortName,
    sample_mut_uninit::{SampleMutUninit, SampleMutUninitType},
    type_storage::TypeStorage,
    unique_publisher_id::UniquePublisherId,
};

pub(crate) enum PublisherType {
    Ipc(
        Option<
            iceoryx2::port::publisher::Publisher<
                crate::IpcService,
                [CustomPayloadMarker],
                CustomHeaderMarker,
            >,
        >,
    ),
    Local(
        Option<
            iceoryx2::port::publisher::Publisher<
                crate::LocalService,
                [CustomPayloadMarker],
                CustomHeaderMarker,
            >,
        >,
    ),
}

#[pyclass]
/// Represents the receiving endpoint of an event based communication.
pub struct Publisher {
    pub(crate) value: Parc<PublisherType>,
    pub(crate) payload_type_details: TypeStorage,
    pub(crate) user_header_type_details: TypeStorage,
}

#[pymethods]
impl Publisher {
    #[getter]
    /// Returns the `UniquePublisherId` of the `Publisher`
    pub fn id(&self) -> UniquePublisherId {
        match &*self.value.lock() {
            PublisherType::Ipc(Some(v)) => UniquePublisherId(v.id()),
            PublisherType::Local(Some(v)) => UniquePublisherId(v.id()),
            _ => fatal_panic!(from "Publisher::id()",
                "Accessing a deleted publisher."),
        }
    }

    #[getter]
    /// Returns the `PortName` of the `Publisher`
    pub fn name(&self) -> PortName {
        match &*self.value.lock() {
            PublisherType::Ipc(Some(v)) => PortName(*v.name()),
            PublisherType::Local(Some(v)) => PortName(*v.name()),
            _ => fatal_panic!(from "Publisher::name()",
                              "Accessing a deleted publisher."),
        }
    }

    #[getter]
    /// Returns the strategy the `Publisher` follows when a `SampleMut` cannot be delivered
    /// since the `Subscriber`'s buffer is full.
    pub fn backpressure_strategy(&self) -> BackpressureStrategy {
        match &*self.value.lock() {
            PublisherType::Ipc(Some(v)) => v.backpressure_strategy().into(),
            PublisherType::Local(Some(v)) => v.backpressure_strategy().into(),
            _ => fatal_panic!(from "Publisher::backpressure_strategy()",
                "Accessing a deleted publisher."),
        }
    }

    #[getter]
    /// Returns the maximum initial slice length configured for this `Publisher`.
    pub fn initial_max_slice_len(&self) -> usize {
        match &*self.value.lock() {
            PublisherType::Ipc(Some(v)) => v.initial_max_slice_len(),
            PublisherType::Local(Some(v)) => v.initial_max_slice_len(),
            _ => fatal_panic!(from "Publisher::initial_max_slice_len()",
                "Accessing a deleted publisher."),
        }
    }

    /// Explicitly updates the connection to every `Subscriber`. This is
    /// required to be called whenever a new `Subscriber` connected to
    /// the service. It is done implicitly whenever `SampleMut.send` or
    /// `Publisher.send_copy` is called. When a `Subscriber` is connected
    /// that requires a history this call will deliver it.
    pub fn update_connections(&self) -> PyResult<()> {
        match &*self.value.lock() {
            PublisherType::Ipc(Some(v)) => v
                .update_connections()
                .map_err(|e| ConnectionFailure::new_err(format!("{e:?}")))?,
            PublisherType::Local(Some(v)) => v
                .update_connections()
                .map_err(|e| ConnectionFailure::new_err(format!("{e:?}")))?,
            _ => {
                fatal_panic!(from "Publisher::update_connections()", "Accessing a deleted publisher.");
            }
        }

        Ok(())
    }

    /// Releases the `Publisher`.
    ///
    /// After this call the `Publisher` is no longer usable!
    pub fn delete(&mut self) {
        match &mut *self.value.lock() {
            PublisherType::Ipc(v) => {
                v.take();
            }
            PublisherType::Local(v) => {
                v.take();
            }
        }
    }

    /// Loans/allocates a `SampleMutUninit` from the underlying data segment of the `Publisher`.
    ///
    /// The user has to initialize the payload before it can be sent. On failure it returns
    /// `LoanError` describing the failure.
    pub fn loan_uninit(&self) -> PyResult<SampleMutUninit> {
        ensure(
            self.payload_type_details.kind == PayloadKind::FixedSize,
            "`loan_uninit()` is not available for `Slice` or `Flatbuffer` payloads",
        )?;
        self.loan_slice_uninit_unchecked(1)
    }

    /// Loans/allocates a `SampleMutUninit` from the underlying data segment of the `Publisher`.
    ///
    /// The user has to initialize the payload before it can be sent.
    /// Fails when it is called for data types which are not a slice.
    /// On failure it returns `LoanError` describing the failure.
    pub fn loan_slice_uninit(&self, number_of_elements: usize) -> PyResult<SampleMutUninit> {
        ensure(
            self.payload_type_details.kind == PayloadKind::Slice,
            "`loan_slice_uninit()` requires a `Slice` payload",
        )?;
        self.loan_slice_uninit_unchecked(number_of_elements)
    }

    /// Loans/allocates a `SampleMutUninit` from the underlying data segment of the `Publisher`
    /// with an integrated flatbuffer builder.
    pub fn loan_flatbuffer(&self) -> PyResult<SampleMutUninit> {
        ensure(
            self.payload_type_details.kind == PayloadKind::Flatbuffer,
            "`loan_flatbuffer()` requires a `Flatbuffer` payload",
        )?;
        // Loaning a slice of 1 byte is exactly what we need here. The flatbuffer builder is
        // in python not zero-copy and completely resides on the heap since they do not have
        // an API to provide a custom allocator.
        //
        // When the data production is finished the sample payload is grown/resized and the
        // serialized flatbuffer content is copied into the sample.
        self.loan_slice_uninit_unchecked(1)
    }

    /// Sends a copy of the provided value.
    pub fn send_copy(&self, t: &Bound<'_, PyAny>) -> PyResult<usize> {
        ensure(
            self.payload_type_details.kind != PayloadKind::Flatbuffer,
            "`send_copy()` is not available for `Flatbuffer` payloads",
        )?;
        let sample = self.loan_uninit()?;
        python_types::copy_value(
            t,
            self.payload_type_details.value.as_ref(),
            sample.payload_ptr(),
        )?;
        sample.__assume_init().send()
    }
}

// Helpers of the Python-side methods that are no longer part of the Python API.
impl Publisher {
    /// Loans/allocates a `SampleMutUninit` from the underlying data segment of the `Publisher`.
    /// The user has to initialize the payload before it can be sent.
    /// Fails when it is called for data types which are not a slice.
    ///
    /// On failure it returns `LoanError` describing the failure.
    pub(crate) fn loan_slice_uninit_unchecked(
        &self,
        number_of_elements: usize,
    ) -> PyResult<SampleMutUninit> {
        match &*self.value.lock() {
            PublisherType::Ipc(Some(v)) => {
                let sample = unsafe {
                    v.loan_custom_payload(number_of_elements)
                        .map_err(|e| LoanError::new_err(format!("{e:?}")))?
                };
                Ok(SampleMutUninit {
                    value: Parc::new(SampleMutUninitType::Ipc(Some(sample))),
                    payload_type_details: self.payload_type_details.clone(),
                    user_header_type_details: self.user_header_type_details.clone(),
                })
            }
            PublisherType::Local(Some(v)) => {
                let sample = unsafe {
                    v.loan_custom_payload(number_of_elements)
                        .map_err(|e| LoanError::new_err(format!("{e:?}")))?
                };
                Ok(SampleMutUninit {
                    value: Parc::new(SampleMutUninitType::Local(Some(sample))),
                    payload_type_details: self.payload_type_details.clone(),
                    user_header_type_details: self.user_header_type_details.clone(),
                })
            }
            _ => fatal_panic!(from "Publisher::loan_slice_uninit()",
                "Accessing a deleted publisher."),
        }
    }
}
