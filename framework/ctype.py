from abc import ABC, abstractmethod


class CType(ABC):
    _types = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        CType._types.append(cls)

    def __init__(self, declaration: str):
        self.declaration = declaration

    def declare(self, name: str) -> str:
        return f"{self.declaration} {name}"

    @classmethod
    @abstractmethod
    def supports(cls, declaration: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def generate_call(
        self,
        function_name: str,
        arguments: str,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def serialize(self, expression: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def parse(self, value: str):
        raise NotImplementedError


class VoidType(CType):
    @classmethod
    def supports(cls, declaration: str) -> bool:
        return declaration == "void"

    def __init__(self, declaration: str):
        super().__init__(declaration)

    def generate_call(
        self,
        function_name: str,
        arguments: str,
    ) -> str:
        return f"{function_name}({arguments});"

    def serialize(self, expression: str) -> str:
        return 'printf("RETURN:VOID\\n");'

    def parse(self, value: str):
        return None


class IntegerType(CType):
    FORMATS = {
        "char": "%d",
        "signed char": "%d",
        "unsigned char": "%u",
        "short": "%d",
        "unsigned short": "%u",
        "int": "%d",
        "unsigned int": "%u",
        "long": "%ld",
        "unsigned long": "%lu",
        "long long": "%lld",
        "unsigned long long": "%llu",
        "size_t": "%zu",
        "ssize_t": "%zd",
    }

    @classmethod
    def supports(cls, declaration: str) -> bool:
        return declaration in cls.FORMATS

    def __init__(self, declaration: str):
        if not self.supports(declaration):
            raise ValueError(f"unsupported integer type: {declaration}")

        super().__init__(declaration)

    def generate_call(
        self,
        function_name: str,
        arguments: str,
    ) -> str:
        return f"{self.declaration} result = " f"{function_name}({arguments});"

    def serialize(self, expression: str) -> str:
        fmt = self.FORMATS[self.declaration]

        return f'printf("RETURN:{fmt}\\n", {expression});'

    def parse(self, value: str):
        return int(value)


class PointerType(CType):
    @classmethod
    def supports(cls, declaration: str) -> bool:
        return "*" in declaration

    def __init__(self, declaration: str):
        super().__init__(declaration)

    def generate_call(
        self,
        function_name: str,
        arguments: str,
    ) -> str:
        return f"{self.declaration} result = " f"{function_name}({arguments});"

    def serialize(self, expression: str) -> str:
        return (
            f"if ({expression} == NULL) "
            f'printf("RETURN:NULL\\n"); '
            f"else "
            f'printf("RETURN:%p\\n", (void *){expression});'
        )

    def parse(self, value: str):
        return value


def parse_ctype(declaration: str) -> CType:
    declaration = declaration.strip()

    for type_class in CType._types:
        if type_class.supports(declaration):
            return type_class(declaration)

    raise ValueError(f"unsupported C type: {declaration}")
