import os
import pytest

from portable_device import Device


@pytest.fixture(scope = "session")
def device():
    device_description, base_name = os.environ["PORTABLE_DEVICE_TEST_PATH"].split("/")

    devices = list(Device.all(refresh=True))
    matching_devices = [device for device in devices if device.description == device_description]
    assert len(matching_devices) == 1
    return matching_devices[0]
