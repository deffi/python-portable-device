from collections.abc import Iterator, Callable, Iterable
from functools import cache
from portable_device_api import (PortableDeviceManager, PortableDevice, PortableDeviceContent, PortableDeviceProperties,
                                 definitions)
from typing import Self

from portable_device import Object, ObjectList
from portable_device.exceptions import DeviceNotFound, AmbiguousDevice, ObjectNotFound, AmbiguousObject


@cache
def _manager() -> PortableDeviceManager:
    return PortableDeviceManager.create()


class Device:
    def __init__(self, device_id: str):
        self._device_id = device_id

    # Creation #################################################################

    @classmethod
    def all(cls, *, refresh = True) -> Iterator[Self]:
        if refresh:
            _manager().refresh_device_list()

        for device_id in _manager().get_devices():
            yield cls(device_id)

    @classmethod
    def find(cls, filter_: Callable[["Device"], bool], /, reference: str, *, refresh = True):
        matching_devices = [device for device in cls.all(refresh=refresh) if filter_(device)]

        if len(matching_devices) == 0:
            raise DeviceNotFound(reference)
        elif len(matching_devices) == 1:
            return matching_devices[0]
        else:
            raise AmbiguousDevice(reference)

    @classmethod
    def by_description(cls, description: str, *,
                       refresh = True, ignore_trailing_space: bool = True) -> Self:

        description_map = str.rstrip if ignore_trailing_space else str
        description = description_map(description)

        return cls.find(lambda d: description_map(d.description) == description,
                        reference = repr(description),
                        refresh = refresh)

    @classmethod
    def by_friendly_name(cls, friendly_name: str, *, refresh = True) -> Self:
        return cls.find(lambda d: d.friendly_name == friendly_name,
                        reference = repr(friendly_name),
                        refresh = refresh)

    # Open #####################################################################

    def open(self):
        self._device.open(self._device_id)

    def close(self):
        self._device.close()

    # Context manager ##########################################################

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # Properties ###############################################################

    @property
    def device_id(self) -> str:
        """Can be accessed without opening the device"""
        return self._device_id

    @property
    @cache
    def description(self) -> str:
        """Can be accessed without opening the device"""
        return _manager().get_device_description(self._device_id)

    @property
    @cache
    def friendly_name(self) -> str:
        """Can be accessed without opening the device"""
        return _manager().get_device_friendly_name(self._device_id)

    @property
    @cache
    def manufacturer(self) -> str:
        """Can be accessed without opening the device"""
        return _manager().get_device_manufacturer(self._device_id)

    @property
    @cache
    def _device(self):
        return PortableDevice.create()

    @property
    @cache
    def _content(self) -> PortableDeviceContent:
        return self._device.content()

    @property
    @cache
    def _properties(self) -> PortableDeviceProperties:
        return self._content.properties()

    # Object access ############################################################

    @property
    @cache
    def device_object(self) -> Object:
        return Object(self, definitions.WPD_DEVICE_OBJECT_ID)

    def root_objects(self) -> ObjectList:
        return self.device_object.children()

    def root_object(self, name: str) -> Object:
        if name:
            # Select root object by name
            return self.root_objects().by_object_name(name)
        else:
            # Select the only root object
            root_objects = self.root_objects()
            if len(root_objects) == 0:
                raise ObjectNotFound("root object")
            elif len(root_objects) == 1:
                return root_objects[0]
            else:
                raise AmbiguousObject("root object")

    def object_by_path(self, path: Iterable[str]) -> Object:
        path = list(path)
        if path:
            root_name = path[0]
            child_path = path[1:]

            return self.root_object(root_name).child_by_path(child_path)
        else:
            return self.device_object

    def walk(self) -> Iterator[tuple[int, Object]]:
        yield from self.device_object.walk(depth = 0)
