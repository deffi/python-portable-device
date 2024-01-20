from collections.abc import Iterator, Callable
from functools import cache
from portable_device_api import PortableDeviceManager, PortableDevice
from typing import Self


@cache
def _manager() -> PortableDeviceManager:
    return PortableDeviceManager.create()


class Device:
    def __init__(self, device_id: str):
        self._device_id = device_id
        self._device = PortableDevice.create()

    # Creation #################################################################

    @classmethod
    def all(cls, refresh = True) -> Iterator[Self]:
        for device_id in _manager().get_devices():
            yield cls(device_id)

    @classmethod
    def by_description(cls, description: str, *, refresh = True, description_map: Callable[[str], str] = str.strip):
        if refresh:
            _manager().refresh_device_list()

        for device_id in _manager().get_devices():
            this_device_description = _manager().get_device_description(device_id)
            this_device_description = description_map(this_device_description)

            if this_device_description == description:
                return Device(device_id)

    @classmethod
    def by_friendly_name(cls, friendly_name: str, *, refresh = True):
        if refresh:
            _manager().refresh_device_list()

        for device_id in _manager().get_devices():
            if _manager().get_device_friendly_name(device_id) == friendly_name:
                return Device(device_id)

    # Open #####################################################################

    def open(self):
        self._device.open(self._device_id)

    def close(self):
        self._device.close()

    # Properties ###############################################################

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

    # Context manager ##########################################################

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# def walk(content: PortableDeviceContent, object_id: str, depth = 0) -> Iterator[int, str]:
#     yield depth, object_id
#     for child_object_id in content.enum_objects(object_id).next(999):
#         yield from walk(content, child_object_id, depth+1)
