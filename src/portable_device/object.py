from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from portable_device import Device


class Object:
    def __init__(self, device: Device, object_id: str):
        self._device = device
        self._object_id = object_id

        self._content = self._device._content
        self._properties = self._device._properties

    @property
    def object_id(self) -> str:
        return self._object_id

    def children(self) -> Iterator[Self]:
        enum_object_ids = self._content.enum_objects(self._object_id)

        while object_ids := enum_object_ids.next(1):
            for object_id in object_ids:
                yield Object(self._device, object_id)

    def walk(self, *, depth = 0) -> Iterator[int, Self]:
        yield depth, self

        for child in self.children():
            yield from child.walk(depth = depth + 1)
