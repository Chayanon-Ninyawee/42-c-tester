from framework import BuildConfig, Project, TestConfig

project = Project(
    name="get_next_line",
    build=BuildConfig(
        method="cc",
        compiler="cc",
        compile_only=True,
        flags=[
            "-Wall",
            "-Wextra",
            "-Werror",
            "-D",
            "BUFFER_SIZE=42",
        ],
        sources=[
            "get_next_line.c",
            "get_next_line_utils.c",
        ],
    ),
    test=TestConfig(
        includes=["."],
        link=[
            "get_next_line.c",
            "get_next_line_utils.c",
        ],
    ),
    tests=["get_next_line"],
)
