from __future__ import annotations

from collections.abc import Iterator, Iterable, Sequence, Generator
from typing import TYPE_CHECKING, Self

from comtypes import COMError
from comtypes.automation import VT_LPWSTR

from portable_device_api import (definitions, PortableDeviceKeyCollection, PropertyKey, PortableDeviceValues,
                                 PortableDevicePropVariantCollection, PropVariant, errors)

from portable_device import ObjectList

if TYPE_CHECKING:
    from portable_device import Device


class Object:
    def __init__(self, device: Device, object_id: str):
        self._device = device
        self._object_id = object_id

        self._content = self._device._content
        self._properties = self._device._properties

    # Properties ###############################################################

    @property
    def object_id(self) -> str:
        return self._object_id

    # Object properties ########################################################

    def supported_properties(self) -> list[PropertyKey]:
        supported_properties = self._properties.get_supported_properties(self._object_id)
        return [supported_properties.get_at(i) for i in range(supported_properties.get_count())]

    def _get_properties(self, keys: Iterable[PropertyKey]):
        """
        Returns PortableDeviceValues, on which you can call:
          * get_string_value -> gets a string
          * get_value -> gets a PropVariant, use .value for the actual value
        """
        keys = list(keys)

        key_collection = PortableDeviceKeyCollection.create()
        for key in keys:
            key_collection.add(key)

        return self._properties.get_values(self._object_id, key_collection)

    # TODO should return a dict?
    def get_properties(self, keys: Iterable[PropertyKey]):
        keys = list(keys)

        properties = self._get_properties(keys)

        # TODO if the key is not in the collection (e. g. file name for device
        # objects and root objects, or object name for device objects):
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
        return [properties.get_value(key).value for key in keys]

    def get_property(self, key: PropertyKey):
        return self._get_properties([key]).get_value(key).value

    def object_name(self) -> str:
        return self.get_property(definitions.WPD_OBJECT_NAME)

    def file_name(self) -> str:
        return self.get_property(definitions.WPD_OBJECT_ORIGINAL_FILE_NAME)

    # Object property attributes ###############################################

    def property_attributes(self, property: PropertyKey) -> dict:  # TODO more specific
        attributes = self._properties.get_property_attributes(self._object_id, property)
        result = {}
        for i in range(attributes.get_count()):
            key, value = attributes.get_at(i)
            result[key] = value.value
        return result

    # Children #################################################################

    def _children(self) -> Iterator[Self]:
        enum_object_ids = self._content.enum_objects(self._object_id)

        while object_ids := enum_object_ids.next(1):
            for object_id in object_ids:
                yield Object(self._device, object_id)

    # TODO a custom generator would be nicer
    def children(self) -> ObjectList:
        return ObjectList(self._children())

    def child_by_path(self, child_path: list[str]) -> Self:
        current = self

        for child_name in child_path:
            current = current.children().by_file_name(child_name)

        return current

    def walk(self, *, depth = 0) -> Iterator[tuple[int, Self]]:
        yield depth, self

        for child in self.children():
            yield from child.walk(depth = depth + 1)

    # Child creation ###########################################################

    def create_directory(self, dir_name: str) -> Self:
        values = PortableDeviceValues.create()
        values.set_guid_value(definitions.WPD_OBJECT_CONTENT_TYPE, definitions.WPD_CONTENT_TYPE_FOLDER)
        values.set_string_value(definitions.WPD_OBJECT_PARENT_ID, self._object_id)
        values.set_string_value(definitions.WPD_OBJECT_NAME, dir_name)

        return type(self)(self._device, self._content.create_object_with_properties_only(values))

    # TODO rename
    def upload_file(self, file_name: str, content: bytes) -> Self:
        values = PortableDeviceValues.create()
        values.set_string_value(definitions.WPD_OBJECT_PARENT_ID, self._object_id)
        values.set_unsigned_large_integer_value(definitions.WPD_OBJECT_SIZE, len(content))
        values.set_string_value(definitions.WPD_OBJECT_ORIGINAL_FILE_NAME, file_name)
        values.set_string_value(definitions.WPD_OBJECT_NAME, file_name)

        stream, chunk_size = self._content.create_object_with_properties_and_data(values)
        buffer = bytearray(content)
        while buffer:
            this_chunk_size = min(len(buffer), chunk_size)
            chunk = buffer[0:this_chunk_size]
            buffer[0:this_chunk_size] = []
            stream.remote_write(chunk)
        stream.commit()

        return type(self)(self._device, stream.get_object_id())

    # File access ##############################################################

    # You must exhaust or close the iterator, or you won't be able to delete
    # the file
    def download(self, chunk_size: int | None = None) -> Generator[bytes]:
        stream, optimal_transfer_size = self._content.transfer().get_stream(self._object_id)

        if chunk_size is None:
            chunk_size = optimal_transfer_size

        while chunk := stream.remote_read(chunk_size):
            try:
                yield chunk
            except GeneratorExit:
                # Does not seem necessary
                stream.cancel()

                # Seems necessary if `stream` doesn't go out of scope before the
                # next operation
                del stream

                break

    def download_all(self, chunk_size: int | None = None) -> bytes:
        buffer = bytearray()
        for chunk in self.download(chunk_size):
            buffer.extend(chunk)
        return buffer

    # Modification #############################################################

    def delete(self, recursive: bool):
        # TODO exception if the result is not 0
        return ObjectList([self]).delete(recursive)[0]

    def move_into(self, target: Object):
        # TODO exception if the result is not 0
        return ObjectList([self]).move_into(target)[0]
