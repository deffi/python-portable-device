import re

from portable_device_api import errors
import pytest

from portable_device import Object

from fixtures import test_dir


class TestObjectList:
    @pytest.mark.device
    def test_delete(self, test_dir):
        dir_names = ["foo", "bar"]
        for dir_name in dir_names:
            assert dir_name not in test_dir.children().object_names()

        for dir_name in dir_names:
            test_dir.create_directory(dir_name)
        for dir_name in dir_names:
            assert dir_name in test_dir.children().object_names()

        # Remove the directories
        children = test_dir.children()
        delete_result = children.delete(False)
        assert delete_result == [0] * len(dir_names)
        for dir_name in dir_names:
            assert dir_name not in test_dir.children().object_names()

        # Remove the directories again (they're missing now)
        delete_result = children.delete(False)
        # TODO own error reporting
        assert delete_result == [errors.ERROR_FILE_NOT_FOUND] * len(dir_names) or delete_result == [errors.E_MTP_INVALID_OBJECT_HANDLE] * len(dir_names)
        for dir_name in dir_names:
            assert dir_name not in test_dir.children().object_names()
