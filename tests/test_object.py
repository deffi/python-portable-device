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

    @pytest.mark.device
    def test_upload_download_remove_file(self, test_dir):
        content = "hello\nportable_device_api\ntest".encode()
        file_name = "upload.txt"
        assert file_name not in [child.object_name() for child in test_dir.children()]

        # Create the file
        file = test_dir.upload_file(file_name, content)
        assert file_name in [child.object_name() for child in test_dir.children()]
        assert test_dir.get_child_by_name(file_name).object_id == file.object_id

        # Download the file
        assert file.download() == content
        assert file_name in [child.object_name() for child in test_dir.children()]

        # Remove the file
        delete_result = file.delete(False)
        assert delete_result == 0
        assert file_name not in [child.object_name() for child in test_dir.children()]

        # Remove the file again (it's missing now)
        delete_result = file.delete(False)
        assert delete_result == errors.ERROR_FILE_NOT_FOUND
        assert file_name not in [child.object_name() for child in test_dir.children()]

    @pytest.mark.device
    def test_recursive_delete(self, test_dir):
        dir_name = "foo"
        assert dir_name not in [child.object_name() for child in test_dir.children()]

        subdir = test_dir.create_directory(dir_name)
        subdir.upload_file("bar", b"bar")
        assert dir_name in [child.object_name() for child in test_dir.children()]

        assert subdir.delete(False) == errors.ERROR_DIR_NOT_EMPTY
        assert dir_name in [child.object_name() for child in test_dir.children()]

        assert subdir.delete(True) == 0
        assert dir_name not in [child.object_name() for child in test_dir.children()]
