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

        return f"static {self.returns} {self.name}({arguments})\n" "{\n" f"{body}\n" "}"

    def __repr__(self):
        return self.name


class Capture:
    def __init__(self, kind, size=None):
        self.kind = kind
        self.size = size
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

    def child(self, capture):
        if not isinstance(capture, Capture):
            raise TypeError("capture child must be a Capture")

        if self.kind in ("buffer", "pointer_raw"):
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
    ):
        self.kind = kind
        self.data = data
        self.children = children or []
        self.count = count

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

        return f"CaptureResult.{self.kind}" f"({len(self.children)} children)"


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

    @classmethod
    def buffer_equals(cls, expected, message=None):
        if not isinstance(expected, bytes):
            raise TypeError("buffer assertion expects bytes")

        return cls("buffer", expected, message)

    @classmethod
    def pointer_equals(cls, expected, message=None):
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

    def child(self, assertion):
        if not isinstance(assertion, Assert):
            raise TypeError("assertion child must be an Assert")

        if self.kind in ("buffer", "pointer_raw"):
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
        self.returncode = None

        self.buffers = {}
        self.pointer_values = {}

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
                f"{self.function.name} has not been executed; " "call .run() first"
            )

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
                fail("expected raw pointer, " f"received {actual.kind}")
                return

            if assertion.expected == "NOT_NULL":
                if actual.data is None:
                    fail("expected non-NULL pointer")
                return

            if actual.data != assertion.expected:
                fail(
                    "pointer mismatch\n"
                    f"  expected: {assertion.expected!r}\n"
                    f"  received: {actual.data!r}"
                )

            return

        if assertion.kind == "pointer_array":
            if actual.kind != "pointer_array":
                fail("expected pointer array, " f"received {actual.kind}")
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

        raise ValueError(f"unknown assertion type: {assertion.kind}")

    @property
    def parsed_value(self):
        self._require_run()
        return self.return_type.parse(self.value)

    @property
    def returned_capture(self):
        self._require_run()
        return self.return_capture

    def equals(self, expected, message: str | None = None):
        self._require_run()

        if isinstance(expected, bytes):
            raise TypeError(
                "equals() cannot compare bytes; " "use buffer_equals() instead"
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

    def not_equal(self, expected, message: str | None = None):
        self._require_run()

        if isinstance(expected, bytes):
            raise TypeError(
                "not_equal() cannot compare bytes; " "use buffer_equals() instead"
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
                "returned capture was not produced; " "call capture_return() first"
            )

        self._assert_capture(
            self.return_capture,
            assertion,
            message or "returned capture",
        )

        return self

    def equals_string(self, expected: str, message: str | None = None):
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
                f"{prefix}expected NULL\n" f"  received: {self.value!r}"
            )

        return self

    def is_not_null(self, message: str | None = None):
        self._require_run()

        if self.value == "NULL":
            prefix = f"{message}: " if message else ""

            self.failures.append(f"{prefix}expected non-NULL pointer")

        return self

    def returned_pointer_is(self, buffer, message: str | None = None):
        self._require_run()

        if isinstance(buffer, CBufferOffset):
            base = self.pointer_values.get(buffer.buffer.name)

            if base is None:
                raise RuntimeError(
                    f"buffer '{buffer.buffer.name}' pointer " f"was not captured"
                )

            expected = hex(int(base, 16) + buffer.offset)
        else:
            expected = self.pointer_values.get(buffer.name)

            if expected is None:
                raise RuntimeError(
                    f"buffer '{buffer.name}' pointer " f"was not captured"
                )

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
    if isinstance(argument, CBuffer):
        return argument.name

    if isinstance(argument, CBufferOffset):
        return f"{argument.buffer.name} + {argument.offset}"

    if isinstance(argument, CCallback):
        return argument.name

    return str(argument)


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
            f'        fprintf(f, "POINTER:%p\\n", (void *)({expression}));'
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
                    f"buffer capture size mismatch: "
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
                    f"expected pointer array count, received: {count_line}"
                )

            count = int(count_line.removeprefix("COUNT:"))

            if count < 0:
                raise RuntimeError("pointer array count cannot be negative")

            children = [parse_node(next(lines)) for _ in range(count)]

            return CaptureResult(
                "pointer_array",
                children=children,
                count=count,
            )

        raise RuntimeError(f"unknown capture record: {line}")

    return parse_node(next(lines))


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

    raise ValueError(f"unknown capture type: {capture.kind}")


