import typer

from portable_device import Device

typer_app = typer.Typer()


@typer_app.command()
def devices():
    print(f"{'Description':<25}{'Friendly name':<25}{'Manufacturer':<25}")
    print(f"{'-----------':<25}{'-------------':<25}{'------------':<25}")

    for d in Device.all():
        print(f"{d.description!r:<25}{d.friendly_name:<25}{d.manufacturer:<25}")


@typer_app.command()
def ls():
    ...


if __name__ == "__main__":
    typer_app()


# def _dump_property_attributes(properties: PortableDeviceProperties, object_id: str, property_key: PropertyKey,
#                               depth: int) -> None:
#     # Some properties don't support this
#     with ignore_com_error(errors.ERROR_NOT_SUPPORTED):
#         attributes = properties.get_property_attributes(object_id, property_key)
#         for j in range(attributes.get_count()):
#             attribute_key, attribute_value = attributes.get_at(j)
#             attribute_key = defs.reverse_lookup.get(attribute_key, str(attribute_key))
#             print(f"{'  ' * (depth + 2)}{attribute_key} = {attribute_value.value}")
#
#
# def _dump_properties(properties: PortableDeviceProperties, object_id: str, depth: int) -> None:
#     supported_properties = properties.get_supported_properties(object_id)
#     all_property_values = properties.get_values(object_id, supported_properties)
#     for i in range(supported_properties.get_count()):
#         property_key = supported_properties.get_at(i)
#
#         propvariant_value = all_property_values.get_value(property_key)
#         # _, propvariant_value = all_property_values.get_at(i)
#         property_value = propvariant_value.value
#         if isinstance(property_value, GUID):
#             property_value = defs.reverse_lookup.get(property_value, property_value)
#
#         print(
#             f"{'  ' * (depth + 1)}{defs.reverse_lookup.get(property_key, str(property_key))} = {property_value}")
#
#         # _dump_property_attributes(properties, object_id, property_key, depth + 1)
#
#
# def _ls(device_description: str) -> None:
#     manager = PortableDeviceManager.create()
#     device_id = [device_id for device_id in manager.get_devices() if
#                  manager.get_device_description(device_id) == device_description][0]
#
#     device = PortableDevice.create()
#     device.open(device_id)
#     content = device.content()
#     properties = content.properties()
#
#     object_id = defs.WPD_DEVICE_OBJECT_ID
#
#     print(f"{'Object ID':<55}{'Content type':<42}{'Object name'!s:<40}{'Original file name'!s:<45}")
#
#     for depth, oid in walk(content, object_id):
#         keys = PortableDeviceKeyCollection.create()
#         keys.add(defs.WPD_OBJECT_NAME)
#         keys.add(defs.WPD_OBJECT_ORIGINAL_FILE_NAME)
#         keys.add(defs.WPD_OBJECT_CONTENT_TYPE)
#         property_values = properties.get_values(oid, keys)
#
#         try:
#             content_type = property_values.get_guid_value(defs.WPD_OBJECT_CONTENT_TYPE)
#             content_type = defs.reverse_lookup.get(content_type, content_type)
#         except COMError:
#             content_type = None
#         try:
#             object_name = property_values.get_string_value(defs.WPD_OBJECT_NAME)
#         except COMError:
#             object_name = None
#         try:
#             original_file_name = property_values.get_string_value(defs.WPD_OBJECT_ORIGINAL_FILE_NAME)
#         except COMError:
#             original_file_name = None
#
#         print(f"{'  ' * depth}{oid:<55}{content_type!s:<42}{object_name!s:<40}{original_file_name!s:<45}")
#         _dump_properties(properties, oid, depth + 1)
