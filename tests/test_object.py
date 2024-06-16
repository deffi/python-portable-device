from datetime import datetime
import re

from portable_device_api import errors, definitions
import pytest

from portable_device import Object

from fixtures import test_dir, device


class TestObject:
    # Properties ###############################################################

    # Object properties ########################################################

    @pytest.mark.device
    def test_supported_properties(self, test_dir: Object):
        supported_properties = test_dir.supported_properties()
        assert definitions.WPD_OBJECT_NAME in supported_properties
        assert definitions.WPD_OBJECT_CONTENT_TYPE in supported_properties
        assert definitions.WPD_OBJECT_PARENT_ID in supported_properties  # TODO getting the parent

    @pytest.mark.device
    def test_get_properties(self, test_dir):
        properties = test_dir.get_properties([definitions.WPD_OBJECT_NAME,
                                              definitions.WPD_OBJECT_CONTENT_TYPE])

        assert definitions.WPD_OBJECT_NAME in properties
        assert definitions.WPD_OBJECT_CONTENT_TYPE in properties

        assert properties[definitions.WPD_OBJECT_CONTENT_TYPE] == definitions.WPD_CONTENT_TYPE_FOLDER
        # TODO also test the content type of a file

    def test_object_name(self, test_dir: Object):
        assert re.fullmatch(r'\d\d\d\d-\d\d-\d\d_\d\d-\d\d-\d\d', test_dir.object_name())

    def test_file_name(self, test_dir: Object):
        assert re.fullmatch(r'\d\d\d\d-\d\d-\d\d_\d\d-\d\d-\d\d', test_dir.file_name())

    # Object property attributes ###############################################

    @pytest.mark.device
    def test_property_attributes(self, test_dir):
        attributes = test_dir.property_attributes(definitions.WPD_OBJECT_CONTENT_TYPE)
        assert attributes[definitions.WPD_PROPERTY_ATTRIBUTE_CAN_READ] is True
        assert attributes[definitions.WPD_PROPERTY_ATTRIBUTE_CAN_WRITE] is False

    # Object access ############################################################

    @pytest.mark.device
    def test_download(self, test_dir):
        content = b"foobarx"
        file_name = "upload.txt"
        assert file_name not in test_dir.children().object_names()

        # Create the file
        file = test_dir.upload_file(file_name, content)
        assert file_name in test_dir.children().object_orignal_file_names()
        assert test_dir.children().by_file_name(file_name).object_id == file.object_id

        # Download the file
        download = file.download(chunk_size=3)
        assert next(download) == b"foo"
        assert next(download) == b"bar"
        assert next(download) == b"x"
        with pytest.raises(StopIteration):
            next(download)
        assert file_name in test_dir.children().object_orignal_file_names()

        # Remove the file
        delete_result = file.delete(False)
        assert delete_result == 0
        assert file_name not in test_dir.children().object_names()

        # Remove the file again (it's missing now)
        delete_result = file.delete(False)
        assert delete_result == errors.ERROR_FILE_NOT_FOUND or delete_result == errors.E_MTP_INVALID_OBJECT_HANDLE
        assert file_name not in test_dir.children().object_names()

    @pytest.mark.device
    def test_download_cancel(self, test_dir):
        content = b"foobarx"
        file_name = "upload.txt"
        assert file_name not in test_dir.children().object_names()

        # Create the file
        file = test_dir.upload_file(file_name, content)
        assert file_name in test_dir.children().object_orignal_file_names()
        assert test_dir.children().by_file_name(file_name).object_id == file.object_id

        # Download the file
        download = file.download(chunk_size=3)
        assert next(download) == b"foo"
        download.close()
        assert file_name in test_dir.children().object_orignal_file_names()

        # Remove the file
        delete_result = file.delete(False)
        assert delete_result == 0
        assert file_name not in test_dir.children().object_names()

        # Remove the file again (it's missing now)
        delete_result = file.delete(False)
        assert delete_result == errors.ERROR_FILE_NOT_FOUND or delete_result == errors.E_MTP_INVALID_OBJECT_HANDLE
        assert file_name not in test_dir.children().object_names()

    # TODO test_delete

    @pytest.mark.device
    def test_recursive_delete(self, test_dir):
        dir_name = "foo"
        assert dir_name not in test_dir.children().object_names()

        subdir = test_dir.create_directory(dir_name)
        subdir.upload_file("bar", b"bar")
        assert dir_name in test_dir.children().object_names()

        assert subdir.delete(False) == errors.ERROR_DIR_NOT_EMPTY
        assert dir_name in test_dir.children().object_names()

        assert subdir.delete(True) == 0
        assert dir_name not in test_dir.children().object_names()

    @pytest.mark.device
    def test_move_file(self, test_dir):
        file_name = "file"
        content = b"foobar"

        source = test_dir.create_directory("source")
        target = test_dir.create_directory("target")

        file = source.upload_file(file_name, content)
        assert file_name in source.children().object_names()
        assert file_name not in target.children().object_names()

        file.move_into(target)
        assert file_name not in source.children().object_names()
        assert file_name in target.children().object_names()

        assert target.children().by_file_name(file_name).object_id == file.object_id
        assert file.download_all() == content

        source.delete(recursive=True)
        target.delete(recursive=True)

    # TODO test_move_directory

    # Parent ###################################################################

    def test_parent(self, test_dir):
        subdirectory = test_dir.create_directory("subdirectory")
        assert subdirectory.parent().object_id == test_dir.object_id

    def test_parent_of_root(self, device):
        with device:
            root = device.root_objects()[0]
            assert root.parent().object_id == device.device_object.object_id

    def test_parent_of_device_object(self, device):
        with device:
            assert device.device_object.parent() is None

    # Children #################################################################

    # TODO test_children
    # TODO test_child_by_path
    # TODO test_walk

    @pytest.mark.device
    def test_create_remove_directory(self, test_dir):
        dir_name = "test_dir"
        assert dir_name not in test_dir.children().object_names()

        directory = test_dir.create_directory(dir_name)
        assert dir_name in test_dir.children().object_names()

        # Remove the directory
        delete_result = directory.delete(False)
        assert delete_result == 0
        assert dir_name not in test_dir.children().object_names()

        # Remove the directory again (it's missing now)
        delete_result = directory.delete(False)
        # TODO own error reporting
        assert delete_result == errors.ERROR_FILE_NOT_FOUND or delete_result == errors.E_MTP_INVALID_OBJECT_HANDLE
        assert dir_name not in test_dir.children().object_names()

    @pytest.mark.device
    def test_upload_download_remove_file(self, test_dir):
        content = "hello\nportable_device_api\ntest".encode()
        file_name = "upload.txt"
        assert file_name not in test_dir.children().object_names()

        # Create the file
        file = test_dir.upload_file(file_name, content)
        assert file_name in test_dir.children().object_orignal_file_names()
        assert test_dir.children().by_file_name(file_name).object_id == file.object_id

        # Download the file
        assert file.download_all() == content
        assert file_name in test_dir.children().object_orignal_file_names()

        # Remove the file
        delete_result = file.delete(False)
        assert delete_result == 0
        assert file_name not in test_dir.children().object_names()

        # Remove the file again (it's missing now)
        delete_result = file.delete(False)
        assert delete_result == errors.ERROR_FILE_NOT_FOUND or delete_result == errors.E_MTP_INVALID_OBJECT_HANDLE
        assert file_name not in test_dir.children().object_names()
