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
use crate::python_types::{PayloadKind, ensure};
use iceoryx2::service::marker::{CustomHeaderMarker, CustomPayloadMarker};
use iceoryx2_log::fatal_panic;
use pyo3::prelude::*;

use crate::{
    error::SendError, header_publish_subscribe::HeaderPublishSubscribe, parc::Parc,
    type_storage::TypeStorage,
};

pub(crate) enum SampleMutType {
    Ipc(
        Option<
            iceoryx2::sample_mut::SampleMut<
                crate::IpcService,
                [CustomPayloadMarker],
                CustomHeaderMarker,
            >,
        >,
    ),
    Local(
        Option<
            iceoryx2::sample_mut::SampleMut<
                crate::LocalService,
                [CustomPayloadMarker],
                CustomHeaderMarker,
            >,
        >,
    ),
}

#[pyclass]
/// Acquired by initializing a `SampleMutUninit` via
///  * `SampleMutUninit.write_payload`,
///  * `SampleMutUninit.assume_init`
///
/// It stores the payload that will be sent
/// to every connected `Subscriber`. If the `SampleMut` is not sent
/// it will release the loaned memory when going out of scope.
pub struct SampleMut {
    pub(crate) value: Parc<SampleMutType>,
    pub(crate) payload_type_details: TypeStorage,
    pub(crate) user_header_type_details: TypeStorage,
}

#[pymethods]
impl SampleMut {
    #[getter]
    /// Returns the `HeaderPublishSubscribe` of the `Sample`.
    pub fn header(&self) -> HeaderPublishSubscribe {
        match &*self.value.lock() {
            SampleMutType::Ipc(Some(v)) => HeaderPublishSubscribe(*v.header()),
            SampleMutType::Local(Some(v)) => HeaderPublishSubscribe(*v.header()),
            _ => fatal_panic!(from "SampleMut::header()",
                "Accessing a released sample."),
        }
    }

    #[getter]
    /// Returns the address of the user header as an `int`.
    /// `SampleMut.user_header` provides typed access.
    pub fn user_header_ptr(&self) -> usize {
        match &mut *self.value.lock() {
            SampleMutType::Ipc(Some(v)) => {
                (v.user_header_mut() as *mut CustomHeaderMarker) as usize
            }
            SampleMutType::Local(Some(v)) => {
                (v.user_header_mut() as *mut CustomHeaderMarker) as usize
            }
            _ => fatal_panic!(from "SampleMut::user_header_ptr()",
                "Accessing a released sample."),
        }
    }

    #[getter]
    /// Returns the address of the payload as an `int`.
    /// `SampleMut.payload` provides typed access.
    pub fn payload_ptr(&self) -> usize {
        match &mut *self.value.lock() {
            SampleMutType::Ipc(Some(v)) => (v.payload_mut().as_mut_ptr()) as usize,
            SampleMutType::Local(Some(v)) => (v.payload_mut().as_mut_ptr()) as usize,
            _ => fatal_panic!(from "SampleMut::user_header_ptr()",
                "Accessing a released sample."),
        }
    }

    /// Releases the `SampleMut`.
    ///
    /// After this call the `SampleMut` is no longer usable!
    pub fn delete(&mut self) {
        match &mut *self.value.lock() {
            SampleMutType::Ipc(v) => {
                v.take();
            }
            SampleMutType::Local(v) => {
                v.take();
            }
        }
    }

    /// Send a previously loaned `Publisher.loan_uninit` `SampleMut` to every connected
    /// `Subscriber` of the service.
    ///
    /// On success the number of `Subscriber` ports that received
    /// the data is returned, otherwise a `SendError` is emitted describing the failure.
    pub fn send(&self) -> PyResult<usize> {
        match &mut *self.value.lock() {
            SampleMutType::Ipc(v) => {
                let sample = v.take().unwrap();
                Ok(sample
                    .send()
                    .map_err(|e| SendError::new_err(format!("{e:?}")))?)
            }
            SampleMutType::Local(v) => {
                let sample = v.take().unwrap();
                Ok(sample
                    .send()
                    .map_err(|e| SendError::new_err(format!("{e:?}")))?)
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

// Helpers of the Python-side methods that are no longer part of the Python API.
impl SampleMut {
    pub(crate) fn truncate_unchecked(&self, number_of_elements: usize) {
        match &mut *self.value.lock() {
            SampleMutType::Ipc(Some(v)) => v.truncate(number_of_elements),
            SampleMutType::Local(Some(v)) => v.truncate(number_of_elements),
            _ => fatal_panic!(from "SampleMut::__truncate()",
                "Accessing a released sample."),
        }
    }
}
