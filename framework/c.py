import subprocess
import tempfile
import textwrap
from pathlib import Path

from .color import Color, color
from .project import Project
from .utils import format_buffer_diff, run_debug_process

MALLOC_STRIKE_DIR = Path(__file__).parent / "malloc_strike"
MALLOC_STRIKE_SOURCE = MALLOC_STRIKE_DIR / "malloc_strike.c"

PROTOCOL_FD = 39


def c_bytes(data: bytes) -> str:
    return ", ".join(f"0x{byte:02x}" for byte in data)


class CCodeAssertion:
    def __init__(
        self,
        code,
        kind,
        expected,
        value_name=None,
        buffer_name=None,
        fd_number=None,
        output_kind=None,
        message=None,
    ):
        self.code = code
        self.kind = kind
        self.expected = expected
        self.value_name = value_name
        self.buffer_name = buffer_name
        self.fd_number = fd_number
        self.output_kind = output_kind
        self.message = message
        self.is_reference = False

    def reference(self):
        self.code._require_configure()
        self.is_reference = True
        return self

    def assert_now(self):
        self.code.assert_now()
        return self


class CCodeMalloc:
    def __init__(self, code):
        self.code = code

    @property
    def actual_count(self):
        self.code._require_run()

        return self.code.malloc_count

    def count(self, expected, message=None):
        self.code._require_configure()

        self.code._malloc_assertions.append(("count", expected, message))

        return self

    def size(self, index, expected, message=None):
        self.code._require_configure()

        if not isinstance(index, int):
            raise TypeError("malloc index must be an integer")

        if index < 0:
            raise ValueError("malloc index cannot be negative")

        self.code._malloc_assertions.append(("size", index, expected, message))

        return self

    def fail_at(self, index):
        self.code._require_configure()

        if not isinstance(index, int):
            raise TypeError("malloc failure index must be an integer")

        if index < 0:
            raise ValueError("malloc failure index cannot be negative")

        self.code.malloc_fail_at = index

        return self


class CCodeValue:
    def __init__(self, code, name):
        self.code = code
        self.name = name

    def equals(self, expected, message=None):
        self.code._require_configure()

        if not isinstance(expected, str):
            raise TypeError("value assertion expected value must be a string")

        assertion = CCodeAssertion(
            self.code,
            "value",
            expected,
            value_name=self.name,
            message=message,
        )

        self.code._assertions.append(assertion)

        return assertion

    def not_equal(self, expected, message=None):
        self.code._require_configure()

        if not isinstance(expected, str):
            raise TypeError("value assertion expected value must be a string")

        assertion = CCodeAssertion(
            self.code,
            "not_value",
            expected,
            value_name=self.name,
            message=message,
        )

        self.code._assertions.append(assertion)

        return assertion


class CCodeBuffer:
    def __init__(self, code, name):
        self.code = code
        self.name = name

    def equals(self, expected, message=None):
        self.code._require_configure()

        if not isinstance(expected, bytes):
            raise TypeError("buffer assertion expected value must be bytes")

        assertion = CCodeAssertion(
            self.code,
            "buffer",
            expected,
            buffer_name=self.name,
            message=message,
        )

        self.code._assertions.append(assertion)

        return assertion

    def not_equal(self, expected, message=None):
        self.code._require_configure()

        if not isinstance(expected, bytes):
            raise TypeError("buffer assertion expected value must be bytes")

        assertion = CCodeAssertion(
            self.code,
            "not_buffer",
            expected,
            buffer_name=self.name,
            message=message,
        )

        self.code._assertions.append(assertion)

        return assertion


class CCodeOutput:
    def __init__(self, code, kind, fd_number=None):
        self.code = code
        self.kind = kind
        self.fd_number = fd_number

    def equals(self, expected, message=None):
        self.code._require_configure()

        assertion = CCodeAssertion(
            self.code,
            "bytes",
            expected,
            fd_number=self.fd_number,
            output_kind=self.kind,
            message=message,
        )

        self.code._assertions.append(assertion)

        return assertion

    def not_equal(self, expected, message=None):
        self.code._require_configure()

        assertion = CCodeAssertion(
            self.code,
            "not_bytes",
            expected,
            fd_number=self.fd_number,
            output_kind=self.kind,
            message=message,
        )

        self.code._assertions.append(assertion)

        return assertion


