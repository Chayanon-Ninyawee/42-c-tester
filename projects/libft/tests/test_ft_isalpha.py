from framework import TestSuite

suite = TestSuite("ft_isalpha")


def compare(c, argument, expected):
    test = c.include("libft.h", "ctype.h").code(f"""
        int ft = ft_isalpha({argument});
        int libc = !!isalpha({argument});

        TEST_VALUE("ft", "%d", ft);
        TEST_VALUE("libc", "%d", libc);

        return 0;
    """)

    test.value("ft").equals(
        str(expected),
        "Test ft_isalpha() returned value",
    )

    test.value("libc").equals(
        str(expected),
        "Reference value from isalpha()",
    ).reference()

    test.malloc.count(0)

    test.assert_now()


@suite.case("'A' is alphabetic")
def test_uppercase_start(c):
    compare(c, "'A'", 1)


@suite.case("'Z' is alphabetic")
def test_uppercase_end(c):
    compare(c, "'Z'", 1)


@suite.case("'a' is alphabetic")
def test_lowercase_start(c):
    compare(c, "'a'", 1)


@suite.case("'z' is alphabetic")
def test_lowercase_end(c):
    compare(c, "'z'", 1)


@suite.case("'[' is not alphabetic")
def test_after_uppercase(c):
    compare(c, "'['", 0)


@suite.case("'`' is not alphabetic")
def test_before_lowercase(c):
    compare(c, "'`'", 0)


@suite.case("'{' is not alphabetic")
def test_after_lowercase(c):
    compare(c, "'{'", 0)


@suite.case("'0' is not alphabetic")
def test_digit(c):
    compare(c, "'0'", 0)


@suite.case("'9' is not alphabetic")
def test_digit_end(c):
    compare(c, "'9'", 0)


@suite.case("' ' is not alphabetic")
def test_space(c):
    compare(c, "' '", 0)


@suite.case("'\\t' is not alphabetic")
def test_tab(c):
    compare(c, "'\\t'", 0)


@suite.case("'\\n' is not alphabetic")
def test_newline(c):
    compare(c, "'\\n'", 0)


@suite.case("'!' is not alphabetic")
def test_punctuation(c):
    compare(c, "'!'", 0)


@suite.case("'@' is not alphabetic")
def test_symbol(c):
    compare(c, "'@'", 0)


@suite.case("-1 is not alphabetic")
def test_negative(c):
    compare(c, "-1", 0)


@suite.case("127 is not alphabetic")
def test_del(c):
    compare(c, "127", 0)
