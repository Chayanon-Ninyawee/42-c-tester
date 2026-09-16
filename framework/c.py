import re
import subprocess
import tempfile
import textwrap
from pathlib import Path

from .color import Color, color
from .ctype import PointerType, parse_ctype
from .project import FunctionConfig, Project
from .result import AssertionFailure, UnexpectedResult
from .utils import format_buffer_diff, run_debug_process

MALLOC_STRIKE_DIR = Path(__file__).with_name("malloc_strike")
MALLOC_STRIKE_SOURCE = MALLOC_STRIKE_DIR / "malloc_strike.c"
MALLOC_STRIKE_HEADER = MALLOC_STRIKE_DIR / "malloc_strike.h"
MALLOC_STRIKE_POISON = b"\xaa"

PROTOCOL_FD = 39


class CBuffer:
    def __init__(
        self,
        data: bytes = b"",
        size: int | None = None,
        name: str = "buffer",
        type: str = "unsigned char",
    ):
        if size is None:
            size = len(data)

        if size < 0:
            raise ValueError("buffer size cannot be negative")

        if len(data) > size:
            raise ValueError(
                f"buffer data ({len(data)} bytes) "
                f"exceeds buffer size ({size} bytes)"
            )

        self.data = data
        self.size = size
        self.name = name
        self.type = parse_ctype(type)

    def __repr__(self):
        return self.name

    def generate(self):
        if self.size <= 0:
            raise ValueError("zero-sized C buffers are not supported")

        values = ", ".join(f"0x{byte:02x}" for byte in self.data)

        return self.type.generate_array(
            self.name,
            self.size,
            values,
        )

    def offset(self, offset: int):
        return CBufferOffset(self, offset)


class CBufferOffset:
    def __init__(self, buffer: CBuffer, offset: int):
        if offset < 0 or offset > buffer.size:
            raise ValueError(
                f"buffer offset {offset} is outside buffer " f"of size {buffer.size}"
            )

        self.buffer = buffer
        self.offset = offset

    @property
    def name(self):
        return f"{self.buffer.name} + {self.offset}"

    def __repr__(self):
        return f"{self.buffer.name}.offset({self.offset})"


def get_buffer(argument):
    if isinstance(argument, CBuffer):
        return argument

    if isinstance(argument, CBufferOffset):
        return argument.buffer

    return None


class CVariable:
    def __init__(
        self,
        context,
        type: str,
        value=None,
        name: str = "variable",
    ):
        if not isinstance(type, str):
            raise TypeError("variable type must be a string")

        if not name.isidentifier():
            raise ValueError(f"variable name must be a valid C identifier: {name!r}")

        self.context = context
        self.type = parse_ctype(type)
        self.value = value
        self.name = name

    def __repr__(self):
        return f"variable({self.name})"

    def generate(self):
        value = None

        if self.value is not None:
            value = generate_argument(self.value)

        return self.type.generate_declaration(
            self.name,
            value,
        )

    def pointer(self):
        return CPointer(self)


class CStruct:
    def __init__(
        self,
        context,
        type: str,
        fields: dict[str, object],
        name: str = "structure",
    ):
        if not isinstance(type, str):
            raise TypeError("struct type must be a string")

        if not name.isidentifier():
            raise ValueError(
                f"struct variable name must be a valid C identifier: {name!r}"
            )

        if not isinstance(fields, dict):
            raise TypeError("struct fields must be a dictionary")

        for field_name in fields:
            if not isinstance(field_name, str):
                raise TypeError("struct field names must be strings")

            if not field_name.isidentifier():
                raise ValueError(
                    f"struct field name must be a valid "
                    f"C identifier: {field_name!r}"
                )

        self.context = context
        self.type = type.strip()
        self.fields = fields
        self.name = name

    def __repr__(self):
        return f"struct({self.name})"

    def generate(self):
        if not self.fields:
            return f"{self.type} {self.name} = {{}};"

        values = []

        for field, value in self.fields.items():
            values.append(f".{field} = {generate_argument(value)}")

        initializer = ", ".join(values)

        return f"{self.type} {self.name} = {{ {initializer} }};"

    def pointer(self):
        return CPointer(self)


class CPointer:
    def __init__(self, variable):
        if not isinstance(variable, (CVariable, CStruct)):
            raise TypeError("pointer requires a CVariable or CStruct")

        self.variable = variable

    @property
    def name(self):
        return f"&{self.variable.name}"

    def __repr__(self):
        return f"{self.variable.name}.pointer()"


class CFileDescriptor:
    def __init__(self, context, fd: int):
        if fd < 3:
            raise ValueError("custom file descriptor must be >= 3")

        if fd == PROTOCOL_FD:
            raise ValueError(
                f"file descriptor {PROTOCOL_FD} is reserved for the framework"
            )

        self.context = context
        self.fd = fd

    def __repr__(self):
        return f"fd({self.fd})"


class CCallback:
    def __init__(
        self,
        context,
        name: str,
        returns: str,
        args: list[tuple[str, str]],
        body: str,
    ):
        if not name.isidentifier():
            raise ValueError(f"callback name must be a valid C identifier: {name!r}")

        if not args:
            args = []

        for argument in args:
            if not isinstance(argument, tuple) or len(argument) != 2:
                raise TypeError("callback arguments must be (type, name) tuples")

            argument_type, argument_name = argument

            if not isinstance(argument_type, str):
                raise TypeError("callback argument type must be a string")

            if not isinstance(argument_name, str):
                raise TypeError("callback argument name must be a string")

            if not argument_name.isidentifier():
                raise ValueError(
                    f"callback argument name must be a valid "
                    f"C identifier: {argument_name!r}"
                )

        self.context = context
        self.name = name
        self.returns = returns
        self.args = args
        self.body = body

    def generate(self):
        arguments = ", ".join(
            f"{argument_type} {argument_name}"
            for argument_type, argument_name in self.args
        )

        if not arguments:
            arguments = "void"

        body = textwrap.indent(
            self.body.strip(),
            "    ",
        )

        return (
            f"static {self.returns} {self.name}({arguments})\n"
            "{\n"
            f"{body}\n"
            "}"
        )

    def __repr__(self):
        return self.name


