from itertools import islice

import pytest

from portable_device import Device, Object
from portable_device.exceptions import DeviceNotFound, AmbiguousDevice

from fixtures import device


class TestDevice:
    def test_construction(self):
        # Most likely doesn't exist
        device = Device("foobar")
        assert device.device_id == "foobar"

    # Creation #################################################################

    def test_all(self):
        devices = Device.all()
        for device in devices:
            assert isinstance(device, Device)

    @pytest.mark.device
    def test_find(self, device):
        other = Device.find(lambda d: d.device_id == device.device_id, repr(device.device_id))
        assert isinstance(other, Device)
        assert other.device_id == device.device_id

    def test_find_not_found(self):
        with pytest.raises(DeviceNotFound, match = r"Device not found: none"):
            Device.find(lambda device: False, "none")

    @pytest.mark.device
    @pytest.mark.devices
    def test_find_ambiguous(self):
        with pytest.raises(AmbiguousDevice, match = r"Ambiguous device: all"):
            Device.find(lambda device: True, "all")

    @pytest.mark.device
    def test_by_description(self, device):
        other = Device.by_description(device.description, ignore_trailing_space=False)
        assert isinstance(other, Device)
        assert other.device_id == device.device_id

    def test_by_description_not_found(self):
        with pytest.raises(DeviceNotFound, match = r"Device not found: 'mutakirorikatum'"):
            Device.by_description("mutakirorikatum", ignore_trailing_space=False)

    @pytest.mark.device
    def test_by_friendly_name(self, device):
        other = Device.by_friendly_name(device.friendly_name)
        assert isinstance(other, Device)
        assert other.device_id == device.device_id

    @pytest.mark.device
    def test_by_friendly_name_not_found(self, device):
        with pytest.raises(DeviceNotFound, match = r"Device not found: 'Mutakirorikatum'"):
            Device.by_friendly_name("Mutakirorikatum")

    # Open #####################################################################

    @pytest.mark.device
    def test_open_close(self, device):
        device.open()
        device.close()

    # Context manager ##########################################################

    @pytest.mark.device
    def test_context_manager(self, device):
        with device:
            pass

    # Properties ###############################################################

    @pytest.mark.device
    def test_device_id(self, device):
        assert isinstance(device.device_id, str)
        assert device.device_id

    @pytest.mark.device
    def test_description(self, device):
        assert isinstance(device.description, str)
        assert device.description

    @pytest.mark.device
    def test_friendly_name(self, device):
        assert isinstance(device.friendly_name, str)
        assert device.friendly_name

    @pytest.mark.device
    def test_manufacturer(self, device):
        assert isinstance(device.manufacturer, str)
        assert device.manufacturer

    # Object access ############################################################

    @pytest.mark.device
    def device_object(self, device):
        device_object = device.device_object
        assert isinstance(device_object, Object)

    @pytest.mark.device
    def test_root_objects(self, device):
        # TODO document what happens if it's not open, or detect and throw exception
        with device:
            for object_ in device.root_objects():
                assert isinstance(object_, Object)

    @pytest.mark.device
    def test_root_object_by_name(self, device):
        with device:
            root_object = device.root_objects()[0]
            other = device.root_object(root_object.object_name())
            assert other.object_id == root_object.object_id

    @pytest.mark.skip
    @pytest.mark.device
    def test_root_object_unique(self, device):
        # We can't test this, as this might have any of the following results,
        # depending on the device:
        #   * Returns an object (device with a single root object)
        #   * Raises ObjectNotFound (device without a root object, not sure if
        #     this even exists)
        #   * Raises AmbiguousObject (device with multiple root objects)
        device.root_object("")

    @pytest.mark.device
    def test_object_by_path_device_object(self, device):
        with device:
            assert device.object_by_path([]).object_id == device.device_object.object_id

    @pytest.mark.device
    def test_object_by_path_root_object(self, device):
        with device:
            root_object = device.root_objects()[0]
            assert device.object_by_path([root_object.object_name()]).object_id == root_object.object_id

    @pytest.mark.device
    def test_walk(self, device):
        with device:
            # Limit to 10 objects, walking the whole tree might take a long time
            for depth, object_ in islice(device.walk(), 0, 10):
                assert isinstance(object_, Object)
