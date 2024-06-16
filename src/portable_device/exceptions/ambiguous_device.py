class AmbiguousDevice(RuntimeError):
    def __init__(self, reference):
        self.reference = reference

    def __str__(self) -> str:
        return f"Ambiguous device: {self.reference!r}"