class Capture:
    def __init__(
        self,
        kind,
        size=None,
        fields=None,
    ):
        self.kind = kind
        self.size = size
        self.fields = fields or {}
        self.children = []

    @classmethod
    def buffer(cls, size):
        if size < 0:
            raise ValueError("capture buffer size cannot be negative")

        return cls("buffer", size)

    @classmethod
    def pointer_raw(cls):
        return cls("pointer_raw")

    @classmethod
    def pointer_array(cls, size):
        if size <= 0:
            raise ValueError("pointer array size must be positive")

        return cls("pointer_array", size)

    @classmethod
    def struct(cls, fields):
        if not isinstance(fields, dict):
            raise TypeError("struct capture fields must be a dictionary")

        for field_name, capture in fields.items():
            if not isinstance(field_name, str):
                raise TypeError("struct capture field names must be strings")

            if not field_name.isidentifier():
                raise ValueError(
                    f"struct capture field name must be a valid "
                    f"C identifier: {field_name!r}"
                )

            if not isinstance(capture, Capture):
                raise TypeError(
                    f"struct capture field {field_name!r} "
                    "must be a Capture"
                )

        return cls(
            "struct",
            fields=fields,
        )

    def child(self, capture):
        if not isinstance(capture, Capture):
            raise TypeError("capture child must be a Capture")

        if self.kind in ("buffer", "pointer_raw", "struct"):
            raise TypeError(f"{self.kind} captures cannot have children")

        if self.kind == "pointer_array":
            if len(self.children) >= self.size:
                raise ValueError(f"pointer array already has {self.size} children")

        self.children.append(capture)

        return self


class CaptureResult:
    def __init__(
        self,
        kind,
        data=None,
        children=None,
        count=None,
        fields=None,
    ):
        self.kind = kind
        self.data = data
        self.children = children or []
        self.count = count
        self.fields = fields or {}

    @property
    def is_null(self):
        return self.kind == "null"

    def __repr__(self):
        if self.kind == "buffer":
            return f"CaptureResult.buffer({len(self.data)})"

        if self.kind == "pointer_raw":
            return f"CaptureResult.pointer_raw({self.data!r})"

        if self.kind == "null":
            return "CaptureResult.null()"

        if self.kind == "struct":
            return (
                "CaptureResult.struct("
                f"{len(self.fields)} fields)"
            )

        return f"CaptureResult.{self.kind}({len(self.children)} children)"


class Assert:
    def __init__(
        self,
        kind,
        expected=None,
        message=None,
    ):
        self.kind = kind
        self.expected = expected
        self.message = message
        self.children = []
        self.fields = {}

    @classmethod
    def buffer_equals(cls, expected, message=None):
        if not isinstance(expected, bytes):
            raise TypeError("buffer assertion expects bytes")

        return cls("buffer", expected, message)

    @classmethod
    def pointer_equals(cls, expected, message=None):
        if not isinstance(
            expected,
            (CBuffer, CBufferOffset, CVariable, CStruct, str),
        ):
            raise TypeError(
                "pointer assertion expects a CBuffer, "
                "CBufferOffset, CVariable, CStruct, or pointer string"
            )

        return cls("pointer_raw", expected, message)

    @classmethod
    def is_null_pointer(cls, message=None):
        return cls("pointer_raw", None, message)

    @classmethod
    def is_not_null_pointer(cls, message=None):
        return cls("pointer_raw", "NOT_NULL", message)

    @classmethod
    def pointer_array(cls, message=None):
        return cls("pointer_array", message=message)

    @classmethod
    def struct(cls, fields, message=None):
        if not isinstance(fields, dict):
            raise TypeError("struct assertion fields must be a dictionary")

        for field_name, assertion in fields.items():
            if not isinstance(field_name, str):
                raise TypeError("struct assertion field names must be strings")

            if not field_name.isidentifier():
                raise ValueError(
                    f"struct assertion field name must be a valid "
                    f"C identifier: {field_name!r}"
                )

            if not isinstance(assertion, Assert):
                raise TypeError(
                    f"struct assertion field {field_name!r} "
                    "must be an Assert"
                )

        result = cls(
            "struct",
            message=message,
        )

        result.fields = fields

        return result

    def child(self, assertion):
        if not isinstance(assertion, Assert):
            raise TypeError("assertion child must be an Assert")

        if self.kind in ("buffer", "pointer_raw", "struct"):
            raise TypeError(f"{self.kind} assertions cannot have children")

        self.children.append(assertion)

        return self


class FunctionPointerType:
    def __init__(self, returns, args):
        self.returns = returns
        self.args = args

    @property
    def declaration(self):
        arguments = ", ".join(self.args)

        if not arguments:
            arguments = "void"

        return f"{self.returns} (*)({arguments})"


def parse_function_pointer_type(type_string):
    match = re.fullmatch(
        r"\s*(.+?)\s*\(\s*\*\s*\)\s*\((.*)\)\s*",
        type_string,
    )

    if match is None:
        return None

    returns = match.group(1).strip()
    args = match.group(2).strip()

    if not args or args == "void":
        arguments = []
    else:
        arguments = [argument.strip() for argument in args.split(",")]

    return returns, arguments


class CFunction:
    def __init__(
        self,
        context,
        name: str,
        returns: str = "int",
        args: list[str] | None = None,
        headers: list[str] | None = None,
        link: list[str] | None = None,
        err_flags: bool = True,
    ):
        self.context = context
        self.name = name

        self.return_type = parse_ctype(returns)

        self.arg_types = []

        for arg in args or []:
            function_pointer = parse_function_pointer_type(arg)

            if function_pointer is not None:
                returns_type, callback_args = function_pointer

                self.arg_types.append(
                    FunctionPointerType(
                        returns_type,
                        callback_args,
                    )
                )
            else:
                self.arg_types.append(parse_ctype(arg))

        self.headers = headers or []
        self.link = link or []
        self.err_flags = err_flags

    def __call__(self, *arguments):
        return self.context.call(
            self,
            *arguments,
        )


