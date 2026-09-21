from framework import TestSuite

suite = TestSuite("ft_isprint")


def compare(c, argument, expected):
    test = c.include("libft.h", "ctype.h").code(f"""
        int ft = ft_isprint({argument});
        int libc = !!isprint({argument});

        TEST_VALUE("ft", "%d", ft);
        TEST_VALUE("libc", "%d", libc);

        return 0;
    """)

    test.value("ft").equals(
        str(expected),
        "Test ft_isprint() returned value",
    )

    test.value("libc").equals(
        str(expected),
        "Reference value from isprint()",
    ).reference()

    test.malloc.count(
        0,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("32 is printable")
def test_lower_bound(c):
    compare(c, "32", 1)


@suite.case("126 is printable")
def test_upper_bound(c):
    compare(c, "126", 1)


@suite.case("' ' is printable")
def test_space(c):
    compare(c, "' '", 1)


@suite.case("'!' is printable")
def test_exclamation(c):
    compare(c, "'!'", 1)


@suite.case("'A' is printable")
def test_uppercase(c):
    compare(c, "'A'", 1)


@suite.case("'z' is printable")
def test_lowercase(c):
    compare(c, "'z'", 1)


@suite.case("'0' is printable")
def test_digit(c):
    compare(c, "'0'", 1)


@suite.case("'~' is printable")
def test_tilde(c):
    compare(c, "'~'", 1)


@suite.case("31 is not printable")
def test_before_lower_bound(c):
    compare(c, "31", 0)


@suite.case("127 is not printable")
def test_after_upper_bound(c):
    compare(c, "127", 0)


@suite.case("0 is not printable")
def test_null(c):
    compare(c, "0", 0)


@suite.case("'\\n' is not printable")
def test_newline(c):
    compare(c, "'\\n'", 0)


@suite.case("'\\t' is not printable")
def test_tab(c):
    compare(c, "'\\t'", 0)


@suite.case("-1 is not printable")
def test_negative(c):
    compare(c, "-1", 0)


@suite.case("128 is not printable")
def test_128(c):
    compare(c, "128", 0)


@suite.case("255 is not printable")
def test_255(c):
    compare(c, "255", 0)
