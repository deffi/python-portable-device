# TODO an ObjectGenerator might be better

from collections.abc import Iterator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from portable_device import Object


class ObjectList(list["Object"]):
    def object_names(self) -> Iterator[str]:
        for object_ in self:
            yield object_.object_name()
