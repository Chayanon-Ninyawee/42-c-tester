import selectors
import subprocess
import tempfile
import textwrap
from pathlib import Path

from .color import Color, color
from .ctype import CType, parse_ctype
from .project import FunctionConfig
from .result import AssertionFailure


def run_debug_process(command, cwd):
    process = subprocess.Popen(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=0,
    )

    selector = selectors.DefaultSelector()

    selector.register(
        process.stdout,
        selectors.EVENT_READ,
        "STDOUT",
    )

    selector.register(
        process.stderr,
        selectors.EVENT_READ,
        "STDERR",
    )

    stdout = bytearray()
    stderr = bytearray()

    print()
    print(color("  [DEBUG] Program output", Color.CYAN))
    print(color("  ────────────────────────────────────", Color.CYAN))

    while selector.get_map():
        for key, _ in selector.select():
            stream = key.fileobj
            name = key.data

            data = stream.read(4096)

            if not data:
                selector.unregister(stream)
                continue

            if name == "STDOUT":
                stdout.extend(data)
                prefix = color("  STDOUT:", Color.BLUE)
            else:
                stderr.extend(data)
                prefix = color("  STDERR:", Color.MAGENTA)

            text = data.decode(errors="replace")

            for line in text.splitlines():
                print(f"{prefix} {line}")

    returncode = process.wait()

    selector.close()

    print(color("  ────────────────────────────────────", Color.CYAN))

    return subprocess.CompletedProcess(
        command,
        returncode,
        bytes(stdout),
        bytes(stderr),
    )


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
        self.type = type

    def __repr__(self):
        return self.name

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
        self.arg_types = [parse_ctype(arg) for arg in (args or [])]

        self.headers = headers or []
        self.link = link or []
        self.err_flags = err_flags

    def __call__(self, *arguments: str):
        return self.context.call(
            self,
            *arguments,
        )


class CCallResult:
    def __init__(
        self,
        value: str,
        return_type: CType,
        stdout: bytes,
        stderr: bytes,
        returncode: int,
        buffers: dict[str, bytes] | None = None,
        pointer_values: dict[str, str] | None = None,
    ):
        self.value = value
        self.return_type = return_type
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode
        self.buffers = buffers or {}
        self.pointer_values = pointer_values or {}

        self.failures: list[str] = []

    def equals(self, expected, message: str | None = None):
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
        if buffer.name not in self.buffers:
            raise RuntimeError(f"buffer '{buffer.name}' was not captured")

        actual = self.buffers[buffer.name]

        if actual != expected:
            prefix = f"{message}: " if message else ""

            self.failures.append(
                f"{prefix}buffer '{buffer.name}' mismatch\n"
                f"  expected: {expected!r}\n"
                f"  received: {actual!r}"
            )

        return self

    def equals_string(self, expected: str, message: str | None = None):
        if self.value != expected:
            prefix = f"{message}: " if message else ""

            self.failures.append(
                f"{prefix}string mismatch\n"
                f"  expected: {expected!r}\n"
                f"  received: {self.value!r}"
            )

        return self

    def is_null(self, message: str | None = None):
        if self.value != "NULL":
            prefix = f"{message}: " if message else ""

            self.failures.append(
                f"{prefix}expected NULL\n" f"  received: {self.value!r}"
            )

        return self

    def is_not_null(self, message: str | None = None):
        if self.value == "NULL":
            prefix = f"{message}: " if message else ""

            self.failures.append(f"{prefix}expected non-NULL pointer")

        return self

    def returned_pointer_is(self, buffer, message: str | None = None):
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

    def assert_now(self):
        if self.failures:
            raise AssertionFailure("\n\n".join(self.failures))

        return self


