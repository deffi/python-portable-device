class DeviceNotFound(RuntimeError):
    def __init__(self, reference):
        self.reference = reference

    def __str__(self) -> str:
        return f"Device not found: {self.reference!r}"