class CCodeReturn:
    def __init__(self, code):
        self.code = code

    def equals(self, expected, message=None):
        self.code._require_configure()

        assertion = CCodeAssertion(
            self.code,
            "return",
            expected,
            message=message,
        )

        self.code._assertions.append(assertion)

        return assertion

    def not_equal(self, expected, message=None):
        self.code._require_configure()

        assertion = CCodeAssertion(
            self.code,
            "not_return",
            expected,
            message=message,
        )

        self.code._assertions.append(assertion)

        return assertion


class CCode:
    def __init__(
        self,
        context,
        source,
        includes,
        functions,
    ):
        self.context = context
        self.source = textwrap.dedent(source).strip()
        self.includes = list(includes)
        self.functions = [textwrap.dedent(function).strip() for function in functions]

        self.executed = False

        self.returncode = None
        self._stdout = b""
        self._stderr = b""

        self.fd_outputs = {}
        self.values = {}
        self.buffers = {}

        self.malloc_count = 0
        self.malloc_sizes = []
        self.malloc_fail_at = None

        self._capture_fds = set()

        self._assertions = []
        self._malloc_assertions = []

        self.failures = []
        self.reference_failures = []

        self._malloc = CCodeMalloc(self)

    @property
    def malloc(self):
        return self._malloc

    def value(self, name):
        self._require_configure()

        if not isinstance(name, str):
            raise TypeError("value name must be a string")

        if not name:
            raise ValueError("value name cannot be empty")

        if not name.replace("_", "").isalnum():
            raise ValueError(
                "value name must contain only letters, numbers, and underscores"
            )

        return CCodeValue(
            self,
            name,
        )

    def buffer(self, name):
        self._require_configure()

        if not isinstance(name, str):
            raise TypeError("buffer name must be a string")

        if not name:
            raise ValueError("buffer name cannot be empty")

        if not name.replace("_", "").isalnum():
            raise ValueError(
                "buffer name must contain only letters, numbers, and underscores"
            )

        return CCodeBuffer(
            self,
            name,
        )

    def fd(self, fd):
        self._require_configure()

        if not isinstance(fd, int):
            raise TypeError("file descriptor must be an integer")

        if fd < 3:
            raise ValueError("captured file descriptor must be >= 3")

        if fd == PROTOCOL_FD:
            raise ValueError(f"file descriptor {PROTOCOL_FD} is reserved")

        self._capture_fds.add(fd)

        return CCodeOutput(
            self,
            "fd",
            fd,
        )

    def stdout(self):
        self._require_configure()

        return CCodeOutput(
            self,
            "stdout",
        )

    def stderr(self):
        self._require_configure()

        return CCodeOutput(
            self,
            "stderr",
        )

    def return_value(self):
        self._require_configure()

        return CCodeReturn(self)

    def run(self):
        if self.executed:
            raise RuntimeError("C code has already been executed")

        self.context._execute_code(self)
        self.executed = True

        return self

    def assert_now(self):
        self._require_run()

        self._run_assertions()

        if self.reference_failures:
            from .result import UnexpectedResult

            raise UnexpectedResult("\n\n".join(self.reference_failures))

        if self.failures:
            from .result import AssertionFailure

            raise AssertionFailure("\n\n".join(self.failures))

        return self

    def _require_configure(self):
        if self.executed:
            raise RuntimeError("cannot configure C code after it has been executed")

    def _require_run(self):
        if not self.executed:
            self.run()

    def _run_assertions(self):
        self.failures = []
        self.reference_failures = []

        for assertion in self._assertions:
            actual = self._get_assertion_value(assertion)

            if self._assertion_matches(assertion, actual):
                continue

            failure = self._format_assertion_failure(
                assertion,
                actual,
            )

            if assertion.is_reference:
                self.reference_failures.append(failure)
            else:
                self.failures.append(failure)

        self._run_malloc_assertions()

    def _get_assertion_value(self, assertion):
        if assertion.kind in (
            "return",
            "not_return",
        ):
            return self.returncode

        if assertion.kind in (
            "value",
            "not_value",
        ):
            if assertion.value_name not in self.values:
                raise RuntimeError(
                    f"value '{assertion.value_name}' " "was not reported by the test"
                )

            return self.values[assertion.value_name]

        if assertion.kind in (
            "buffer",
            "not_buffer",
        ):
            if assertion.buffer_name not in self.buffers:
                raise RuntimeError(
                    f"buffer '{assertion.buffer_name}' was not reported by the test"
                )

            return self.buffers[assertion.buffer_name]

        if assertion.output_kind == "stdout":
            return self._stdout

        if assertion.output_kind == "stderr":
            return self._stderr

        if assertion.output_kind == "fd":
            return self.fd_outputs.get(
                assertion.fd_number,
                b"",
            )

        raise RuntimeError(f"unknown output kind: {assertion.output_kind}")

    def _assertion_matches(self, assertion, actual):
        if assertion.kind in (
            "bytes",
            "return",
            "value",
            "buffer",
        ):
            return actual == assertion.expected

        if assertion.kind in (
            "not_bytes",
            "not_return",
            "not_value",
            "not_buffer",
        ):
            return actual != assertion.expected

        raise RuntimeError(f"unknown assertion kind: {assertion.kind}")

    def _run_malloc_assertions(self):
        for assertion in self._malloc_assertions:
            kind = assertion[0]

            if kind == "count":
                _, expected, message = assertion

                if self.malloc_count != expected:
                    self.failures.append(
                        self._format_malloc_failure(
                            message,
                            f"malloc count {expected}",
                            f"malloc count {self.malloc_count}",
                        )
                    )

            elif kind == "size":
                _, index, expected, message = assertion

                if index >= len(self.malloc_sizes):
                    self.failures.append(
                        self._format_malloc_failure(
                            message,
                            f"malloc[{index}] size {expected}",
                            "allocation does not exist",
                        )
                    )
                    continue

                actual = self.malloc_sizes[index]

                if actual != expected:
                    self.failures.append(
                        self._format_malloc_failure(
                            message,
                            f"malloc[{index}] size {expected}",
                            f"malloc[{index}] size {actual}",
                        )
                    )

            else:
                raise RuntimeError(f"unknown malloc assertion: {kind}")

    def _format_assertion_failure(self, assertion, actual):
        if assertion.kind in (
            "buffer",
            "not_buffer",
        ):
            if assertion.kind == "buffer":
                comparison = format_buffer_diff(
                    assertion.expected,
                    actual,
                )

                if not comparison:
                    comparison = (
                        f"Expected: {assertion.expected!r}\n" f"Actual:   {actual!r}"
                    )
            else:
                comparison = (
                    f"Expected: not {assertion.expected!r}\n"
                    f"Actual:       {actual!r}"
                )

            if assertion.message:
                return f"{assertion.message}\n" f"{comparison}"

            return comparison

        expected = repr(assertion.expected)
        actual = repr(actual)

        if assertion.kind in (
            "bytes",
            "return",
            "value",
        ):
            comparison = f"Expected: {expected}\n" f"Actual:   {actual}"
        else:
            comparison = f"Expected: not {expected}\n" f"Actual:       {actual}"

        if assertion.message:
            return f"{assertion.message}\n" f"{comparison}"

        return comparison

    def _format_malloc_failure(
        self,
        message,
        expected,
        actual,
    ):
        comparison = f"Expected: {expected}\n" f"Actual:   {actual}"

        if message:
            return f"{message}\n{comparison}"

        return comparison


