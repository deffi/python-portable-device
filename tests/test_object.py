import re

from portable_device import Object

from fixtures import test_dir


class TestObject:
    def test_object_name(self, test_dir: Object):
        assert re.fullmatch(r'\d\d\d\d-\d\d-\d\d_\d\d-\d\d-\d\d', test_dir.object_name())
