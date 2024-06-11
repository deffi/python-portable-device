from datetime import datetime
import os

import pytest

from portable_device import Device


@pytest.fixture(scope = "session")
def device():
    # TODO support subdirectories or document that we don't
    device_description, base_name = os.environ["PORTABLE_DEVICE_TEST_PATH"].split("/")

    devices = list(Device.all(refresh=True))
    matching_devices = [device for device in devices if device.description == device_description]
    assert len(matching_devices) == 1
    return matching_devices[0]


@pytest.fixture(scope = "session")
def test_dir():
    # TODO duplication in parsing the string
    # TODO use device fixture instead
    device_description, base_name = os.environ["PORTABLE_DEVICE_TEST_PATH"].split("/")

    device = Device.by_description(device_description, description_map=lambda x:x)
    with device:
        device_object = device.device_object
        root = next(device_object.children())  # TODO ensure that there is only one
        base = root.get_child_by_name(base_name)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        test_dir = base.create_directory(timestamp)
        yield test_dir
        test_dir.delete()