class CCodeBuilder:
    def __init__(
        self,
        context,
        includes=None,
        functions=None,
    ):
        self.context = context
        self.includes = list(includes or [])
        self.functions = list(functions or [])

    def include(self, *headers):
        for header in headers:
            if not isinstance(header, str):
                raise TypeError("header name must be a string")

            if not header:
                raise ValueError("header name cannot be empty")

            self.includes.append(header)

        return self

    def function(self, source):
        if not isinstance(source, str):
            raise TypeError("function source must be a string")

        if not source.strip():
            raise ValueError("function source cannot be empty")

        self.functions.append(source)

        return self

    def code(self, source):
        return CCode(
            self.context,
            source,
            list(self.includes),
            list(self.functions),
        )


def generate_code_harness(
    source,
    includes,
    functions,
    capture_fds,
    malloc_fail_at=None,
):
    explicit_includes = "\n".join(f"#include <{header}>" for header in includes)

    explicit_functions = "\n\n".join(functions for functions in functions)

    fd_setup = []

    for fd in sorted(capture_fds):
        fd_setup.append(f"""
    {{
        int __capture_fd = open(
            "{_fd_path_placeholder(fd)}",
            O_WRONLY | O_CREAT | O_TRUNC,
            0600
        );

        if (__capture_fd < 0)
            return 100;

        if (__capture_fd != {fd})
        {{
            if (dup2(__capture_fd, {fd}) < 0)
            {{
                close(__capture_fd);
                return 100;
            }}

            close(__capture_fd);
        }}
    }}
""")

    fd_setup = "".join(fd_setup)

    source = textwrap.indent(
        source,
        "    ",
    )

    malloc_setup = """
    malloc_strike_reset();
"""

    if malloc_fail_at is not None:
        malloc_setup += f"""
    malloc_strike_fail_at({malloc_fail_at});
"""

    return f"""
#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>

#include "malloc_strike.h"

{explicit_includes}

#define TEST_VALUE(name, format, value) \\
    dprintf({PROTOCOL_FD}, "TEST_VALUE %s " format "\\n", \\
        (name), (value))

#define TEST_BUFFER(name, buffer, size) do {{ \\
    dprintf({PROTOCOL_FD}, "TEST_BUFFER %s ", (name)); \\
    for (size_t __i = 0; __i < (size); __i++) \\
        dprintf( \\
            {PROTOCOL_FD}, \\
            "%02x", \\
            ((const unsigned char *)(buffer))[__i] \\
        ); \\
    dprintf({PROTOCOL_FD}, "\\n"); \\
}} while (0)

{explicit_functions}

static int __test_code(void)
{{
{source}
}}

int main(void)
{{
    int __protocol_fd;
    int __return_value;
    size_t __malloc_count;
    const char *__protocol_path;

    __protocol_path = "{_protocol_path_placeholder()}";

    __protocol_fd = open(
        __protocol_path,
        O_WRONLY | O_CREAT | O_TRUNC,
        0600
    );

    if (__protocol_fd < 0)
        return 100;

    if (dup2(__protocol_fd, {PROTOCOL_FD}) < 0)
    {{
        close(__protocol_fd);
        return 100;
    }}

    close(__protocol_fd);

{fd_setup}

{malloc_setup}

    __return_value = __test_code();

    __malloc_count = malloc_strike_count();

    dprintf(
        {PROTOCOL_FD},
        "MALLOC_COUNT %zu\\n",
        __malloc_count
    );

    for (size_t __i = 0; __i < __malloc_count; __i++)
    {{
        dprintf(
            {PROTOCOL_FD},
            "MALLOC %zu %zu\\n",
            __i,
            malloc_strike_size(__i)
        );
    }}

    dprintf(
        {PROTOCOL_FD},
        "RETURN %d\\n",
        __return_value
    );

    close({PROTOCOL_FD});

    return 0;
}}
"""


