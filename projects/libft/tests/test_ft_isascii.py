from framework import TestSuite

suite = TestSuite("ft_isascii")


def compare(c, argument, expected):
    test = c.include("libft.h", "ctype.h").code(f"""
        int ft = ft_isascii({argument});
        int libc = !!isascii({argument});

        TEST_VALUE("ft", "%d", ft);
        TEST_VALUE("libc", "%d", libc);

        return 0;
    """)

    test.value("ft").equals(
        str(expected),
        "Test ft_isascii() returned value",
    )

    test.value("libc").equals(
        str(expected),
        "Reference value from isascii()",
    ).reference()

    test.malloc.count(
        0,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("0 is ASCII")
def test_lower_bound(c):
    compare(c, "0", 1)


@suite.case("127 is ASCII")
def test_upper_bound(c):
    compare(c, "127", 1)


@suite.case("'A' is ASCII")
def test_uppercase(c):
    compare(c, "'A'", 1)


@suite.case("'z' is ASCII")
def test_lowercase(c):
    compare(c, "'z'", 1)


@suite.case("'0' is ASCII")
def test_digit(c):
    compare(c, "'0'", 1)


@suite.case("' ' is ASCII")
def test_space(c):
    compare(c, "' '", 1)


@suite.case("'\\n' is ASCII")
def test_newline(c):
    compare(c, "'\\n'", 1)


@suite.case("'\\t' is ASCII")
def test_tab(c):
    compare(c, "'\\t'", 1)


@suite.case("'~' is ASCII")
def test_tilde(c):
    compare(c, "'~'", 1)


@suite.case("-1 is not ASCII")
def test_negative(c):
    compare(c, "-1", 0)


@suite.case("128 is not ASCII")
def test_128(c):
    compare(c, "128", 0)


@suite.case("255 is not ASCII")
def test_255(c):
    compare(c, "255", 0)


@suite.case("256 is not ASCII")
def test_256(c):
    compare(c, "256", 0)
