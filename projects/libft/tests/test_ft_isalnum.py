from framework import TestSuite

suite = TestSuite("ft_isalnum")


def compare(c, argument, expected):
    ft = c.ft_isalnum(argument)

    libc = c.isalnum(argument)
    # NOTE: this is because some libc implementation will return other non-zero int instead of 1
    libc_value = int(bool(libc.return_type.parse(libc.value)))

    libc.value_equals(
        libc_value,
        expected,
        "Test with isalnum() from libc",
    ).assert_reference()

    ft.equals(
        expected,
        "Test with value",
    ).assert_now()


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
