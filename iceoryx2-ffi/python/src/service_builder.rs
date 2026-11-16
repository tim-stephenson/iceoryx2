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

use crate::public::Public;
use iceoryx2::service::marker::{CustomHeaderMarker, CustomKeyMarker, CustomPayloadMarker};
use pyo3::prelude::*;

use crate::parc::Parc;
use crate::service_builder_blackboard::{
    ServiceBuilderBlackboardCreatorType, ServiceBuilderBlackboardOpenerType,
};
use crate::service_builder_request_response::ServiceBuilderRequestResponseType;
use crate::{
    service_builder_blackboard::{ServiceBuilderBlackboardCreator, ServiceBuilderBlackboardOpener},
    service_builder_event::{ServiceBuilderEvent, ServiceBuilderEventType},
    service_builder_publish_subscribe::{
        ServiceBuilderPublishSubscribe, ServiceBuilderPublishSubscribeType,
    },
    service_builder_request_response::ServiceBuilderRequestResponse,
};

pub(crate) enum ServiceBuilderType {
    Ipc(iceoryx2::service::builder::Builder<crate::IpcService>),
    Local(iceoryx2::service::builder::Builder<crate::LocalService>),
}

#[pyclass]
/// Builder to create or open a `Service`
pub struct ServiceBuilder(pub(crate) Parc<ServiceBuilderType>);

#[pymethods]
impl ServiceBuilder {
    /// Create a new builder to create a `MessagingPattern.Event` `Service`.
    pub fn event(&self) -> ServiceBuilderEvent {
        match &*self.0.lock() {
            ServiceBuilderType::Ipc(v) => {
                let this = v.clone();
                ServiceBuilderEvent(ServiceBuilderEventType::Ipc(this.event()))
            }
            ServiceBuilderType::Local(v) => {
                let this = v.clone();
                ServiceBuilderEvent(ServiceBuilderEventType::Local(this.event()))
            }
        }
    }

    /// Returns the `ServiceBuilderPublishSubscribe` to create a new publish-subscribe service.
    /// The payload ctype must be provided as argument.
    pub fn publish_subscribe(
        &self,
        t: &Bound<'_, PyAny>,
    ) -> PyResult<Public<ServiceBuilderPublishSubscribe>> {
        self.publish_subscribe_builder()
            .with_payload_type(t)
            .map(Public)
    }

    /// Returns the `ServiceBuilderRequestResponse` to create a new request-response service.
    ///
    /// The request/response payload ctype must be provided as argument.
    pub fn request_response(
        &self,
        request: &Bound<'_, PyAny>,
        response: &Bound<'_, PyAny>,
    ) -> PyResult<Public<ServiceBuilderRequestResponse>> {
        self.request_response_builder()
            .with_payload_types(request, response)
            .map(Public)
    }

    /// Returns the `ServiceBuilderBlackboardCreator` to create a new blackboard service.
    ///
    /// The key ctype must be provided as argument. If the key is of type ctypes.Structure,
    /// it must implement __eq__.
    pub fn blackboard_creator(
        &self,
        key: &Bound<'_, PyAny>,
    ) -> PyResult<Public<ServiceBuilderBlackboardCreator>> {
        self.blackboard_creator_builder()
            .with_key_type(key)
            .map(Public)
    }

    /// Returns the `ServiceBuilderBlackboardOpener` to open a blackboard service.
    ///
    /// The key ctype must be provided as argument.
    pub fn blackboard_opener(
        &self,
        key: &Bound<'_, PyAny>,
    ) -> PyResult<ServiceBuilderBlackboardOpener> {
        self.blackboard_opener_builder().with_key_type(key)
    }
}

// Helpers of the Python-side methods that are no longer part of the Python API.
impl ServiceBuilder {
    /// Create a new builder to create a `MessagingPattern.PublishSubscribe` `Service`.
    pub(crate) fn publish_subscribe_builder(&self) -> ServiceBuilderPublishSubscribe {
        match &*self.0.lock() {
            ServiceBuilderType::Ipc(v) => {
                let this = v.clone();
                ServiceBuilderPublishSubscribe::new(ServiceBuilderPublishSubscribeType::Ipc(
                    this.publish_subscribe::<[CustomPayloadMarker]>()
                        .user_header::<CustomHeaderMarker>(),
                ))
            }
            ServiceBuilderType::Local(v) => {
                let this = v.clone();
                ServiceBuilderPublishSubscribe::new(ServiceBuilderPublishSubscribeType::Local(
                    this.publish_subscribe::<[CustomPayloadMarker]>()
                        .user_header::<CustomHeaderMarker>(),
                ))
            }
        }
    }

    /// Create a new builder to create a `MessagingPattern.RequestResponse` `Service`.
    pub(crate) fn request_response_builder(&self) -> ServiceBuilderRequestResponse {
        match &*self.0.lock() {
            ServiceBuilderType::Ipc(v) => {
                let this = v.clone();
                ServiceBuilderRequestResponse::new(ServiceBuilderRequestResponseType::Ipc(
                    this.request_response::<[CustomPayloadMarker], [CustomPayloadMarker]>()
                        .request_user_header::<CustomHeaderMarker>()
                        .response_user_header::<CustomHeaderMarker>(),
                ))
            }
            ServiceBuilderType::Local(v) => {
                let this = v.clone();
                ServiceBuilderRequestResponse::new(ServiceBuilderRequestResponseType::Local(
                    this.request_response::<[CustomPayloadMarker], [CustomPayloadMarker]>()
                        .request_user_header::<CustomHeaderMarker>()
                        .response_user_header::<CustomHeaderMarker>(),
                ))
            }
        }
    }

    /// Create a new builder to create a `MessagingPattern.Blackboard` `Service`.
    pub(crate) fn blackboard_creator_builder(&self) -> ServiceBuilderBlackboardCreator {
        match &*self.0.lock() {
            ServiceBuilderType::Ipc(v) => {
                let this = v.clone();
                ServiceBuilderBlackboardCreator::new(ServiceBuilderBlackboardCreatorType::Ipc(
                    Some(this.blackboard_creator::<CustomKeyMarker>()),
                ))
            }
            ServiceBuilderType::Local(v) => {
                let this = v.clone();
                ServiceBuilderBlackboardCreator::new(ServiceBuilderBlackboardCreatorType::Local(
                    Some(this.blackboard_creator::<CustomKeyMarker>()),
                ))
            }
        }
    }

    /// Create a new builder to open a `MessagingPattern.Blackboard` `Service`.
    pub(crate) fn blackboard_opener_builder(&self) -> ServiceBuilderBlackboardOpener {
        match &*self.0.lock() {
            ServiceBuilderType::Ipc(v) => {
                let this = v.clone();
                ServiceBuilderBlackboardOpener::new(ServiceBuilderBlackboardOpenerType::Ipc(Some(
                    this.blackboard_opener::<CustomKeyMarker>(),
                )))
            }
            ServiceBuilderType::Local(v) => {
                let this = v.clone();
                ServiceBuilderBlackboardOpener::new(ServiceBuilderBlackboardOpenerType::Local(
                    Some(this.blackboard_opener::<CustomKeyMarker>()),
                ))
            }
        }
    }
}
