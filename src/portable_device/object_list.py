# TODO an ObjectGenerator might be better

from collections.abc import Iterator
from typing import TYPE_CHECKING, Self

from comtypes.automation import VT_LPWSTR

from portable_device_api import (definitions, PortableDeviceKeyCollection, PropertyKey, PortableDeviceValues,
                                 PortableDevicePropVariantCollection, PropVariant, errors)

if TYPE_CHECKING:
    from portable_device import Object


class ObjectList(list["Object"]):
    def object_names(self) -> Iterator[str]:
        for object_ in self:
            yield object_.object_name()

    # TODO rename to file_names everywhere?
    def object_orignal_file_names(self) -> Iterator[str]:
        for object_ in self:
            yield object_.file_name()

    def by_object_name(self, object_name: str) -> "Object":
        matching_objects = [o for o in self if o.object_name() == object_name]
        assert len(matching_objects) == 1
        return matching_objects[0]

    def by_file_name(self, file_name: str) -> "Object":
        matching_objects = [o for o in self if o.file_name() == file_name]
        assert len(matching_objects) == 1
        return matching_objects[0]

    # TODO is this faster than deleting individually?
    # TODO expected result is [0] * len(object_ids)
    def delete(self, recursive: bool) -> list[int]:
        # TODO code duplication with Object._delete, factor out
        object_ids_pvc = PortableDevicePropVariantCollection.create()
        for object_ in self:
            object_ids_pvc.add(PropVariant.create(VT_LPWSTR, object_.object_id))

        if recursive:
            flags = definitions.DELETE_OBJECT_OPTIONS.PORTABLE_DEVICE_DELETE_WITH_RECURSION
        else:
            flags = definitions.DELETE_OBJECT_OPTIONS.PORTABLE_DEVICE_DELETE_NO_RECURSION

        # TODO will fail for empty lists
        # TODO assert that all contents are the same (or group)
        delete_result = self[0]._content.delete(flags, object_ids_pvc)
        assert delete_result.get_count() == len(self)
        return [errors.to_hresult(delete_result.get_at(i).value) for i in range(delete_result.get_count())]

    def move_into(self, target: "Object"):
        # TODO multi-move
        object_ids_pvc = PortableDevicePropVariantCollection.create()
        for object_ in self:
            object_ids_pvc.add(PropVariant.create(VT_LPWSTR, object_.object_id))

        # TODO assert that all contents are the same (or group)
        move_result = self[0]._content.move(object_ids_pvc, target.object_id)
        assert move_result.get_count() == len(self)
        return [errors.to_hresult(move_result.get_at(i).value) for i in range(move_result.get_count())]