def generate_harness(
    function: CFunction,
    arguments,
    buffer_outputs: dict[str, Path],
    protocol_output: Path,
    capture_output: Path | None = None,
    capture: Capture | None = None,
    malloc_fail_at: int | None = None,
):
    callbacks = [argument for argument in arguments if isinstance(argument, CCallback)]

    callback_names = set()

    reserved_names = {
        "result",
        *(
            buffer.name
            for argument in arguments
            if (buffer := get_buffer(argument)) is not None
        ),
    }

    for callback in callbacks:
        if callback.name in callback_names:
            raise ValueError(f"duplicate callback name: {callback.name!r}")

        if callback.name in reserved_names:
            raise ValueError(
                f"callback name conflicts with harness name: " f"{callback.name!r}"
            )

        callback_names.add(callback.name)

    if function.name in callback_names:
        raise ValueError(
            f"callback name conflicts with function name: {function.name!r}"
        )

    callback_definitions = "\n\n".join(callback.generate() for callback in callbacks)

    argument_types = ", ".join(
        argument_type.declaration for argument_type in function.arg_types
    )

    if not argument_types:
        argument_types = "void"

    argument_values = ", ".join(generate_argument(argument) for argument in arguments)

    buffers = [argument for argument in arguments if isinstance(argument, CBuffer)]

    buffer_declarations = "\n    ".join(buffer.generate() for buffer in buffers)

    buffer_pointers = "\n    ".join(
        f'dprintf({PROTOCOL_FD}, "BUFFER:{buffer.name}:%p\\n", (void *){buffer.name});'
        for buffer in buffers
    )

    buffer_writes = "\n    ".join(
        (
            f'{{ FILE *f = fopen("{path}", "wb"); '
            f"fwrite({buffer.name}, 1, {buffer.size}, f); "
            f"fclose(f); }}"
        )
        for buffer, path in (
            (buffer, buffer_outputs[buffer.name]) for buffer in buffers
        )
    )

    call = function.return_type.generate_call(
        function.name,
        argument_values,
    )

    output = function.return_type.generate_output("result", fd=PROTOCOL_FD)

    capture_write = ""
    cleanup_write = ""

    if capture_output is not None:
        if capture is None:
            raise ValueError("capture output requires a capture specification")

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

    headers = "\n".join(f"#include <{header}>" for header in function.headers)

    protocol_setup = f"""
        {{
            FILE *protocol_file = fopen("{protocol_output}", "w");
    
            if (protocol_file == NULL)
                return 1;
    
            if (dup2(fileno(protocol_file), {PROTOCOL_FD}) == -1)
                return 1;
    
            fclose(protocol_file);
        }}
    """

    declaration = ""

    if not function.headers:
        declaration = f"""extern {function.return_type.declaration} {function.name}(
    {argument_types}
);"""

    malloc_setup = "malloc_strike_reset();"

    if malloc_fail_at is not None:
        malloc_setup += f"\n    malloc_strike_fail_at({malloc_fail_at});"

    malloc_output = f"""dprintf({PROTOCOL_FD}, "MALLOC_COUNT:%zu\\n", malloc_strike_count());
    
    for (size_t i = 0; i < malloc_strike_count(); i++)
        dprintf({PROTOCOL_FD}, "MALLOC:%zu:%zu\\n", i, malloc_strike_size(i));"""

    return f"""
#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
#include <unistd.h>
#include "malloc_strike.h"
{headers}

{callback_definitions}

{declaration}

int main(void)
{{
    {protocol_setup}

    {buffer_declarations}

    {buffer_pointers}

    {malloc_setup}

    {call}

    {malloc_output}

    {buffer_writes}

    {capture_write}

    {output}

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
            raise RuntimeError("This project does not configure " "C function testing")

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
                        f"argument {index} of {function.name} expects " f"a callback"
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
                        f"{len(argument_type.args)} arguments, got "
                        f"{len(argument.args)}"
                    )

                for callback_arg, expected_arg in zip(
                    argument.args,
                    argument_type.args,
                ):
                    actual_type, _ = callback_arg

                    if actual_type != expected_arg:
                        raise TypeError(
                            f"callback {argument.name!r} argument type "
                            f"{actual_type!r} does not match expected "
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
        malloc_fail_at = self.malloc.fail_at_index

        buffers = []

        for argument in arguments:
            buffer = get_buffer(argument)

            if buffer is not None and buffer not in buffers:
                buffers.append(buffer)

        with tempfile.TemporaryDirectory(prefix="test-42-c-call-") as temp:
            temp_dir = Path(temp)

            protocol_output = temp_dir / "protocol.txt"

            buffer_outputs = {
                buffer.name: temp_dir / f"{buffer.name}.bin" for buffer in buffers
            }

            capture_output = None

            if call_result._return_capture is not None:
                capture_output = temp_dir / "capture.txt"

            source = generate_harness(
                function,
                arguments,
                buffer_outputs,
                protocol_output=protocol_output,
                capture_output=capture_output,
                capture=call_result._return_capture,
                malloc_fail_at=self.malloc.fail_at_index,
            )

            if self.debug:
                print()
                print(color("  [DEBUG] Generated C test", Color.CYAN))
                print(
                    color("  ────────────────────────────────────", Color.CYAN), end=""
                )
                print(
                    color(textwrap.indent(source, "  "), Color.YELLOW),
                    end="" if source.endswith("\n") else "\n",
                )
                print(color("  ────────────────────────────────────", Color.CYAN))

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
                    + compile_result.stderr.decode(errors="replace")
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
                raise AssertionFailure("C function test crashed")

            stderr = result.stderr.decode(errors="replace")

            if self.asan and "AddressSanitizer" in stderr:
                message = "AddressSanitizer detected a memory error"

                if malloc_fail_at is not None:
                    message += f" at malloc failure {malloc_fail_at}"

                raise AssertionFailure(message + ":\n\n" + stderr)

            if result.returncode != 0:
                raise RuntimeError(
                    "C test harness failed "
                    f"(exit code {result.returncode})\n" + stderr
                )

            captured_buffers = {}

            for buffer in buffers:
                path = buffer_outputs[buffer.name]

                if path.exists():
                    captured_buffers[buffer.name] = path.read_bytes()

            if not protocol_output.exists():
                raise RuntimeError("C test harness did not produce protocol output")

            output = protocol_output.read_text().splitlines()

            pointer_values = {}

            for line in output:
                if line.startswith("BUFFER:"):
                    _, name, pointer = line.split(":", 2)
                    pointer_values[name] = pointer

            malloc_count = 0
            malloc_sizes = []

            for line in output:
                if line.startswith("MALLOC_COUNT:"):
                    malloc_count = int(line.removeprefix("MALLOC_COUNT:"))

                elif line.startswith("MALLOC:"):
                    _, _, size = line.split(":", 2)
                    malloc_sizes.append(int(size))

            return_lines = [line for line in output if line.startswith("RETURN:")]

            if not return_lines:
                raise RuntimeError("C test harness did not produce a return value")

            value = return_lines[-1].removeprefix("RETURN:")

            call_result.value = value
            call_result.stdout = result.stdout
            call_result.stderr = result.stderr
            call_result.returncode = result.returncode
            call_result.buffers = captured_buffers
            call_result.pointer_values = pointer_values
            call_result.malloc_count = malloc_count
            call_result.malloc_sizes = malloc_sizes

            if capture_output is not None:
                if not capture_output.exists():
                    raise RuntimeError("C test harness did not produce return capture")

                capture_lines = capture_output.read_text().splitlines()

                if not capture_lines:
                    raise RuntimeError(
                        "C test harness produced an empty return capture"
                    )

                call_result.return_capture = parse_capture(capture_lines)

            return call_result
