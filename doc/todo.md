portable_device_api:
  * Add lookup_name to PropertyKey/GUID so we don't have to import defs here?

Code TODOs

Add CLI script to pyproject.toml

Error handling:
  * Accessing a device that is not open
  * Creating a file/directory that already exists

Tests:
  * Tests for ObjectList
  * Test accessing a non-existent child (ObjectNotFound exception)
  * Can we have multiple Object instances with the same object ID?
  * Can we have multiple Device instances with the same device ID?
