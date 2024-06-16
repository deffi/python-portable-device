from datetime import datetime
import os

import pytest

from portable_device import Device, Object


@pytest.fixture(scope = "session")
def device():
    # TODO support subdirectories or document that we don't
    device_description, *base_path = os.environ["PORTABLE_DEVICE_TEST_PATH"].split("/")

    devices = list(Device.all(refresh=True))
    matching_devices = [device for device in devices if device.description == device_description]
    assert len(matching_devices) == 1
    return matching_devices[0]


@pytest.fixture(scope = "module")
def test_dir() -> Object:
    # TODO duplication in parsing the string
    # TODO use device fixture instead
    device_description, *base_path = os.environ["PORTABLE_DEVICE_TEST_PATH"].split("/")

    device = Device.by_description(device_description.rstrip())
    with device:
        # device_object = device.device_object
        # children = device_object.children()
        # assert len(children) == 1
        # root = children[0]
        # base = device_object.get_child_by_path(base_name)

        # matching_root_objects = device.root_objects.by_object_name(base_name[0])
        # assert len(matching_root_objects) == 1

        base = device.object_by_path(base_path)


        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        test_dir = base.create_directory(timestamp)
        yield test_dir
        test_dir.delete(recursive=False)
