from __future__ import annotations

from collections.abc import Iterator, Iterable, Sequence
from typing import TYPE_CHECKING, Self

from portable_device_api import definitions, PortableDeviceKeyCollection, PropertyKey

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