class CCallResult:
    def __init__(
        self,
        context,
        function: CFunction,
        arguments,
    ):
        self.context = context
        self.function = function
        self.arguments = arguments

        self.executed = False

        self.value = None
        self.return_type = function.return_type
        self.stdout = b""
        self.stderr = b""
        self.fd_outputs = {}
        self.returncode = None

        self.buffers = {}
        self.pointer_values = {}
        self.variables = {}

        self.malloc_count = 0
        self.malloc_sizes = []

        self._return_capture = None
        self.return_capture = None

        self.failures: list[str] = []

    def capture_return(self, capture: Capture):
        if self.executed:
            raise RuntimeError("cannot configure a call after it has been executed")

        if not isinstance(self.return_type, PointerType):
            raise TypeError(f"{self.function.name} does not return a pointer")

        if not isinstance(capture, Capture):
            raise TypeError("return capture must be a Capture")

        self._return_capture = capture

        return self

    def run(self):
        if self.executed:
            raise RuntimeError("call has already been executed")

        self.context._execute(self)

        self.executed = True

        return self

    def _require_run(self):
        if not self.executed:
            raise RuntimeError(
                f"{self.function.name} has not been executed; "
                "call .run() first"
            )

    def _resolve_pointer(self, expected):
        if expected is None:
            return None

        if isinstance(expected, CBufferOffset):
            base = self.pointer_values.get(expected.buffer.name)

            if base is None:
                raise RuntimeError(
                    f"buffer '{expected.buffer.name}' pointer "
                    "was not captured"
                )

            return hex(int(base, 16) + expected.offset)

        if isinstance(expected, (CBuffer, CVariable, CStruct)):
            pointer = self.pointer_values.get(expected.name)

            if pointer is None:
                raise RuntimeError(
                    f"pointer for '{expected.name}' "
                    "was not captured"
                )

            return pointer

        return expected

    def _assert_capture(
        self,
        actual,
        assertion,
        path,
    ):
        def fail(message):
            if assertion.message:
                message = f"{assertion.message}: {message}"

            self.failures.append(f"{path}: {message}")

        if assertion.kind == "buffer":
            if actual.kind == "null":
                fail("expected buffer, received NULL")
                return

            if actual.kind != "buffer":
                fail(f"expected buffer, received {actual.kind}")
                return

            if actual.data != assertion.expected:
                diff = format_buffer_diff(
                    assertion.expected,
                    actual.data,
                )

                fail(
                    "buffer mismatch\n"
                    f"  expected: {assertion.expected!r}\n"
                    f"  received: {actual.data!r}"
                    f"{diff}"
                )

            return

        if assertion.kind == "pointer_raw":
            if actual.kind != "pointer_raw":
                fail(
                    "expected raw pointer, "
                    f"received {actual.kind}"
                )
                return

            expected = self._resolve_pointer(assertion.expected)

            if assertion.expected == "NOT_NULL":
                if actual.data is None:
                    fail("expected non-NULL pointer")
                return

            if actual.data != expected:
                fail(
                    "pointer mismatch\n"
                    f"  expected: {expected!r}\n"
                    f"  received: {actual.data!r}"
                )

            return

        if assertion.kind == "pointer_array":
            if actual.kind != "pointer_array":
                fail(
                    "expected pointer array, "
                    f"received {actual.kind}"
                )
                return

            if len(actual.children) != len(assertion.children):
                fail(
                    "pointer array size mismatch\n"
                    f"  expected: {len(assertion.children)}\n"
                    f"  received: {len(actual.children)}"
                )

            count = min(
                len(actual.children),
                len(assertion.children),
            )

            for index in range(count):
                self._assert_capture(
                    actual.children[index],
                    assertion.children[index],
                    f"{path}[{index}]",
                )

            return

        if assertion.kind == "struct":
            if actual.kind == "null":
                fail("expected struct, received NULL")
                return

            if actual.kind != "struct":
                fail(f"expected struct, received {actual.kind}")
                return

            expected_fields = assertion.fields
            actual_fields = actual.fields

            if set(actual_fields) != set(expected_fields):
                missing = set(expected_fields) - set(actual_fields)
                unexpected = set(actual_fields) - set(expected_fields)

                if missing:
                    fail(
                        "struct missing fields: "
                        + ", ".join(sorted(missing))
                    )

                if unexpected:
                    fail(
                        "struct has unexpected fields: "
                        + ", ".join(sorted(unexpected))
                    )

            for field_name, field_assertion in expected_fields.items():
                if field_name not in actual_fields:
                    continue

                self._assert_capture(
                    actual_fields[field_name],
                    field_assertion,
                    f"{path}.{field_name}",
                )

            return

        raise ValueError(f"unknown assertion type: {assertion.kind}")

    @property
    def parsed_value(self):
        self._require_run()
        return self.return_type.parse(self.value)

    @property
    def returned_capture(self):
        self._require_run()
        return self.return_capture

    def equals(
        self,
        expected,
        message: str | None = None,
    ):
        self._require_run()

        if isinstance(expected, bytes):
            raise TypeError(
                "equals() cannot compare bytes; "
                "use buffer_equals() instead"
            )

        actual = self.return_type.parse(self.value)

        if actual != expected:
            prefix = f"{message}: " if message else ""

            self.failures.append(
                f"{prefix}return value mismatch\n"
                f"  expected: {expected!r}\n"
                f"  received: {actual!r}"
            )

        return self

    def not_equal(
        self,
        expected,
        message: str | None = None,
    ):
        self._require_run()

        if isinstance(expected, bytes):
            raise TypeError(
                "not_equal() cannot compare bytes; "
                "use buffer_equals() instead"
            )

        actual = self.return_type.parse(self.value)

        if actual == expected:
            prefix = f"{message}: " if message else ""

            self.failures.append(
                f"{prefix}unexpected return value\n"
                f"  expected anything except: {expected!r}\n"
                f"  received: {actual!r}"
            )

        return self

    def stdout_equals(
        self,
        expected: bytes,
        message: str | None = None,
    ):
        self._require_run()

        if not isinstance(expected, bytes):
            raise TypeError("stdout assertion expects bytes")

        if self.stdout != expected:
            prefix = f"{message}: " if message else ""

            diff = format_buffer_diff(
                expected,
                self.stdout,
            )

            self.failures.append(
                f"{prefix}stdout mismatch\n"
                f"  expected: {expected!r}\n"
                f"  received: {self.stdout!r}"
                f"{diff}"
            )

        return self

    def stderr_equals(
        self,
        expected: bytes,
        message: str | None = None,
    ):
        self._require_run()

        if not isinstance(expected, bytes):
            raise TypeError("stderr assertion expects bytes")

        if self.stderr != expected:
            prefix = f"{message}: " if message else ""

            diff = format_buffer_diff(
                expected,
                self.stderr,
            )

            self.failures.append(
                f"{prefix}stderr mismatch\n"
                f"  expected: {expected!r}\n"
                f"  received: {self.stderr!r}"
                f"{diff}"
            )

        return self

    def fd_equals(
        self,
        fd: CFileDescriptor,
        expected: bytes,
        message: str | None = None,
    ):
        self._require_run()

        if not isinstance(fd, CFileDescriptor):
            raise TypeError("fd assertion expects a CFileDescriptor")

        if not isinstance(expected, bytes):
            raise TypeError("fd assertion expects bytes")

        if fd.fd not in self.fd_outputs:
            raise RuntimeError(f"file descriptor {fd.fd} was not captured")

        actual = self.fd_outputs[fd.fd]

        if actual != expected:
            prefix = f"{message}: " if message else ""

            diff = format_buffer_diff(
                expected,
                actual,
            )

            self.failures.append(
                f"{prefix}fd {fd.fd} mismatch\n"
                f"  expected: {expected!r}\n"
                f"  received: {actual!r}"
                f"{diff}"
            )

        return self

    def buffer_equals(
        self,
        buffer: CBuffer,
        expected: bytes,
        message: str | None = None,
    ):
        self._require_run()

        if buffer.name not in self.buffers:
            raise RuntimeError(f"buffer '{buffer.name}' was not captured")

        actual = self.buffers[buffer.name]

        if actual != expected:
            prefix = f"{message}: " if message else ""

            diff = format_buffer_diff(
                expected,
                actual,
            )

            self.failures.append(
                f"{prefix}buffer '{buffer.name}' mismatch\n"
                f"  expected: {expected!r}\n"
                f"  received: {actual!r}"
                f"{diff}"
            )

        return self

    def variable_equals(
        self,
        variable: CVariable,
        expected,
        message: str | None = None,
    ):
        self._require_run()

        if not isinstance(variable, CVariable):
            raise TypeError("variable assertion expects a CVariable")

        if variable.name not in self.variables:
            raise RuntimeError(f"variable '{variable.name}' was not captured")

        actual = self.variables[variable.name]

        if actual != expected:
            prefix = f"{message}: " if message else ""

            self.failures.append(
                f"{prefix}variable '{variable.name}' mismatch\n"
                f"  expected: {expected!r}\n"
                f"  received: {actual!r}"
            )

        return self

    def returned_buffer_equals(
        self,
        expected: bytes,
        message: str | None = None,
    ):
        return self.assert_return(
            Assert.buffer_equals(expected),
            message or "returned buffer",
        )

    def assert_return(
        self,
        assertion: Assert,
        message: str | None = None,
    ):
        self._require_run()

        if not isinstance(assertion, Assert):
            raise TypeError("return assertion must be an Assert")

        if self.return_capture is None:
            raise RuntimeError(
                "returned capture was not produced; "
                "call capture_return() first"
            )

        self._assert_capture(
            self.return_capture,
            assertion,
            message or "returned capture",
        )

        return self

    def equals_string(
        self,
        expected: str,
        message: str | None = None,
    ):
        self._require_run()

        if self.value != expected:
            prefix = f"{message}: " if message else ""

            self.failures.append(
                f"{prefix}string mismatch\n"
                f"  expected: {expected!r}\n"
                f"  received: {self.value!r}"
            )

        return self

    def is_null(self, message: str | None = None):
        self._require_run()

        if self.value != "NULL":
            prefix = f"{message}: " if message else ""

            self.failures.append(
                f"{prefix}expected NULL\n"
                f"  received: {self.value!r}"
            )

        return self

    def is_not_null(self, message: str | None = None):
        self._require_run()

        if self.value == "NULL":
            prefix = f"{message}: " if message else ""

            self.failures.append(
                f"{prefix}expected non-NULL pointer"
            )

        return self

    def returned_pointer_is(
        self,
        buffer,
        message: str | None = None,
    ):
        self._require_run()

        expected = self._resolve_pointer(buffer)

        if self.value != expected:
            prefix = f"{message}: " if message else ""

            self.failures.append(
                f"{prefix}returned pointer mismatch\n"
                f"  expected: {expected}\n"
                f"  received: {self.value}"
            )

        return self

    def malloc_count_equals(
        self,
        expected: int,
        message: str | None = None,
    ):
        self._require_run()

        if self.malloc_count != expected:
            prefix = f"{message}: " if message else ""

            self.failures.append(
                f"{prefix}malloc call count mismatch\n"
                f"  expected: {expected}\n"
                f"  received: {self.malloc_count}"
            )

        return self

    def malloc_size_equals(
        self,
        index: int,
        expected: int,
        message: str | None = None,
    ):
        self._require_run()

        if index < 0:
            raise ValueError("malloc index cannot be negative")

        if index >= len(self.malloc_sizes):
            prefix = f"{message}: " if message else ""

            self.failures.append(
                f"{prefix}malloc call size was not recorded\n"
                f"  index: {index}\n"
                f"  call count: {self.malloc_count}"
            )

            return self

        actual = self.malloc_sizes[index]

        if actual != expected:
            prefix = f"{message}: " if message else ""

            self.failures.append(
                f"{prefix}malloc size mismatch\n"
                f"  call: {index}\n"
                f"  expected: {expected}\n"
                f"  received: {actual}"
            )

        return self

    def value_equals(
        self,
        actual,
        expected,
        message: str | None = None,
    ):
        self._require_run()

        if actual != expected:
            prefix = f"{message}: " if message else ""

            self.failures.append(
                f"{prefix}value mismatch\n"
                f"  expected: {expected!r}\n"
                f"  received: {actual!r}"
            )

        return self

    def assert_now(self):
        self._require_run()

        if self.failures:
            raise AssertionFailure("\n\n".join(self.failures))

        return self

    def assert_reference(self):
        self._require_run()

        if self.failures:
            raise UnexpectedResult("\n\n".join(self.failures))

        return self


