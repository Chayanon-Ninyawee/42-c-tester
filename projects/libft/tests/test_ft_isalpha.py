from framework import TestSuite

suite = TestSuite("ft_isalpha")


def compare(c, argument, expected):
    ft = c.ft_isalpha(argument)

    libc = c.isalpha(argument)
    # NOTE: this is because some libc implementation will return other non-zero int instead of 1
    libc_value = int(bool(libc.return_type.parse(libc.value)))

    libc.value_equals(
        libc_value,
        expected,
        "Test with isalpha() from libc",
    ).assert_reference()

    ft.equals(
        expected,
        "Test with value",
    ).assert_now()


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
