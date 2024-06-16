class AmbiguousObject(RuntimeError):
    def __init__(self, reference):
        self.reference = reference

    def __str__(self) -> str:
        if self.reference is None:
            return "Ambiguous root object"
        else:
            return f"Ambiguous object: {self.reference!r}"