class MallocController:
    def __init__(self, context):
        self.context = context
        self._fail_at: int | None = None

    def fail_at(self, index: int):
        if index < 0:
            raise ValueError("malloc failure index cannot be negative")

        self._fail_at = index
        return self

    def reset(self):
        self._fail_at = None
        return self

    @property
    def fail_at_index(self):
        return self._fail_at


def generate_argument(argument):
    if argument is None:
        return "NULL"

    if isinstance(argument, CBuffer):
        return argument.name

    if isinstance(argument, CBufferOffset):
        return f"{argument.buffer.name} + {argument.offset}"

    if isinstance(argument, CVariable):
        return argument.name

    if isinstance(argument, CStruct):
        return argument.name

    if isinstance(argument, CPointer):
        return f"&{argument.variable.name}"

    if isinstance(argument, CCallback):
        return argument.name

    if isinstance(argument, CFileDescriptor):
        return str(argument.fd)

    return str(argument)


def get_variable(argument):
    if isinstance(argument, CPointer):
        if isinstance(argument.variable, CVariable):
            return argument.variable

    return None

def get_declarations(argument):
    if isinstance(argument, CPointer):
        return get_declarations(argument.variable)

    if isinstance(argument, CVariable):
        return [argument]

    if isinstance(argument, CStruct):
        declarations = [argument]

        for value in argument.fields.values():
            declarations.extend(get_declarations(value))

        return declarations

    return []

