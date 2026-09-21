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
class TestConfig:
    includes: list[str] = field(default_factory=list)
    cflags: list[str] = field(default_factory=list)
    link: list[str] = field(default_factory=list)


@dataclass
class Project:
    name: str
    build: BuildConfig
    test: TestConfig = field(default_factory=TestConfig)
    tests: list[str] = field(default_factory=list)
    directory: Path | None = None
