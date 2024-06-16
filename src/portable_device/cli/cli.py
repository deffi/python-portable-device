import sys

import cyclopts
from portable_device_api import definitions

from portable_device import Device
from portable_device.exceptions import DeviceNotFound

cyclopts_app = cyclopts.App()


@cyclopts_app.command()
def devices():
    print(f"{'Description':<25}{'Friendly name':<25}{'Manufacturer':<25}")
    print(f"{'-----------':<25}{'-------------':<25}{'------------':<25}")

    # TODO get interesting properties
    for d in Device.all():
        print(f"{d.description!r:<25}{d.friendly_name:<25}{d.manufacturer:<25}")


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


@cyclopts_app.command()
def ls(device_description: str):
    try:
        with Device.by_description(device_description) as device:
            # TODO no fixed width
            print(f"{'Object ID':<55}{'Content type':<42}{'Object name':<40}{'Original file name':<45}")
            print(f"{'---------':<55}{'------------':<42}{'-----------':<40}{'------------------':<45}")

            for depth, object_ in device.walk():
                oid = object_._object_id

                content_type, object_name, file_name = object_.get_properties([
                    definitions.WPD_OBJECT_CONTENT_TYPE,
                    definitions.WPD_OBJECT_NAME,
                    definitions.WPD_OBJECT_ORIGINAL_FILE_NAME,
                ])
                content_type = definitions.reverse_lookup.get(content_type, content_type)

                print(f"{'  ' * depth}{oid:<55}{content_type:<42}{object_name:<40}{file_name:<45}")
                # _dump_properties(properties, oid, depth + 1)
    except DeviceNotFound as e:
        print(e)
        return 1


if __name__ == "__main__":
    sys.exit(cyclopts_app())
