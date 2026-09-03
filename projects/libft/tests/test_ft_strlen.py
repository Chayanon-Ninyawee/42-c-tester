from framework import TestSuite

suite = TestSuite("ft_strlen")


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

    ft = c.ft_strlen(ft_buffer)
    libc = c.strlen(libc_buffer)

    libc.equals(
        expected,
        "Test with strlen() from libc",
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
    ).assert_now()


@suite.case("empty string has length 0")
def test_empty(c):
    original = b"\x00"
    expected = 0

    compare(c, original, expected)


@suite.case("'a' has length 1")
def test_single_character(c):
    original = b"a\x00"
    expected = 1

    compare(c, original, expected)


@suite.case("'hello' has length 5")
def test_basic(c):
    original = b"hello\x00"
    expected = 5

    compare(c, original, expected)


@suite.case("'Hello World' has length 11")
def test_spaces(c):
    original = b"Hello World\x00"
    expected = 11

    compare(c, original, expected)


@suite.case("string with spaces")
def test_multiple_spaces(c):
    original = b"hello  world\x00"
    expected = 12

    compare(c, original, expected)


@suite.case("digits are counted")
def test_digits(c):
    original = b"1234567890\x00"
    expected = 10

    compare(c, original, expected)


@suite.case("punctuation is counted")
def test_punctuation(c):
    original = b"!@#$%^&*()\x00"
    expected = 10

    compare(c, original, expected)


@suite.case("uppercase and lowercase are counted")
def test_mixed_case(c):
    original = b"AbCdEf\x00"
    expected = 6

    compare(c, original, expected)


@suite.case("newline is counted")
def test_newline(c):
    original = b"hello\nworld\x00"
    expected = 11

    compare(c, original, expected)


@suite.case("tab is counted")
def test_tab(c):
    original = b"hello\tworld\x00"
    expected = 11

    compare(c, original, expected)


@suite.case("long string")
def test_long_string(c):
    original = b"This is a reasonably long string for testing\x00"
    expected = 44

    compare(c, original, expected)
