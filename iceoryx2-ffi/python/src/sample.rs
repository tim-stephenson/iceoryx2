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
    header_publish_subscribe::HeaderPublishSubscribe, parc::Parc, type_storage::TypeStorage,
};

pub(crate) enum SampleType {
    Ipc(
        Option<
            iceoryx2::sample::Sample<crate::IpcService, [CustomPayloadMarker], CustomHeaderMarker>,
        >,
    ),
    Local(
        Option<
            iceoryx2::sample::Sample<
                crate::LocalService,
                [CustomPayloadMarker],
                CustomHeaderMarker,
            >,
        >,
    ),
}

#[pyclass]
/// It stores the payload and is acquired by the `Subscriber` whenever
/// it receives new data from a `Publisher` via `Subscriber.receive`.
pub struct Sample {
    pub(crate) value: Parc<SampleType>,
    pub payload_type_details: TypeStorage,
    pub user_header_type_details: TypeStorage,
}

#[pymethods]
impl Sample {
    #[getter]
    /// Returns the `HeaderPublishSubscribe` of the `Sample`.
    pub fn header(&self) -> HeaderPublishSubscribe {
        match &*self.value.lock() {
            SampleType::Ipc(Some(v)) => HeaderPublishSubscribe(*v.header()),
            SampleType::Local(Some(v)) => HeaderPublishSubscribe(*v.header()),
            _ => fatal_panic!(from "Sample::header()",
                "Accessing a released sample."),
        }
    }

    #[getter]
    /// Returns the address of the user header as an `int`.
    /// `Sample.user_header` provides typed access.
    pub fn user_header_ptr(&self) -> usize {
        match &mut *self.value.lock() {
            SampleType::Ipc(Some(v)) => (v.user_header() as *const CustomHeaderMarker) as usize,
            SampleType::Local(Some(v)) => (v.user_header() as *const CustomHeaderMarker) as usize,
            _ => fatal_panic!(from "Sample::user_header_ptr()",
                "Accessing a released sample."),
        }
    }

    #[getter]
    /// Returns the address of the payload as an `int`.
    /// `Sample.payload` provides typed access.
    pub fn payload_ptr(&self) -> usize {
        match &mut *self.value.lock() {
            SampleType::Ipc(Some(v)) => (v.payload().as_ptr()) as usize,
            SampleType::Local(Some(v)) => (v.payload().as_ptr()) as usize,
            _ => fatal_panic!(from "Sample::payload_ptr()",
                "Accessing a released sample."),
        }
    }

    /// Releases the `Sample`.
    ///
    /// After this call the `Sample` is no longer usable!
    pub fn delete(&mut self) {
        match &mut *self.value.lock() {
            SampleType::Ipc(v) => {
                v.take();
            }
            SampleType::Local(v) => {
                v.take();
            }
        }
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
            Some(this.header().number_of_elements()),
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

    /// Returns the serialized flatbuffer data as bytes.
    ///
    /// Only available when the payload type is a `Flatbuffer`.
    pub fn payload_bytes(slf: &Bound<'_, Self>) -> PyResult<payload_access::ByteSlice> {
        let this = slf.borrow();
        let header = this.header();
        payload_access::payload_bytes(
            slf.as_any(),
            &this.payload_type_details,
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
            &this.payload_type_details,
            this.payload_ptr(),
            header.number_of_elements(),
            header.payload_offset(),
        )
    }
}
