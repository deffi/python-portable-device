import re

from portable_device_api import errors
import pytest

from portable_device import Object

from fixtures import test_dir


class TestObject:
    def test_object_name(self, test_dir: Object):
        assert re.fullmatch(r'\d\d\d\d-\d\d-\d\d_\d\d-\d\d-\d\d', test_dir.object_name())

    @pytest.mark.device
    def test_create_remove_dir(self, test_dir):
        dir_name = "test_dir"
        assert dir_name not in [child.object_name() for child in test_dir.children()]

        directory = test_dir.create_directory(dir_name)
        assert dir_name in [child.object_name() for child in test_dir.children()]

        # Remove the directory
        delete_result = directory.delete(False)
        assert delete_result == 0
        assert dir_name not in [child.object_name() for child in test_dir.children()]

        # Remove the directory again (it's missing now)
        delete_result = directory.delete(False)
        # TODO own error reporting
        assert delete_result == errors.ERROR_FILE_NOT_FOUND
        assert dir_name not in [child.object_name() for child in test_dir.children()]
