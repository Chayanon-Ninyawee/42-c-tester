from framework import TestSuite

suite = TestSuite("ft_isprint")


def compare(c, argument, expected):
    ft = c.ft_isprint(argument)

    libc = c.isprint(argument)
    # NOTE: this is because some libc implementation will return other non-zero int instead of 1
    libc_value = int(bool(libc.return_type.parse(libc.value)))

    ft.equals(
        expected,
        "Test with value",
    )

    ft.equals(
        libc_value,
        f"Test with isprint({argument}) from libc",
    ).assert_now()


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