def _protocol_path_placeholder():
    return "__PROTOCOL_PATH__"


def _fd_path_placeholder(fd):
    return f"__FD_PATH_{fd}__"


class CContext:
    def __init__(
        self,
        project: Project,
        debug=False,
        asan=False,
    ):
        self.project = project
        self.project_dir = project.directory
        self.debug = debug
        self.asan = asan

    def include(self, *headers):
        return CCodeBuilder(
            self,
            headers,
        )

    def function(self, source):
        return CCodeBuilder(
            self,
            functions=[source],
        )

    def code(self, source):
        return CCodeBuilder(self).code(source)

    def program(self, executable):
        from .process import Program

        return Program(
            self.project_dir,
            executable,
        )

    def _execute_code(self, test):
        if self.project_dir is None:
            raise RuntimeError("project directory has not been set")

        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)

            harness = tmp / "test.c"
            executable = tmp / "test"
            protocol = tmp / "protocol"

            fd_paths = {fd: tmp / f"fd_{fd}" for fd in test._capture_fds}

            source = generate_code_harness(
                test.source,
                test.includes,
                test.functions,
                test._capture_fds,
                test.malloc_fail_at,
            )

            source = source.replace(
                _protocol_path_placeholder(),
                str(protocol),
            )

            for fd, path in fd_paths.items():
                source = source.replace(
                    _fd_path_placeholder(fd),
                    str(path),
                )

            harness.write_text(source)

            command = [
                "cc",
                "-g",
            ]

            if self.asan:
                command.extend(
                    [
                        "-fsanitize=address",
                        "-fno-omit-frame-pointer",
                    ]
                )

            for include in self.project.test.includes:
                command.extend(
                    [
                        "-I",
                        str(self.project_dir / include),
                    ]
                )

            command.extend(self.project.test.cflags)

            command.extend(
                [
                    "-I",
                    str(MALLOC_STRIKE_DIR),
                    str(harness),
                    str(MALLOC_STRIKE_SOURCE),
                    "-Wl,--wrap=malloc",
                ]
            )

            command.extend(self.project.test.link)

            command.extend(
                [
                    "-o",
                    str(executable),
                ]
            )

            result = subprocess.run(
                command,
                cwd=self.project_dir,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                if self.debug:
                    print()
                    print(
                        color(
                            "  [DEBUG] Compilation failed",
                            Color.YELLOW,
                        )
                    )
                    print(
                        color(
                            "  ────────────────────────────────────",
                            Color.YELLOW,
                        )
                    )
                    print(
                        "  "
                        + result.stderr.rstrip().replace(
                            "\n",
                            "\n  ",
                        )
                    )
                    print(
                        color(
                            "  ────────────────────────────────────",
                            Color.YELLOW,
                        )
                    )

                raise RuntimeError("test compilation failed:\n\n" + result.stderr)

            if self.debug:
                print()
                print(
                    color(
                        "  ──────────────────── C CODE " "────────────────────",
                        Color.YELLOW,
                    )
                )

                for line in source.splitlines():
                    print(
                        color(
                            "  " + line,
                            Color.YELLOW,
                        )
                    )

                print(
                    color(
                        "  ────────────────────────────────────────────────",
                        Color.YELLOW,
                    )
                )

            if self.debug:
                result = run_debug_process(
                    executable,
                    cwd=self.project_dir,
                )
            else:
                result = subprocess.run(
                    [str(executable)],
                    cwd=self.project_dir,
                    capture_output=True,
                )

            if result.returncode < 0:
                raise RuntimeError("C test crashed " f"(signal {-result.returncode})")

            if self.asan and (b"AddressSanitizer" in result.stderr):
                raise RuntimeError(
                    "AddressSanitizer reported an error:\n\n"
                    + result.stderr.decode(errors="replace")
                )

            if result.returncode != 0:
                raise RuntimeError(
                    "test harness failed " f"(exit code {result.returncode})"
                )

            if not protocol.exists():
                raise RuntimeError("test harness did not produce " "a protocol file")

            self._parse_protocol(
                test,
                protocol,
            )

            test._stdout = result.stdout
            test._stderr = result.stderr

            for fd, path in fd_paths.items():
                if path.exists():
                    test.fd_outputs[fd] = path.read_bytes()
                else:
                    test.fd_outputs[fd] = b""

    def _parse_protocol(self, test, protocol):
        malloc_count = None
        malloc_sizes = []
        return_value = None
        values = {}
        buffers = {}

        for line in protocol.read_text().splitlines():
            parts = line.split(maxsplit=2)

            if not parts:
                continue

            if parts[0] == "MALLOC_COUNT":
                if len(parts) != 2:
                    raise RuntimeError("invalid MALLOC_COUNT protocol line")

                malloc_count = int(parts[1])

            elif parts[0] == "MALLOC":
                if len(parts) != 3:
                    raise RuntimeError("invalid MALLOC protocol line")

                index = int(parts[1])
                size = int(parts[2])

                while len(malloc_sizes) <= index:
                    malloc_sizes.append(None)

                malloc_sizes[index] = size

            elif parts[0] == "TEST_VALUE":
                if len(parts) != 3:
                    raise RuntimeError("invalid TEST_VALUE protocol line")

                name = parts[1]
                value = parts[2]

                if name in values:
                    raise RuntimeError(f"value '{name}' was reported more than once")

                values[name] = value

            elif parts[0] == "TEST_BUFFER":
                if len(parts) not in (2, 3):
                    raise RuntimeError("invalid TEST_BUFFER protocol line")

                name = parts[1]
                data = parts[2] if len(parts) == 3 else ""

                if name in buffers:
                    raise RuntimeError(f"buffer '{name}' was reported more than once")

                try:
                    buffers[name] = bytes.fromhex(data)
                except ValueError:
                    raise RuntimeError(f"invalid TEST_BUFFER data for '{name}'")

            elif parts[0] == "RETURN":
                if len(parts) != 2:
                    raise RuntimeError("invalid RETURN protocol line")

                return_value = int(parts[1])

            else:
                raise RuntimeError(f"unknown protocol entry: {parts[0]}")

        if malloc_count is None:
            raise RuntimeError("protocol did not contain MALLOC_COUNT")

        if return_value is None:
            raise RuntimeError("protocol did not contain RETURN")

        if any(size is None for size in malloc_sizes):
            raise RuntimeError("protocol contains missing malloc entries")

        if len(malloc_sizes) != malloc_count:
            raise RuntimeError("malloc count does not match malloc entries")

        test.malloc_count = malloc_count
        test.malloc_sizes = malloc_sizes
        test.values = values
        test.buffers = buffers
        test.returncode = return_value
