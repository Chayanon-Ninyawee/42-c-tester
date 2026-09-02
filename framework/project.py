from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class BuildConfig:
    method: str = "make"

    # make
    target: str | None = None

    # cc
    compiler: str = "cc"
    flags: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    output: str = "a.out"


@dataclass
class FunctionDefinition:
    returns: str = "int"
    args: list[str] = field(default_factory=list)


@dataclass
class FunctionConfig:
    """
    Configuration used when compiling generated C function
    test harnesses.

    link:
        Files to link against the generated harness.

        Example:
            ["libft.a"]

    includes:
        Include directories available to the harness.

        Example:
            ["."]

    cflags:
        Additional compiler flags.
    """

    functions: dict[str, FunctionDefinition] = field(default_factory=dict)

    link: list[str] = field(default_factory=list)
    includes: list[str] = field(default_factory=list)
    cflags: list[str] = field(default_factory=list)


@dataclass
class Project:
    name: str
    build: BuildConfig

    functions: FunctionConfig | None = None

    tests: list[str] = field(default_factory=list)

    directory: Path | None = None
