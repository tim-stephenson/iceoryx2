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
use crate::python_types;
use iceoryx2_log::fatal_panic;
use pyo3::prelude::*;

use crate::entry_handle_mut::{EntryHandleMut, EntryHandleMutType};
use crate::parc::Parc;
use crate::type_detail::TypeDetail;
use crate::type_storage::TypeStorage;

pub(crate) enum EntryValueUninitType {
    Ipc(Option<iceoryx2::port::writer::__InternalEntryValueUninit<crate::IpcService>>),
    Local(Option<iceoryx2::port::writer::__InternalEntryValueUninit<crate::LocalService>>),
}

#[pyclass]
pub struct EntryValueUninit {
    pub(crate) value: Parc<EntryValueUninitType>,
    pub(crate) value_type_details: TypeDetail,
    pub(crate) value_type_storage: TypeStorage,
}

#[pymethods]
impl EntryValueUninit {
    /// Discards the `EntryValueUninit` and returns the original
    /// `EntryHandleMut`.
    pub fn discard(&mut self) -> EntryHandleMut {
        match &mut *self.value.lock() {
            EntryValueUninitType::Ipc(v) => {
                let entry_value_uninit = v.take().unwrap();
                let entry_handle_mut = entry_value_uninit.discard();
                EntryHandleMut {
                    value: Parc::new(EntryHandleMutType::Ipc(Some(entry_handle_mut))),
                    value_type_storage: self.value_type_storage.clone(),
                    value_type_details: self.value_type_details.clone(),
                }
            }
            EntryValueUninitType::Local(v) => {
                let entry_value_uninit = v.take().unwrap();
                let entry_handle_mut = entry_value_uninit.discard();
                EntryHandleMut {
                    value: Parc::new(EntryHandleMutType::Local(Some(entry_handle_mut))),
                    value_type_storage: self.value_type_storage.clone(),
                    value_type_details: self.value_type_details.clone(),
                }
            }
        }
    }

    /// Makes the new value accessible.
    ///
    /// Consumes the `EntryValueUninit`, makes the new value accessible and returns the original
    /// `EntryHandleMut`.
    pub fn assume_init_and_update(&mut self) -> EntryHandleMut {
        self.update_write_cell()
    }

    /// Updates the entry value.
    ///
    /// Consumes the `EntryValueUninit`, writes the value to the entry and returns the original
    /// `EntryHandleMut`.
    pub fn update_with_copy(&mut self, value: &Bound<'_, PyAny>) -> PyResult<EntryHandleMut> {
        let size = python_types::ensure_layout(value, self.value_type_storage.value.as_ref())?;
        python_types::copy_bytes(value, self.__get_write_cell(), size)?;
        Ok(self.update_write_cell())
    }

    /// Returns a `ctypes.POINTER` to the value of the blackboard entry.
    ///
    /// It can be used to update the value without copy. After writing,
    /// assume_init_and_update() must be called.
    pub fn value_mut(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        payload_access::value_pointer(
            py,
            self.__get_write_cell(),
            self.value_type_storage.value.as_ref(),
        )
    }
}

// Helpers of the Python-side methods that are no longer part of the Python API.
impl EntryValueUninit {
    pub(crate) fn update_write_cell(&mut self) -> EntryHandleMut {
        match &mut *self.value.lock() {
            EntryValueUninitType::Ipc(v) => {
                let entry_value_uninit = v.take().unwrap();
                let entry_handle_mut = entry_value_uninit.update();
                EntryHandleMut {
                    value: Parc::new(EntryHandleMutType::Ipc(Some(entry_handle_mut))),
                    value_type_storage: self.value_type_storage.clone(),
                    value_type_details: self.value_type_details.clone(),
                }
            }
            EntryValueUninitType::Local(v) => {
                let entry_value_uninit = v.take().unwrap();
                let entry_handle_mut = entry_value_uninit.update();
                EntryHandleMut {
                    value: Parc::new(EntryHandleMutType::Local(Some(entry_handle_mut))),
                    value_type_storage: self.value_type_storage.clone(),
                    value_type_details: self.value_type_details.clone(),
                }
            }
        }
    }

    pub fn __get_write_cell(&self) -> usize {
        match &*self.value.lock() {
            EntryValueUninitType::Ipc(Some(v)) => v.write_cell() as usize,
            EntryValueUninitType::Local(Some(v)) => v.write_cell() as usize,
            _ => {
                fatal_panic!(from "EntryValueUninit::write()", "Accessing a deleted EntryValueUninit")
            }
        }
    }
}
