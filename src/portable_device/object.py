from __future__ import annotations

from collections.abc import Iterator, Iterable, Sequence
from typing import TYPE_CHECKING, Self

from comtypes.automation import VT_LPWSTR

from portable_device_api import (definitions, PortableDeviceKeyCollection, PropertyKey, PortableDeviceValues,
                                 PortableDevicePropVariantCollection, PropVariant)

if TYPE_CHECKING:
    from portable_device import Device


class Object:
    def __init__(self, device: Device, object_id: str):
        self._device = device
        self._object_id = object_id

        self._content = self._device._content
        self._properties = self._device._properties

    @property
    def object_id(self) -> str:
        return self._object_id

    # TODO test that it can be changed or cache it
    def object_name(self) -> str:
        keys = PortableDeviceKeyCollection.create()
        keys.add(definitions.WPD_OBJECT_ORIGINAL_FILE_NAME)
        return self._properties.get_values(self._object_id, keys).get_string_value(definitions.WPD_OBJECT_ORIGINAL_FILE_NAME)

    def children(self) -> Iterator[Self]:
        enum_object_ids = self._content.enum_objects(self._object_id)

        while object_ids := enum_object_ids.next(1):
            for object_id in object_ids:
                yield Object(self._device, object_id)

    def walk(self, *, depth = 0) -> Iterator[tuple[int, Self]]:
        yield depth, self

        for child in self.children():
            yield from child.walk(depth = depth + 1)

    def get_properties(self, keys: Sequence[PropertyKey]):
        key_collection = PortableDeviceKeyCollection.create()
        for key in keys:
            key_collection.add(key)

        property_values = self._properties.get_values(self._object_id, key_collection)

        # TODO if the key is not in the collection:
        #   * property_values.get_string_value raises get COMError (-2147023728 = 0x80070490 = ERROR_NOT_FOUND)
        #   * property_values.get_value returns -2147023728 instead, and v.VT is comtypes.automation.VT_ERROR
        # We can't easily use the former without exposing PortableDeviceValues
        # and PropVariant, and we don't want the latter. PortableDeviceValues
        # has get_error_value, maybe we can use this (but does it distinguish
        # an error from a regular integer-typed property?). Otherwise, we may
        # have to use property_values.get_count and property_values.get_at
        # (returns key, value) and check for presence ourselves.
        # Also explain this in portable_device_api.PortableDeviceValues
        # Or maybe we could embed the expected value in the PropertyKey
        return [property_values.get_value(key).value for key in keys]

    def create_directory(self, dir_name: str) -> Self:
        values = PortableDeviceValues.create()
        values.set_guid_value(definitions.WPD_OBJECT_CONTENT_TYPE, definitions.WPD_CONTENT_TYPE_FOLDER)
        values.set_string_value(definitions.WPD_OBJECT_PARENT_ID, self._object_id)
        values.set_string_value(definitions.WPD_OBJECT_NAME, dir_name)

        return type(self)(self._device, self._content.create_object_with_properties_only(values))

    def get_child_by_name(self, child_name: str) -> Self:
        object_ids = self._content.enum_objects(self._object_id).next(999)  # TODO arbitrary number
        keys = PortableDeviceKeyCollection.create()
        keys.add(definitions.WPD_OBJECT_ORIGINAL_FILE_NAME)
        matching_object_ids = [oid for oid in object_ids if self._properties.get_values(oid, keys).get_string_value(
            definitions.WPD_OBJECT_ORIGINAL_FILE_NAME) == child_name]
        assert len(matching_object_ids) == 1
        return type(self)(self._device, matching_object_ids[0])

    def delete(self):
        object_ids_pvc = PortableDevicePropVariantCollection.create()
        object_ids_pvc.add(PropVariant.create(VT_LPWSTR, self._object_id))
        self._content.delete(definitions.DELETE_OBJECT_OPTIONS.PORTABLE_DEVICE_DELETE_NO_RECURSION, object_ids_pvc)
