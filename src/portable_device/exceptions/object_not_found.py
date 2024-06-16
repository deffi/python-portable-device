class ObjectNotFound(RuntimeError):
    def __init__(self, reference):
        self.reference = reference

    def __str__(self) -> str:
        if self.reference is None:
            return f"Root object not found"
        else:
            return f"Object not found: {self.reference!r}"
