from framework import TestSuite

suite = TestSuite("ft_isdigit")


def compare(c, argument, expected):
    ft = c.ft_isdigit(argument)

    libc = c.isdigit(argument)
    # NOTE: this is because some libc implementation will return other non-zero int instead of 1
    libc_value = int(bool(libc.return_type.parse(libc.value)))

    libc.value_equals(
        libc_value,
        expected,
        "Test with isdigit() from libc",
    ).assert_reference()

    ft.equals(
        expected,
        "Test with value",
    ).assert_now()


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
