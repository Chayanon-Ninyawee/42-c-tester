from framework import BuildConfig, FunctionConfig, FunctionDefinition, Project

project = Project(
    name="libft",
    build=BuildConfig(
        method="make",
        target="all",
    ),
    functions=FunctionConfig(
        functions={
            "ft_isalpha": FunctionDefinition(
                returns="int",
                args=["int"],
            ),
            "ft_isdigit": FunctionDefinition(
                returns="int",
                args=["int"],
            ),
            "ft_isalnum": FunctionDefinition(
                returns="int",
                args=["int"],
            ),
            "ft_isascii": FunctionDefinition(
                returns="int",
                args=["int"],
            ),
            "ft_isprint": FunctionDefinition(
                returns="int",
                args=["int"],
            ),
            "ft_strlen": FunctionDefinition(
                returns="size_t",
                args=["const char *"],
            ),
            "ft_memset": FunctionDefinition(
                returns="void *",
                args=["void *", "int", "size_t"],
            ),
            "ft_bzero": FunctionDefinition(
                returns="void",
                args=["void *", "size_t"],
            ),
        },
        link=[
            "libft.a",
        ],
        includes=[
            ".",
        ],
    ),
    tests=[
        "ft_isalpha",
        "ft_isdigit",
        "ft_isalnum",
        "ft_isascii",
        "ft_isprint",
        "ft_strlen",
        "ft_memset",
        "ft_bzero",
    ],
)