def generate_capture(capture, expression):
    if capture.kind == "buffer":
        if capture.size == 0:
            return f"""    if ({expression} == NULL)
        fprintf(f, "NULL\\n");
    else
        fprintf(f, "BUFFER:0:\\n");"""

        return f"""    if ({expression} == NULL)
        fprintf(f, "NULL\\n");
    else
    {{
        fprintf(f, "BUFFER:{capture.size}:");
        for (size_t i = 0; i < {capture.size}; i++)
            fprintf(f, "%02x", ((unsigned char *){expression})[i]);
        fprintf(f, "\\n");
    }}"""

    if capture.kind == "pointer_raw":
        return (
            f"    if ({expression} == NULL)\n"
            f'        fprintf(f, "POINTER:NULL\\n");\n'
            f"    else\n"
            f'        fprintf(f, "POINTER:%p\\n", '
            f"(void *)({expression}));"
        )

    if capture.kind == "pointer_array":
        if len(capture.children) != capture.size:
            raise ValueError(
                "pointer_array capture has "
                f"{len(capture.children)} children, "
                f"expected {capture.size}"
            )

        children = []

        for index, child in enumerate(capture.children):
            children.append(
                generate_capture(
                    child,
                    f"{expression}[{index}]",
                )
            )

        return (
            f"    if ({expression} == NULL) {{\n"
            f'        fprintf(f, "NULL\\n");\n'
            f"    }} else {{\n"
            f'        fprintf(f, "POINTER_ARRAY\\n");\n'
            f'        fprintf(f, "COUNT:{capture.size}\\n");\n'
            f"    {textwrap.indent(chr(10).join(children), '    ')}\n"
            f"    }}"
        )

    if capture.kind == "struct":
        fields = []

        for field_name, field_capture in capture.fields.items():
            field_code = generate_capture(
                field_capture,
                f"{expression}->{field_name}",
            )

            fields.append(
                f'fprintf(f, "FIELD:{field_name}\\n");\n'
                f"{field_code}"
            )

        field_code = "\n".join(fields)

        return (
            f"    if ({expression} == NULL) {{\n"
            f'        fprintf(f, "NULL\\n");\n'
            f"    }} else {{\n"
            f'        fprintf(f, "STRUCT\\n");\n'
            f'        fprintf(f, "COUNT:{len(capture.fields)}\\n");\n'
            f"{textwrap.indent(field_code, '        ')}\n"
            f"    }}"
        )

    raise ValueError(f"unknown capture type: {capture.kind}")


def parse_capture(lines):
    lines = iter(lines)

    def parse_node(line):
        if line == "NULL":
            return CaptureResult("null")

        if line.startswith("BUFFER:"):
            _, size, data = line.split(":", 2)

            size = int(size)
            data = bytes.fromhex(data)

            if len(data) != size:
                raise RuntimeError(
                    "buffer capture size mismatch: "
                    f"declared {size}, received {len(data)}"
                )

            return CaptureResult(
                "buffer",
                data=data,
            )

        if line.startswith("POINTER:"):
            value = line.removeprefix("POINTER:")

            if value == "NULL":
                return CaptureResult(
                    "pointer_raw",
                    data=None,
                )

            return CaptureResult(
                "pointer_raw",
                data=value,
            )

        if line == "POINTER_ARRAY":
            count_line = next(lines)

            if not count_line.startswith("COUNT:"):
                raise RuntimeError(
                    "expected pointer array count, "
                    f"received: {count_line}"
                )

            count = int(count_line.removeprefix("COUNT:"))

            if count < 0:
                raise RuntimeError(
                    "pointer array count cannot be negative"
                )

            children = [
                parse_node(next(lines))
                for _ in range(count)
            ]

            return CaptureResult(
                "pointer_array",
                children=children,
                count=count,
            )

        if line == "STRUCT":
            count_line = next(lines)

            if not count_line.startswith("COUNT:"):
                raise RuntimeError(
                    "expected struct field count, "
                    f"received: {count_line}"
                )

            count = int(count_line.removeprefix("COUNT:"))

            if count < 0:
                raise RuntimeError(
                    "struct field count cannot be negative"
                )

            fields = {}

            for _ in range(count):
                field_line = next(lines)

                if not field_line.startswith("FIELD:"):
                    raise RuntimeError(
                        "expected struct field, "
                        f"received: {field_line}"
                    )

                field_name = field_line.removeprefix("FIELD:")

                if not field_name.isidentifier():
                    raise RuntimeError(
                        f"invalid captured struct field name: "
                        f"{field_name!r}"
                    )

                if field_name in fields:
                    raise RuntimeError(
                        f"duplicate captured struct field: "
                        f"{field_name!r}"
                    )

                fields[field_name] = parse_node(next(lines))

            return CaptureResult(
                "struct",
                fields=fields,
            )

        raise RuntimeError(f"unknown capture record: {line}")

    try:
        return parse_node(next(lines))
    except StopIteration:
        raise RuntimeError("empty capture output")


