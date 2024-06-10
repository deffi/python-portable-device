from collections.abc import Iterator, Callable
from functools import cache
from portable_device_api import (PortableDeviceManager, PortableDevice, PortableDeviceContent, PortableDeviceProperties,
                                 definitions)
from typing import Self

from portable_device import Object
from portable_device.exceptions import DeviceNotFound


@cache
def _manager() -> PortableDeviceManager:
    return PortableDeviceManager.create()


class Device:
    def __init__(self, device_id: str):
        self._device_id = device_id
        self._device = PortableDevice.create()

    # Creation #################################################################

    @classmethod
    def ids(cls, refresh = True) -> Iterator[str]:
        yield from _manager().get_devices()

    @classmethod
    def all(cls, refresh = True) -> Iterator[Self]:
        for device_id in cls.ids(refresh = refresh):
            yield cls(device_id)

    @classmethod
    def by_description(cls, description: str, *,
                       refresh = True, description_map: Callable[[str], str] = str.strip) -> Self:
        if refresh:
            _manager().refresh_device_list()

        for device_id in _manager().get_devices():
            this_device_description = _manager().get_device_description(device_id)
            this_device_description = description_map(this_device_description)

            if this_device_description == description:
                return Device(device_id)
        else:
            raise DeviceNotFound(description)

    @classmethod
    def by_friendly_name(cls, friendly_name: str, *, refresh = True) -> Self:
        if refresh:
            _manager().refresh_device_list()

        for device_id in _manager().get_devices():
            if _manager().get_device_friendly_name(device_id) == friendly_name:
                return Device(device_id)
        else:
            raise DeviceNotFound(friendly_name)

    # Open #####################################################################

    def open(self):
        self._device.open(self._device_id)

    def close(self):
        self._device.close()

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
    def _content(self) -> PortableDeviceContent:
        return self._device.content()

    @property
    @cache
    def _properties(self) -> PortableDeviceProperties:
        return self._content.properties()

    @property
    @cache
    def root_object(self) -> Object:
        return Object(self, definitions.WPD_DEVICE_OBJECT_ID)

    # Object access

    def walk(self, depth = 0) -> Iterator[tuple[int, Object]]:
        yield from self.root_object.walk(depth = 0)

    # Context manager ##########################################################

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
