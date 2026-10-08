import re
import shutil
import subprocess
from pathlib import Path

from .color import Color, color


class GFMNorminetteError(Exception):
    pass


def _run_make(
    project_dir: Path,
    target: str | None = None,
) -> subprocess.CompletedProcess:
    command = ["make"]

    if target:
        command.append(target)

    return subprocess.run(
        command,
        cwd=project_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def _find_makefile(
    project_dir: Path,
) -> Path | None:
    for name in ("Makefile", "makefile"):
        path = project_dir / name

        if path.is_file():
            return path

    return None


def _get_variable(
    makefile: str,
    name: str,
) -> str | None:
    pattern = rf"(?m)^[ \t]*{re.escape(name)}" rf"[ \t]*[?:+]?=[ \t]*(.*)$"

    match = re.search(pattern, makefile)

    if match is None:
        return None

    value = match.group(1).strip()

    if not value:
        return None

    return value


def _get_rules(
    makefile: str,
) -> list[tuple[int, str]]:
    rules = []

    for line_number, line in enumerate(
        makefile.splitlines(),
        start=1,
    ):
        if not line.strip():
            continue

        if line.lstrip().startswith("#"):
            continue

        # Recipe lines are not rules.
        if line.startswith("\t"):
            continue

        stripped = line.strip()

        if ":" not in stripped:
            continue

        target = stripped.split(":", 1)[0].strip()

        if not target:
            continue

        rules.append((line_number, target))

    return rules


def _has_rule(
    rules: list[tuple[int, str]],
    target: str,
) -> bool:
    for _, rule_target in rules:
        targets = rule_target.split()

        if target in targets:
            return True

    return False


def _has_name_rule(
    rules: list[tuple[int, str]],
) -> bool:
    for _, target in rules:
        targets = target.split()

        for rule_target in targets:
            if rule_target in (
                "$(NAME)",
                "${NAME}",
            ):
                return True

    return False


def _check_mandatory_rules(
    makefile: str,
) -> list[str]:
    errors = []

    rules = _get_rules(makefile)
    name = _get_variable(makefile, "NAME")

    if name is None:
        errors.append("III.11: missing mandatory '$(NAME)' variable")
    elif not _has_rule(rules, name):
        if not _has_name_rule(rules):
            errors.append("III.11: missing mandatory '$(NAME)' rule")

    for target in (
        "clean",
        "fclean",
        "re",
        "all",
    ):
        if not _has_rule(rules, target):
            errors.append(f"III.11: missing mandatory '{target}' rule")

    return errors


def _check_default_rule(
    makefile: str,
) -> list[str]:
    for line in makefile.splitlines():
        if not line.strip():
            continue

        if line.startswith("\t"):
            continue

        stripped = line.strip()

        if stripped.startswith("#"):
            continue

        # Variable assignment.
        if re.match(
            r"^[A-Za-z_][A-Za-z0-9_]*\s*(?::=|\+=|\?=|=)",
            stripped,
        ):
            continue

        # Make directives.
        if stripped.startswith(
            (
                "include ",
                "-include ",
                "sinclude ",
                "ifeq ",
                "ifneq ",
                "ifdef ",
                "ifndef ",
                "else",
                "endif",
                "define ",
                "endef",
            )
        ):
            continue

        if ":" not in stripped:
            continue

        target = stripped.split(":", 1)[0].strip()

        if target == "all":
            return []

        return [
            "III.11: the 'all' rule must be the "
            "default rule and therefore must be first"
        ]

    return ["III.11: Makefile contains no rules"]


def _check_source_wildcards(
    makefile: str,
) -> list[str]:
    errors = []

    for line_number, line in enumerate(
        makefile.splitlines(),
        start=1,
    ):
        stripped = line.strip()

        if not stripped:
            continue

        if stripped.startswith("#"):
            continue

        # $(wildcard *.c)
        if re.search(
            r"\$\(\s*wildcard\b",
            stripped,
        ):
            errors.append(
                "III.11: line "
                f"{line_number}: source files must be "
                "explicitly named; '$(wildcard ...)' "
                "is not allowed"
            )
            continue

        # Plain *.c / *.o style lists.
        #
        # Do not reject %.c / %.o because those are
        # Make pattern rules, not wildcard source lists.
        if re.search(
            r"(^|[ \t])\*[^ \t]*",
            stripped,
        ):
            if ":" not in stripped:
                errors.append(
                    "III.11: line "
                    f"{line_number}: source files must be "
                    "explicitly named; wildcard detected"
                )

    return errors


def _check_no_relink(
    project_dir: Path,
    makefile: str,
) -> list[str]:
    errors = []

    name = _get_variable(makefile, "NAME")

    if not name:
        return errors

    target = project_dir / name

    first = _run_make(project_dir)

    if first.returncode != 0:
        errors.append("III.11: unable to check relinking because " "'make' failed")
        return errors

    if not target.exists():
        errors.append(f"III.11: target '{name}' was not created " "when running 'make'")
        return errors

    first_mtime = target.stat().st_mtime_ns

    second = _run_make(project_dir)

    if second.returncode != 0:
        errors.append(
            "III.11: unable to check relinking because " "the second 'make' failed"
        )
        return errors

    second_mtime = target.stat().st_mtime_ns

    if first_mtime != second_mtime:
        errors.append(
            f"III.11: Makefile relinks '{name}' " "when relinking is not necessary"
        )

    return errors


def _check_makefile(
    project_dir: Path,
    makefile: Path,
) -> list[str]:
    try:
        makefile_text = makefile.read_text()
    except OSError as error:
        raise GFMNorminetteError(f"cannot read {makefile.name}: {error}") from error

    errors = []

    errors.extend(
        _check_mandatory_rules(
            makefile_text,
        )
    )

    errors.extend(
        _check_default_rule(
            makefile_text,
        )
    )

    errors.extend(
        _check_source_wildcards(
            makefile_text,
        )
    )

    errors.extend(
        _check_no_relink(
            project_dir,
            makefile_text,
        )
    )

    return errors


def run_gfm_norminette(
    project_dir: Path,
) -> bool:
    makefile = _find_makefile(project_dir)

    if makefile is None:
        return True

    if shutil.which("make") is None:
        raise GFMNorminetteError("make was not found in PATH")

    print(
        color(
            "GFM-Norminette",
            Color.BOLD,
            Color.CYAN,
        )
    )

    print(
        color(
            f"Checking {makefile.name}...",
            Color.YELLOW,
        )
    )

    errors = _check_makefile(
        project_dir,
        makefile,
    )

    if errors:
        for error in errors:
            print(f"  {color('[FAIL]', Color.RED)} " f"{error}")

        return False

    print(f"  {color('[PASS]', Color.GREEN)} " "III.11 Makefile")

    return True