def generate_cleanup(capture, expression):
    if capture.kind == "buffer":
        return f"free({expression});"

    if capture.kind == "pointer_raw":
        return ""

    if capture.kind == "pointer_array":
        cleanup = []

        for index, child in enumerate(capture.children):
            code = generate_cleanup(
                child,
                f"{expression}[{index}]",
            )

            if code:
                cleanup.append(code)

        cleanup.append(f"free({expression});")

        return "\n".join(cleanup)

    if capture.kind == "struct":
        return f"free({expression});"

    raise ValueError(f"unknown capture type: {capture.kind}")


def generate_harness(
    function: CFunction,
    arguments,
    declarations,
    buffer_outputs: dict[str, Path],
    protocol_output: Path,
    fd_outputs: dict[int, Path],
    capture_output: Path | None = None,
    capture: Capture | None = None,
    malloc_fail_at: int | None = None,
):
    callbacks = [
        argument
        for argument in arguments
        if isinstance(argument, CCallback)
    ]

    callback_names = set()

    buffers = []

    for argument in arguments:
        buffer = get_buffer(argument)

        if buffer is not None and buffer not in buffers:
            buffers.append(buffer)

    variables = [
        declaration
        for declaration in declarations
        if isinstance(declaration, CVariable)
    ]

    reserved_names = {
        "result",
        *(buffer.name for buffer in buffers),
        *(declaration.name for declaration in declarations),
    }

    for callback in callbacks:
        if callback.name in callback_names:
            raise ValueError(
                f"duplicate callback name: {callback.name!r}"
            )

        if callback.name in reserved_names:
            raise ValueError(
                "callback name conflicts with "
                f"harness name: {callback.name!r}"
            )

        callback_names.add(callback.name)

    if function.name in callback_names:
        raise ValueError(
            "callback name conflicts with "
            f"function name: {function.name!r}"
        )

    callback_definitions = "\n\n".join(
        callback.generate()
        for callback in callbacks
    )

    argument_types = ", ".join(
        argument_type.declaration
        for argument_type in function.arg_types
    )

    if not argument_types:
        argument_types = "void"

    argument_values = ", ".join(
        generate_argument(argument)
        for argument in arguments
    )

    buffer_declarations = "\n    ".join(
        buffer.generate()
        for buffer in buffers
    )

    declaration_code = "\n    ".join(
        declaration.generate()
        for declaration in declarations
    )

    buffer_pointers = "\n    ".join(
        f'dprintf({PROTOCOL_FD}, '
        f'"BUFFER:{buffer.name}:%p\\n", '
        f"(void *){buffer.name});"
        for buffer in buffers
    )

    variable_outputs = "\n    ".join(
        variable.type.generate_output(
            variable.name,
            fd=PROTOCOL_FD,
            prefix=f"VARIABLE:{variable.name}",
        )
        for variable in variables
    )

    variable_pointers = "\n    ".join(
        f'dprintf({PROTOCOL_FD}, '
        f'"VARIABLE_POINTER:{variable.name}:%p\\n", '
        f"(void *)&{variable.name});"
        for variable in variables
    )

    struct_pointers = "\n    ".join(
        f'dprintf({PROTOCOL_FD}, '
        f'"STRUCT_POINTER:{declaration.name}:%p\\n", '
        f"(void *)&{declaration.name});"
        for declaration in declarations
        if isinstance(declaration, CStruct)
    )

    buffer_writes = "\n    ".join(
        (
            f'{{ FILE *f = fopen("{path}", "wb"); '
            f"fwrite({buffer.name}, 1, {buffer.size}, f); "
            f"fclose(f); }}"
        )
        for buffer, path in (
            (buffer, buffer_outputs[buffer.name])
            for buffer in buffers
        )
    )

    call = function.return_type.generate_call(
        function.name,
        argument_values,
    )

    output = function.return_type.generate_output(
        "result",
        fd=PROTOCOL_FD,
    )

    capture_write = ""
    cleanup_write = ""

    if capture_output is not None:
        if capture is None:
            raise ValueError(
                "capture output requires a capture specification"
            )

        capture_code = generate_capture(
            capture,
            "result",
        )

        capture_write = (
            f'{{ FILE *f = fopen("{capture_output}", "w"); '
            f"if (f == NULL) return 1;\n"
            f"{capture_code}; "
            f"fclose(f); }}"
        )

        cleanup_code = generate_cleanup(
            capture,
            "result",
        )

        if cleanup_code:
            cleanup_write = cleanup_code

    headers = "\n".join(
        f"#include <{header}>"
        for header in function.headers
    )

    protocol_setup = f"""
        {{
            FILE *protocol_file = fopen(
                "{protocol_output}",
                "w"
            );

            if (protocol_file == NULL)
                return 1;

            if (dup2(
                fileno(protocol_file),
                {PROTOCOL_FD}
            ) == -1)
                return 1;

            fclose(protocol_file);
        }}
    """

    fd_setup = "\n    ".join(
        (
            f'{{ int fd = open("{path}", '
            f"O_WRONLY | O_CREAT | O_TRUNC, 0600); "
            f"if (fd == -1) return 1; "
            f"if (dup2(fd, {fd_number}) == -1) "
            f"return 1; "
            f"if (fd != {fd_number}) close(fd); }}"
        )
        for fd_number, path in fd_outputs.items()
    )

    declaration = ""

    if not function.headers:
        declaration = f"""extern {function.return_type.declaration} {function.name}(
    {argument_types}
);"""

    malloc_setup = "malloc_strike_reset();"

    if malloc_fail_at is not None:
        malloc_setup += (
            f"\n    malloc_strike_fail_at({malloc_fail_at});"
        )

    malloc_output = f"""dprintf(
        {PROTOCOL_FD},
        "MALLOC_COUNT:%zu\\n",
        malloc_strike_count()
    );

    for (size_t i = 0; i < malloc_strike_count(); i++)
        dprintf(
            {PROTOCOL_FD},
            "MALLOC:%zu:%zu\\n",
            i,
            malloc_strike_size(i)
        );"""

    return f"""
#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include "malloc_strike.h"
{headers}

{callback_definitions}

{declaration}

int main(void)
{{
    {protocol_setup}

    {fd_setup}

    {buffer_declarations}

    {declaration_code}

    {buffer_pointers}

    {variable_pointers}

    {struct_pointers}

    {malloc_setup}

    {call}

    {malloc_output}

    {buffer_writes}

    {capture_write}

    {output}

    {variable_outputs}

    {cleanup_write}

    return 0;
}}
"""


