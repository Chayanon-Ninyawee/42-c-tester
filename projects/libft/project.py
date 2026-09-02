from framework import BuildConfig, FunctionConfig, FunctionDefinition, Project

project = Project(
    name="libft",
    build=BuildConfig(
        method="make",
        target="all",
    ),
    functions=FunctionConfig(
        functions={
            # isalpha
            "ft_isalpha": FunctionDefinition(
                returns="int",
                args=["int"],
            ),
            "isalpha": FunctionDefinition(
                returns="int",
                args=["int"],
                headers=["ctype.h"],
            ),
            # isdigit
            "ft_isdigit": FunctionDefinition(
                returns="int",
                args=["int"],
            ),
            "isdigit": FunctionDefinition(
                returns="int",
                args=["int"],
                headers=["ctype.h"],
            ),
            # isalnum
            "ft_isalnum": FunctionDefinition(
                returns="int",
                args=["int"],
            ),
            "isalnum": FunctionDefinition(
                returns="int",
                args=["int"],
                headers=["ctype.h"],
            ),
            # isascii
            "ft_isascii": FunctionDefinition(
                returns="int",
                args=["int"],
            ),
            "isascii": FunctionDefinition(
                returns="int",
                args=["int"],
                headers=["ctype.h"],
            ),
            # isprint
            "ft_isprint": FunctionDefinition(
                returns="int",
                args=["int"],
            ),
            "isprint": FunctionDefinition(
                returns="int",
                args=["int"],
                headers=["ctype.h"],
            ),
            # strlen
            "ft_strlen": FunctionDefinition(
                returns="size_t",
                args=["const char *"],
            ),
            "strlen": FunctionDefinition(
                returns="size_t",
                args=["const char *"],
                headers=["string.h"],
            ),
            # memset
            "ft_memset": FunctionDefinition(
                returns="void *",
                args=["void *", "int", "size_t"],
            ),
            "memset": FunctionDefinition(
                returns="void *",
                args=["void *", "int", "size_t"],
                headers=["string.h"],
                err_flags=False,
            ),
            # bzero
            "ft_bzero": FunctionDefinition(
                returns="void",
                args=["void *", "size_t"],
            ),
            "bzero": FunctionDefinition(
                returns="void",
                args=["void *", "size_t"],
                headers=["string.h"],
            ),
            # memcpy
            "ft_memcpy": FunctionDefinition(
                returns="void *",
                args=["void *", "const void *", "size_t"],
            ),
            "memcpy": FunctionDefinition(
                returns="void *",
                args=["void *", "const void *", "size_t"],
                headers=["string.h"],
            ),
            # memmove
            "ft_memmove": FunctionDefinition(
                returns="void *",
                args=["void *", "const void *", "size_t"],
            ),
            "memmove": FunctionDefinition(
                returns="void *",
                args=["void *", "const void *", "size_t"],
                headers=["string.h"],
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
        "ft_memcpy",
        "ft_memmove",
    ],
)
