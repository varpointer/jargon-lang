from enum import Enum

BasicType = Enum("BasicType", [
    "INT", "FLOAT", "STR", "CHAR", "BOOL", "VOID"
])

class ArrayType:
    def __init__(self, element_type):
        self.element_type: Type = element_type
    def __repr__(self):
        return f"ARR of {self.element_type}"

class Type:
    def __init__(self, type_: BasicType | ArrayType):
        self.value = type_
    def __repr__(self):
        return f"<{self.value}>"