class CContext:
    def __init__(
        self,
        project: Project,
        config: FunctionConfig | None,
        debug: bool = False,
        asan: bool = False,
    ):
        self.project = project
        self.project_dir = project.directory
        self.config = config
        self.debug = debug
        self.asan = asan
        self._asan_built = False

        self._functions = {}

        self.malloc = MallocController(self)
        self._next_fd = 3

    def function(
        self,
        name: str,
        *,
        returns: str = "int",
        args: list[str] | None = None,
    ):
        if name in self._functions:
            return self._functions[name]

        headers = []
        link = []
        err_flags = True

        if self.config is not None:
            definition = self.config.functions.get(name)

            if definition is not None:
                returns = definition.returns
                args = definition.args
                headers = definition.headers
                link = definition.link
                err_flags = definition.err_flags

        function = CFunction(
            context=self,
            name=name,
            returns=returns,
            args=args,
            headers=headers,
            link=link,
            err_flags=err_flags,
        )

        self._functions[name] = function

        return function

    def __getattr__(self, name: str):
        if name.startswith("_"):
            raise AttributeError(name)

        return self.function(name)

    def buffer(
        self,
        data: bytes = b"",
        size: int | None = None,
        name: str = "buffer",
        type: str = "unsigned char",
    ):
        return CBuffer(
            data=data,
            size=size,
            name=name,
            type=type,
        )

    def variable(
        self,
        type: str,
        value=None,
        name: str = "variable",
    ):
        return CVariable(
            context=self,
            type=type,
            value=value,
            name=name,
        )

    def struct(
        self,
        type: str,
        fields: dict[str, object],
        name: str = "structure",
    ):
        return CStruct(
            context=self,
            type=type,
            fields=fields,
            name=name,
        )

    def fd(self):
        while self._next_fd == PROTOCOL_FD:
            self._next_fd += 1

        fd = CFileDescriptor(
            self,
            self._next_fd,
        )

        self._next_fd += 1

        return fd

    def callback(
        self,
        *,
        name: str,
        returns: str,
        args: list[tuple[str, str]] | None = None,
        body: str,
    ):
        return CCallback(
            context=self,
            name=name,
            returns=returns,
            args=args or [],
            body=body,
        )

    def call(
        self,
        function: CFunction | str,
        *arguments,
    ):
        if self.config is None:
            raise RuntimeError(
                "This project does not configure "
                "C function testing"
            )

        if isinstance(function, str):
            function = self.function(function)

        if len(arguments) != len(function.arg_types):
            raise ValueError(
                f"{function.name} expects "
                f"{len(function.arg_types)} arguments, "
                f"got {len(arguments)}"
            )

        for index, (argument, argument_type) in enumerate(
            zip(arguments, function.arg_types)
        ):
            if isinstance(argument_type, FunctionPointerType):
                if not isinstance(argument, CCallback):
                    raise TypeError(
                        f"argument {index} of {function.name} "
                        "expects a callback"
                    )

                if argument.returns != argument_type.returns:
                    raise TypeError(
                        f"callback {argument.name!r} returns "
                        f"{argument.returns!r}, expected "
                        f"{argument_type.returns!r}"
                    )

                if len(argument.args) != len(argument_type.args):
                    raise TypeError(
                        f"callback {argument.name!r} expects "
                        f"{len(argument_type.args)} arguments, "
                        f"got {len(argument.args)}"
                    )

                for callback_arg, expected_arg in zip(
                    argument.args,
                    argument_type.args,
                ):
                    actual_type, _ = callback_arg

                    if actual_type != expected_arg:
                        raise TypeError(
                            f"callback {argument.name!r} "
                            f"argument type {actual_type!r} "
                            f"does not match expected "
                            f"{expected_arg!r}"
                        )

        return CCallResult(
            context=self,
            function=function,
            arguments=list(arguments),
        )

    def program(self, executable: str):
        from .process import Program

        return Program(
            self.project_dir,
            executable,
        )

    def _execute(self, call_result: CCallResult):
        function = call_result.function
        arguments = call_result.arguments


        declarations = []

        for argument in arguments:
            for declaration in get_declarations(argument):
                if declaration not in declarations:
                    declarations.append(declaration)

        malloc_fail_at = self.malloc.fail_at_index

        buffers = []

        for argument in arguments:
            buffer = get_buffer(argument)

            if buffer is not None and buffer not in buffers:
                buffers.append(buffer)

        with tempfile.TemporaryDirectory(
            prefix="test-42-c-call-"
        ) as temp:
            temp_dir = Path(temp)

            protocol_output = temp_dir / "protocol.txt"

            fd_outputs = {
                argument.fd: temp_dir / f"fd-{argument.fd}.bin"
                for argument in arguments
                if isinstance(argument, CFileDescriptor)
            }

            buffer_outputs = {
                buffer.name: temp_dir / f"{buffer.name}.bin"
                for buffer in buffers
            }

            capture_output = None

            if call_result._return_capture is not None:
                capture_output = temp_dir / "capture.txt"

            source = generate_harness(
                function,
                arguments,
                declarations,
                buffer_outputs,
                protocol_output=protocol_output,
                fd_outputs=fd_outputs,
                capture_output=capture_output,
                capture=call_result._return_capture,
                malloc_fail_at=malloc_fail_at,
            )

            if self.debug:
                print()
                print(
                    color(
                        "  [DEBUG] Generated C test",
                        Color.CYAN,
                    )
                )
                print(
                    color(
                        "  ────────────────────────────────────",
                        Color.CYAN,
                    ),
                    end="",
                )
                print(
                    color(
                        textwrap.indent(
                            source,
                            "  ",
                        ),
                        Color.YELLOW,
                    ),
                    end=(
                        ""
                        if source.endswith("\n")
                        else "\n"
                    ),
                )
                print(
                    color(
                        "  ────────────────────────────────────",
                        Color.CYAN,
                    )
                )

            source_file = temp_dir / "test.c"
            executable = temp_dir / "test"

            source_file.write_text(source)

            command = [
                "cc",
                "-Wall",
                "-Wextra",
                "-g",
            ]

            if self.asan:
                command.extend(
                    [
                        "-fsanitize=address",
                        "-fno-omit-frame-pointer",
                    ]
                )

            if function.err_flags:
                command.append("-Werror")

            for include in self.config.includes:
                command.extend(
                    [
                        "-I",
                        str(self.project_dir / include),
                    ]
                )

            command.extend(
                [
                    "-I",
                    str(MALLOC_STRIKE_DIR),
                ]
            )

            command.extend(self.config.cflags)

            command.append(str(source_file))
            command.append(str(MALLOC_STRIKE_SOURCE))

            for link in self.config.link:
                command.append(str(self.project_dir / link))

            for link in function.link:
                command.append(f"-l{link}")

            command.extend(
                [
                    "-Wl,--wrap=malloc",
                    "-o",
                    str(executable),
                ]
            )

            compile_result = subprocess.run(
                command,
                cwd=self.project_dir,
                capture_output=True,
            )

            if compile_result.returncode != 0:
                raise RuntimeError(
                    "failed to compile C test harness:\n"
                    + compile_result.stderr.decode(
                        errors="replace"
                    )
                )

            if self.debug:
                result = run_debug_process(
                    [str(executable)],
                    self.project_dir,
                )
            else:
                result = subprocess.run(
                    [str(executable)],
                    cwd=self.project_dir,
                    capture_output=True,
                )

            if result.returncode < 0:
                raise AssertionFailure(
                    "C function test crashed"
                )

            stderr = result.stderr.decode(
                errors="replace"
            )

            if self.asan and "AddressSanitizer" in stderr:
                message = (
                    "AddressSanitizer detected "
                    "a memory error"
                )

                if malloc_fail_at is not None:
                    message += (
                        f" at malloc failure "
                        f"{malloc_fail_at}"
                    )

                raise AssertionFailure(
                    message + ":\n\n" + stderr
                )

            if result.returncode != 0:
                raise RuntimeError(
                    "C test harness failed "
                    f"(exit code {result.returncode})\n"
                    + stderr
                )

            captured_buffers = {}

            for buffer in buffers:
                path = buffer_outputs[buffer.name]

                if path.exists():
                    captured_buffers[buffer.name] = (
                        path.read_bytes()
                    )

            if not protocol_output.exists():
                raise RuntimeError(
                    "C test harness did not produce "
                    "protocol output"
                )

            output = protocol_output.read_text().splitlines()

            captured_fds = {}

            for fd, path in fd_outputs.items():
                if path.exists():
                    captured_fds[fd] = path.read_bytes()

            pointer_values = {}
            variables = {}

            for line in output:
                if line.startswith("BUFFER:"):
                    _, name, pointer = line.split(
                        ":",
                        2,
                    )

                    pointer_values[name] = pointer

                elif line.startswith("VARIABLE_POINTER:"):
                    _, name, pointer = line.split(
                        ":",
                        2,
                    )

                    pointer_values[name] = pointer

                elif line.startswith("STRUCT_POINTER:"):
                    _, name, pointer = line.split(
                        ":",
                        2,
                    )

                    pointer_values[name] = pointer

                elif line.startswith("VARIABLE:"):
                    _, name, value = line.split(
                        ":",
                        2,
                    )

                    variables[name] = value

            for declaration in declarations:
                if not isinstance(
                    declaration,
                    CVariable,
                ):
                    continue

                if declaration.name not in variables:
                    continue

                variables[declaration.name] = (
                    declaration.type.parse(
                        variables[declaration.name]
                    )
                )

            malloc_count = 0
            malloc_sizes = []

            for line in output:
                if line.startswith("MALLOC_COUNT:"):
                    malloc_count = int(
                        line.removeprefix(
                            "MALLOC_COUNT:"
                        )
                    )

                elif line.startswith("MALLOC:"):
                    _, _, size = line.split(
                        ":",
                        2,
                    )

                    malloc_sizes.append(int(size))

            return_lines = [
                line
                for line in output
                if line.startswith("RETURN:")
            ]

            if not return_lines:
                raise RuntimeError(
                    "C test harness did not produce "
                    "a return value"
                )

            value = return_lines[-1].removeprefix(
                "RETURN:"
            )

            call_result.value = value
            call_result.stdout = result.stdout
            call_result.stderr = result.stderr
            call_result.fd_outputs = captured_fds
            call_result.returncode = result.returncode
            call_result.buffers = captured_buffers
            call_result.pointer_values = pointer_values
            call_result.variables = variables
            call_result.malloc_count = malloc_count
            call_result.malloc_sizes = malloc_sizes

            if capture_output is not None:
                if not capture_output.exists():
                    raise RuntimeError(
                        "C test harness did not produce "
                        "return capture"
                    )

                capture_lines = (
                    capture_output
                    .read_text()
                    .splitlines()
                )

                if not capture_lines:
                    raise RuntimeError(
                        "C test harness produced an "
                        "empty return capture"
                    )

                call_result.return_capture = (
                    parse_capture(capture_lines)
                )

            return call_result
