from framework import TestSuite

suite = TestSuite("ft_atoi")


def compare(c, original, expected):
    ft_buffer = c.buffer(
        original,
        size=len(original),
        type="char",
        name="ft",
    )

    libc_buffer = c.buffer(
        original,
        size=len(original),
        type="char",
        name="libc",
    )

    ft = c.ft_atoi(
        ft_buffer,
    )

    libc = c.atoi(
        libc_buffer,
    )

    libc.equals(
        expected,
        "Test with atoi() from libc",
    )
    libc.buffer_equals(
        libc_buffer,
        original,
        "Input buffer was modified by libc",
    ).assert_reference()

    ft.equals(
        expected,
        "Test with value",
    )
    ft.buffer_equals(
        ft_buffer,
        original,
        "Input buffer was modified",
    )
    ft.malloc_count_equals(
        0,
        "Test malloc count",
    ).assert_now()


@suite.case("positive number")
def test_positive(c):
    original = b"12345\x00"
    expected = 12345

    compare(c, original, expected)


@suite.case("negative number")
def test_negative(c):
    original = b"-12345\x00"
    expected = -12345

    compare(c, original, expected)


@suite.case("leading whitespace")
def test_leading_whitespace(c):
    original = b"   12345\x00"
    expected = 12345

    compare(c, original, expected)


@suite.case("leading tabs and spaces")
def test_leading_tabs(c):
    original = b"\t\n\v\f\r  42\x00"
    expected = 42

    compare(c, original, expected)


@suite.case("plus sign")
def test_plus(c):
    original = b"+42\x00"
    expected = 42

    compare(c, original, expected)


@suite.case("minus sign")
def test_minus(c):
    original = b"-42\x00"
    expected = -42

    compare(c, original, expected)


@suite.case("plus followed by number")
def test_plus_number(c):
    original = b"+123\x00"
    expected = 123

    compare(c, original, expected)


@suite.case("minus followed by number")
def test_minus_number(c):
    original = b"-123\x00"
    expected = -123

    compare(c, original, expected)


@suite.case("zero")
def test_zero(c):
    original = b"0\x00"
    expected = 0

    compare(c, original, expected)


@suite.case("leading zeros")
def test_leading_zeros(c):
    original = b"00000123\x00"
    expected = 123

    compare(c, original, expected)


@suite.case("stops at non-digit")
def test_stops_at_non_digit(c):
    original = b"123abc\x00"
    expected = 123

    compare(c, original, expected)


@suite.case("stops at whitespace")
def test_stops_at_whitespace(c):
    original = b"123 456\x00"
    expected = 123

    compare(c, original, expected)


@suite.case("whitespace after sign")
def test_whitespace_after_sign(c):
    original = b"+ 123\x00"
    expected = 0

    compare(c, original, expected)


@suite.case("multiple signs")
def test_multiple_signs(c):
    original = b"--123\x00"
    expected = 0

    compare(c, original, expected)


@suite.case("plus and minus signs")
def test_mixed_signs(c):
    original = b"+-123\x00"
    expected = 0

    compare(c, original, expected)


@suite.case("empty string")
def test_empty(c):
    original = b"\x00"
    expected = 0

    compare(c, original, expected)


@suite.case("only whitespace")
def test_only_whitespace(c):
    original = b"   \t\n\r\x00"
    expected = 0

    compare(c, original, expected)


@suite.case("only sign")
def test_only_sign(c):
    original = b"-\x00"
    expected = 0

    compare(c, original, expected)


@suite.case("number with leading zeros")
def test_large_leading_zeros(c):
    original = b"00000000000000000000042\x00"
    expected = 42

    compare(c, original, expected)


@suite.case("integer maximum")
def test_int_max(c):
    original = b"2147483647\x00"
    expected = 2147483647

    compare(c, original, expected)


@suite.case("integer minimum")
def test_int_min(c):
    original = b"-2147483648\x00"
    expected = -2147483648

    compare(c, original, expected)


@suite.case("number after whitespace")
def test_whitespace_number(c):
    original = b" \t\n\v\f\r-9876\x00"
    expected = -9876

    compare(c, original, expected)
