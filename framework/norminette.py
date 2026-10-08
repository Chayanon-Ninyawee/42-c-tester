import shutil
import subprocess
from pathlib import Path

from .color import Color, color


class NorminetteError(Exception):
    pass


def run_norminette(
    project_dir: Path,
    paths: list[str],
) -> None:
    if shutil.which("norminette") is None:
        raise NorminetteError("norminette was not found in PATH")

    command = ["norminette", *paths]

    print(color("$ " + " ".join(command), Color.YELLOW))

    result = subprocess.run(
        command,
        cwd=project_dir,
    )

    if result.returncode != 0:
        raise NorminetteError("norminette failed " f"(exit code {result.returncode})")
