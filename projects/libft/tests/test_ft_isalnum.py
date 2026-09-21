from framework import TestSuite

suite = TestSuite("ft_isalnum")


def compare(c, argument, expected):
    test = c.include("libft.h", "ctype.h").code(f"""
        int ft = ft_isalnum({argument});
        int libc = !!isalnum({argument});

        TEST_VALUE("ft", "%d", ft);
        TEST_VALUE("libc", "%d", libc);

        return 0;
    """)

    test.value("ft").equals(
        str(expected),
        "Test ft_isalnum() returned value",
    )

    test.value("libc").equals(
        str(expected),
        "Reference value from isalnum()",
    ).reference()

    test.malloc.count(
        0,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("'A' is alphanumeric")
def test_uppercase_start(c):
    compare(c, "'A'", 1)


@suite.case("'Z' is alphanumeric")
def test_uppercase_end(c):
    compare(c, "'Z'", 1)


@suite.case("'a' is alphanumeric")
def test_lowercase_start(c):
    compare(c, "'a'", 1)


@suite.case("'z' is alphanumeric")
def test_lowercase_end(c):
    compare(c, "'z'", 1)


@suite.case("'0' is alphanumeric")
def test_digit_start(c):
    compare(c, "'0'", 1)


@suite.case("'9' is alphanumeric")
def test_digit_end(c):
    compare(c, "'9'", 1)


@suite.case("'/' is not alphanumeric")
def test_before_digits(c):
    compare(c, "'/'", 0)


@suite.case("':' is not alphanumeric")
def test_after_digits(c):
    compare(c, "':'", 0)


@suite.case("'[' is not alphanumeric")
def test_after_uppercase(c):
    compare(c, "'['", 0)


@suite.case("'`' is not alphanumeric")
def test_before_lowercase(c):
    compare(c, "'`'", 0)


@suite.case("'{' is not alphanumeric")
def test_after_lowercase(c):
    compare(c, "'{'", 0)


@suite.case("' ' is not alphanumeric")
def test_space(c):
    compare(c, "' '", 0)


@suite.case("'!' is not alphanumeric")
def test_punctuation(c):
    compare(c, "'!'", 0)


@suite.case("-1 is not alphanumeric")
def test_negative(c):
    compare(c, "-1", 0)


@suite.case("127 is not alphanumeric")
def test_127(c):
    compare(c, "127", 0)
