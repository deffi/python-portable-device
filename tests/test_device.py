import pytest

from portable_device import Device, Object
from fixtures import device


class TestDevice:
    def test_construction(self):
        # Pretty useless, and most likely doesn't exist
        device = Device("foobar")
        assert device.device_id == "foobar"

    # Creation #################################################################

    def test_all(self):
        devices = Device.all()
        assert all([isinstance(device, Device) for device in devices])

    @pytest.mark.device
    def test_by_description(self, device):
        other = Device.by_description(device.description, ignore_trailing_space=False)
        assert other.device_id == device.device_id

    @pytest.mark.device
    def test_by_friendly_name(self, device):
        other = Device.by_friendly_name(device.friendly_name)
        assert other.device_id == device.device_id

    # Open #####################################################################

    @pytest.mark.device
    def test_open_close(self, device):
        device.open()
        device.close()

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
    def test_root_object(self, device):
        # TODO document what happens if it's not open, or detect and throw exception
        with device:
            assert isinstance(device.device_object, Object)

    @pytest.mark.device
    def test_walk(self, device):
        # TODO test, but limit or it might take a long time
        pass

    # Context manager ##########################################################

    @pytest.mark.device
    def test_context_manager(self, device):
        with device:
            pass
