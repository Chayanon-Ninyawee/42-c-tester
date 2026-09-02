import shutil
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path

from .color import Color, color
from .project import BuildConfig


class BuildError(Exception):
    pass


class Builder(ABC):
    def __init__(
        self,
        project_dir: Path,
        config: BuildConfig,
    ):
        self.project_dir = project_dir
        self.config = config

    @abstractmethod
    def build(self) -> Path | None:
        raise NotImplementedError


class MakeBuilder(Builder):
    def build(self) -> Path | None:
        if shutil.which("make") is None:
            raise BuildError("make was not found in PATH")

        command = ["make"]

        if self.config.target:
            command.append(self.config.target)

        print(
            color(
                "$ " + " ".join(command),
                Color.YELLOW,
            )
        )

        result = subprocess.run(
            command,
            cwd=self.project_dir,
        )

        if result.returncode != 0:
            raise BuildError(f"make failed " f"(exit code {result.returncode})")

        return None


class CCBuilder(Builder):
    def build(self) -> Path:
        if shutil.which(self.config.compiler) is None:
            raise BuildError(
                f"compiler '{self.config.compiler}' " "was not found in PATH"
            )

        output = self.project_dir / self.config.output

        command = [
            self.config.compiler,
            *self.config.flags,
            *self.config.sources,
            "-o",
            str(output),
        ]

        print(
            color(
                "$ " + " ".join(command),
                Color.YELLOW,
            )
        )

        result = subprocess.run(
            command,
            cwd=self.project_dir,
        )

        if result.returncode != 0:
            raise BuildError(
                f"{self.config.compiler} failed " f"(exit code {result.returncode})"
            )

        return output


def create_builder(
    project_dir: Path,
    config: BuildConfig,
) -> Builder:

    if config.method == "make":
        return MakeBuilder(project_dir, config)

    if config.method == "cc":
        return CCBuilder(project_dir, config)

    raise ValueError(f"Unknown build method: {config.method}")
