from framework import TestSuite

suite = TestSuite("ft_isascii")


def compare(c, argument, expected):
    ft = c.ft_isascii(argument)

    libc = c.isascii(argument)
    # NOTE: this is because some libc implementation will return other non-zero int instead of 1
    libc_value = int(bool(libc.return_type.parse(libc.value)))

    ft.equals(
        expected,
        "Test with value",
    )

    ft.equals(
        libc_value,
        f"Test with isascii({argument}) from libc",
    ).assert_now()


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
