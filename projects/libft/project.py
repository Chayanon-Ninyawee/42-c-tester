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
            # strlcpy
            "ft_strlcpy": FunctionDefinition(
                returns="size_t",
                args=["char *", "const char *", "size_t"],
            ),
            "strlcpy": FunctionDefinition(
                returns="size_t",
                args=["char *", "const char *", "size_t"],
                headers=["bsd/string.h"],
                link=["bsd"],
            ),
            # strlcat
            "ft_strlcat": FunctionDefinition(
                returns="size_t",
                args=["char *", "const char *", "size_t"],
            ),
            "strlcat": FunctionDefinition(
                returns="size_t",
                args=["char *", "const char *", "size_t"],
                headers=["bsd/string.h"],
                link=["bsd"],
            ),
            # toupper
            "ft_toupper": FunctionDefinition(
                returns="int",
                args=["int"],
            ),
            "toupper": FunctionDefinition(
                returns="int",
                args=["int"],
                headers=["ctype.h"],
            ),
            # tolower
            "ft_tolower": FunctionDefinition(
                returns="int",
                args=["int"],
            ),
            "tolower": FunctionDefinition(
                returns="int",
                args=["int"],
                headers=["ctype.h"],
            ),
            # strchr
            "ft_strchr": FunctionDefinition(
                returns="char *",
                args=["const char *", "int"],
            ),
            "strchr": FunctionDefinition(
                returns="char *",
                args=["const char *", "int"],
                headers=["string.h"],
            ),
            # strrchr
            "ft_strrchr": FunctionDefinition(
                returns="char *",
                args=["const char *", "int"],
            ),
            "strrchr": FunctionDefinition(
                returns="char *",
                args=["const char *", "int"],
                headers=["string.h"],
            ),
            # strncmp
            "ft_strncmp": FunctionDefinition(
                returns="int",
                args=["const char *", "const char *", "size_t"],
            ),
            "strncmp": FunctionDefinition(
                returns="int",
                args=["const char *", "const char *", "size_t"],
                headers=["string.h"],
            ),
            # memchr
            "ft_memchr": FunctionDefinition(
                returns="void *",
                args=["const void *", "int", "size_t"],
            ),
            "memchr": FunctionDefinition(
                returns="void *",
                args=["const void *", "int", "size_t"],
                headers=["string.h"],
            ),
            # memcmp
            "ft_memcmp": FunctionDefinition(
                returns="int",
                args=["const void *", "const void *", "size_t"],
            ),
            "memcmp": FunctionDefinition(
                returns="int",
                args=["const void *", "const void *", "size_t"],
                headers=["string.h"],
            ),
            # strnstr
            "ft_strnstr": FunctionDefinition(
                returns="char *",
                args=["const char *", "const char *", "size_t"],
            ),
            "strnstr": FunctionDefinition(
                returns="char *",
                args=["const char *", "const char *", "size_t"],
                headers=["bsd/string.h"],
                link=["bsd"],
            ),
            # atoi
            "ft_atoi": FunctionDefinition(
                returns="int",
                args=["const char *"],
            ),
            "atoi": FunctionDefinition(
                returns="int",
                args=["const char *"],
                headers=["stdlib.h"],
            ),
            # calloc
            "ft_calloc": FunctionDefinition(
                returns="void *",
                args=["size_t", "size_t"],
            ),
            "calloc": FunctionDefinition(
                returns="void *",
                args=["size_t", "size_t"],
                headers=["stdlib.h"],
                err_flags=False,
            ),
            # strdup
            "ft_strdup": FunctionDefinition(
                returns="char *",
                args=["const char *"],
            ),
            "strdup": FunctionDefinition(
                returns="char *",
                args=["const char *"],
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
        "ft_strlcpy",
        "ft_strlcat",
        "ft_toupper",
        "ft_tolower",
        "ft_tolower",
        "ft_strchr",
        "ft_strrchr",
        "ft_strncmp",
        "ft_memchr",
        "ft_memcmp",
        "ft_strnstr",
        "ft_atoi",
        "ft_calloc",
        "ft_strdup",
    ],
)
