import os
import shutil
import signal
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .result import AssertionFailure


class OutputValue:
    def __init__(
        self,
        value: str,
        label: str,
    ):
        self.value = value
        self.label = label

    def equals(self, expected: str):
        if self.value != expected:
            raise AssertionFailure(
                f"{self.label} mismatch\n"
                f"  expected: {expected!r}\n"
                f"  received: {self.value!r}"
            )

        return self

    def contains(self, expected: str):
        if expected not in self.value:
            raise AssertionFailure(
                f"{self.label} does not contain "
                f"{expected!r}\n"
                f"  received: {self.value!r}"
            )

        return self

    def is_empty(self):
        return self.equals("")

    def is_not_empty(self):
        if self.value == "":
            raise AssertionFailure(f"{self.label} is empty")

        return self


class BytesValue:
    def __init__(
        self,
        value: bytes,
        label: str,
    ):
        self.value = value
        self.label = label

    def equals(self, expected: bytes):
        if self.value != expected:
            raise AssertionFailure(
                f"{self.label} mismatch\n"
                f"  expected: {expected!r}\n"
                f"  received: {self.value!r}"
            )

        return self


class ExitCodeValue:
    def __init__(self, value: int | None):
        self.value = value

    def equals(self, expected: int):
        if self.value != expected:
            raise AssertionFailure(
                f"exit code mismatch\n"
                f"  expected: {expected}\n"
                f"  received: {self.value}"
            )

        return self

    def is_zero(self):
        return self.equals(0)

    def is_nonzero(self):
        if self.value == 0:
            raise AssertionFailure("expected a non-zero exit code")

        return self


class FileValue:
    def __init__(self, path: Path):
        self.path = path

    def exists(self):
        if not self.path.exists():
            raise AssertionFailure(f"file does not exist: {self.path}")

        return self

    def not_exists(self):
        if self.path.exists():
            raise AssertionFailure(f"file unexpectedly exists: {self.path}")

        return self

    def equals(self, expected: str):
        self.exists()

        actual = self.path.read_text()

        if actual != expected:
            raise AssertionFailure(
                f"file mismatch: {self.path.name}\n"
                f"  expected: {expected!r}\n"
                f"  received: {actual!r}"
            )

        return self

    def equals_bytes(self, expected: bytes):
        self.exists()

        actual = self.path.read_bytes()

        if actual != expected:
            raise AssertionFailure(
                f"file mismatch: {self.path.name}\n"
                f"  expected: {expected!r}\n"
                f"  received: {actual!r}"
            )

        return self


@dataclass
class ExecutionResult:
    returncode: int | None
    stdout_data: bytes
    stderr_data: bytes
    timed_out: bool
    cwd: Path

    @property
    def stdout(self):
        return OutputValue(
            self.stdout_data.decode(errors="replace"),
            "stdout",
        )

    @property
    def stderr(self):
        return OutputValue(
            self.stderr_data.decode(errors="replace"),
            "stderr",
        )

    @property
    def stdout_bytes(self):
        return BytesValue(
            self.stdout_data,
            "stdout",
        )

    @property
    def stderr_bytes(self):
        return BytesValue(
            self.stderr_data,
            "stderr",
        )

    @property
    def exit_code(self):
        return ExitCodeValue(self.returncode)

    def crashed(self):
        if self.timed_out:
            raise AssertionFailure("process timed out")

        if self.returncode is None:
            raise AssertionFailure("process did not return")

        if self.returncode >= 0:
            raise AssertionFailure(
                f"process exited normally with " f"code {self.returncode}"
            )

        signal_name = signal.Signals(-self.returncode).name

        raise AssertionFailure(f"process crashed with {signal_name}")

    def did_not_crash(self):
        if self.returncode is not None and self.returncode < 0:
            signal_name = signal.Signals(-self.returncode).name

            raise AssertionFailure(f"process crashed with {signal_name}")

        return self

    def timed_out_assert(self):
        if not self.timed_out:
            raise AssertionFailure("process did not time out")

        return self

    def file(self, path: str):
        return FileValue(self.cwd / path)


class Program:
    def __init__(
        self,
        project_dir: Path,
        executable: str,
    ):
        self.project_dir = project_dir
        self.executable = executable

    def run(
        self,
        *,
        args: list[str] | None = None,
        stdin: str | bytes | None = None,
        files: dict[str, str | bytes] | None = None,
        cwd: str | None = None,
        env: dict[str, str] | None = None,
        timeout: float = 5.0,
    ) -> ExecutionResult:

        args = args or []
        files = files or {}

        sandbox = Path(tempfile.mkdtemp(prefix="test-42-c-"))

        for relative, data in files.items():
            path = sandbox / relative
            path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            if isinstance(data, bytes):
                path.write_bytes(data)
            else:
                path.write_text(data)

        workdir = sandbox

        if cwd:
            workdir = sandbox / cwd
            workdir.mkdir(
                parents=True,
                exist_ok=True,
            )

        executable = Path(self.executable)

        if not executable.is_absolute():
            executable = self.project_dir / executable

        command = [
            str(executable),
            *args,
        ]

        process_env = os.environ.copy()

        if env:
            process_env.update(env)

        try:
            completed = subprocess.run(
                command,
                input=stdin,
                capture_output=True,
                cwd=workdir,
                env=process_env,
                timeout=timeout,
            )

            return ExecutionResult(
                returncode=completed.returncode,
                stdout_data=completed.stdout,
                stderr_data=completed.stderr,
                timed_out=False,
                cwd=sandbox,
            )

        except subprocess.TimeoutExpired as error:
            stdout = error.stdout or b""
            stderr = error.stderr or b""

            if isinstance(stdout, str):
                stdout = stdout.encode()

            if isinstance(stderr, str):
                stderr = stderr.encode()

            return ExecutionResult(
                returncode=None,
                stdout_data=stdout,
                stderr_data=stderr,
                timed_out=True,
                cwd=sandbox,
            )