class CContext:
    def __init__(
        self,
        project_dir: Path,
        config: FunctionConfig | None,
        debug: bool = False,
    ):
        self.project_dir = project_dir
        self.config = config
        self.debug = debug
        self._functions = {}

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

        return self._execute(
            function,
            list(arguments),
        )

    def program(self, executable: str):
        from .process import Program

        return Program(
            self.project_dir,
            executable,
        )

    def _execute(
        self,
        function: CFunction,
        arguments,
    ):

        buffers = []

        for argument in arguments:
            buffer = get_buffer(argument)

            if buffer is not None and buffer not in buffers:
                buffers.append(buffer)

        with tempfile.TemporaryDirectory(prefix="test-42-c-call-") as temp:
            temp_dir = Path(temp)

            buffer_outputs = {
                buffer.name: temp_dir / f"{buffer.name}.bin" for buffer in buffers
            }

            source = generate_harness(
                function,
                arguments,
                buffer_outputs,
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
            ]

            if function.err_flags:
                command.append("-Werror")

            for include in self.config.includes:
                command.extend(
                    [
                        "-I",
                        str(self.project_dir / include),
                    ]
                )

            command.extend(self.config.cflags)

            command.append(str(source_file))

            for link in self.config.link:
                command.append(str(self.project_dir / link))

            for link in function.link:
                command.append(f"-l{link}")

            command.extend(
                [
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

            if result.returncode != 0:
                raise RuntimeError(
                    "C test harness failed "
                    f"(exit code {result.returncode})\n"
                    + result.stderr.decode(errors="replace")
                )

            captured_buffers = {}

            for buffer in buffers:
                path = buffer_outputs[buffer.name]

                if path.exists():
                    captured_buffers[buffer.name] = path.read_bytes()

            output = result.stdout.decode(errors="replace").splitlines()

            pointer_values = {}

            for line in output:
                if line.startswith("BUFFER:"):
                    _, name, pointer = line.split(":", 2)
                    pointer_values[name] = pointer

            return_lines = [line for line in output if line.startswith("RETURN:")]

            if not return_lines:
                raise RuntimeError("C test harness did not produce a return value")

            value = return_lines[-1].removeprefix("RETURN:")

            return CCallResult(
                value=value,
                return_type=function.return_type,
                stdout=result.stdout,
                stderr=result.stderr,
                returncode=result.returncode,
                buffers=captured_buffers,
                pointer_values=pointer_values,
            )


def generate_argument(argument):
    if isinstance(argument, CBuffer):
        return argument.name

    if isinstance(argument, CBufferOffset):
        return f"{argument.buffer.name} + {argument.offset}"

    return argument


def generate_buffer(buffer: CBuffer):
    if buffer.size <= 0:
        raise ValueError("zero-sized C buffers are not supported")

    values = ", ".join(f"0x{byte:02x}" for byte in buffer.data)

    return f"{buffer.type} {buffer.name}[{buffer.size}]" f" = {{ {values} }};"


def get_buffer(argument):
    if isinstance(argument, CBuffer):
        return argument

    if isinstance(argument, CBufferOffset):
        return argument.buffer

    return None


def generate_harness(
    function: CFunction,
    arguments,
    buffer_outputs: dict[str, Path],
):
    argument_types = ", ".join(
        argument_type.declaration for argument_type in function.arg_types
    )

    if not argument_types:
        argument_types = "void"

    argument_values = ", ".join(generate_argument(argument) for argument in arguments)

    buffers = [argument for argument in arguments if isinstance(argument, CBuffer)]

    buffer_declarations = "\n    ".join(generate_buffer(buffer) for buffer in buffers)

    buffer_pointers = "\n    ".join(
        f'printf("BUFFER:{buffer.name}:%p\\n", (void *){buffer.name});'
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

    output = function.return_type.serialize("result")

    headers = "\n".join(f"#include <{header}>" for header in function.headers)

    declaration = ""

    if not function.headers:
        declaration = f"""extern {function.return_type.declaration} {function.name}(
    {argument_types}
);"""

    return f"""
#include <stdio.h>
{headers}
{declaration}

int main(void)
{{
    {buffer_declarations}

    {buffer_pointers}

    {call}

    {buffer_writes}

    {output}

    return 0;
}}
"""
