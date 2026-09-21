from framework import TestSuite

suite = TestSuite("ft_isdigit")


def compare(c, argument, expected):
    test = c.include("libft.h", "ctype.h").code(f"""
        int ft = ft_isdigit({argument});
        int libc = !!isdigit({argument});

        TEST_VALUE("ft", "%d", ft);
        TEST_VALUE("libc", "%d", libc);

        return 0;
    """)

    test.value("ft").equals(
        str(expected),
        "Test ft_isdigit() returned value",
    )

    test.value("libc").equals(
        str(expected),
        "Reference value from isdigit()",
    ).reference()

    test.malloc.count(
        0,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("'0' is a digit")
def test_zero(c):
    compare(c, "'0'", 1)


@suite.case("'9' is a digit")
def test_nine(c):
    compare(c, "'9'", 1)


@suite.case("'1' is a digit")
def test_one(c):
    compare(c, "'1'", 1)


@suite.case("'5' is a digit")
def test_middle(c):
    compare(c, "'5'", 1)


@suite.case("':' is not a digit")
def test_after_digits(c):
    compare(c, "':'", 0)


@suite.case("'/' is not a digit")
def test_before_digits(c):
    compare(c, "'/'", 0)


@suite.case("'A' is not a digit")
def test_uppercase(c):
    compare(c, "'A'", 0)


@suite.case("'a' is not a digit")
def test_lowercase(c):
    compare(c, "'a'", 0)


@suite.case("' ' is not a digit")
def test_space(c):
    compare(c, "' '", 0)


@suite.case("'!' is not a digit")
def test_punctuation(c):
    compare(c, "'!'", 0)


@suite.case("-1 is not a digit")
def test_negative(c):
    compare(c, "-1", 0)


@suite.case("127 is not a digit")
def test_127(c):
    compare(c, "127", 0)


@suite.case("128 is not a digit")
def test_128(c):
    compare(c, "128", 0)
