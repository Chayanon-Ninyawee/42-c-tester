from framework import TestSuite

suite = TestSuite("ft_strlen")


@suite.case("empty string has length 0")
def test_empty(c):
    buffer = c.buffer(b"\x00", size=1, type="char")

    result = c.ft_strlen(buffer)

    result.equals(0)
    result.buffer_equals(buffer, b"\x00")
    result.assert_now()


@suite.case("'a' has length 1")
def test_single_character(c):
    buffer = c.buffer(b"a\x00", size=2, type="char")

    result = c.ft_strlen(buffer)

    result.equals(1)
    result.buffer_equals(buffer, b"a\x00")
    result.assert_now()


@suite.case("'hello' has length 5")
def test_basic(c):
    buffer = c.buffer(b"hello\x00", size=6, type="char")

    result = c.ft_strlen(buffer)

    result.equals(5)
    result.buffer_equals(buffer, b"hello\x00")
    result.assert_now()


@suite.case("'Hello World' has length 11")
def test_spaces(c):
    buffer = c.buffer(b"Hello World\x00", size=12, type="char")

    result = c.ft_strlen(buffer)

    result.equals(11)
    result.buffer_equals(buffer, b"Hello World\x00")
    result.assert_now()


@suite.case("string with spaces")
def test_multiple_spaces(c):
    buffer = c.buffer(b"hello  world\x00", size=13, type="char")

    result = c.ft_strlen(buffer)

    result.equals(12)
    result.buffer_equals(buffer, b"hello  world\x00")
    result.assert_now()


@suite.case("digits are counted")
def test_digits(c):
    buffer = c.buffer(b"1234567890\x00", size=11, type="char")

    result = c.ft_strlen(buffer)

    result.equals(10)
    result.buffer_equals(buffer, b"1234567890\x00")
    result.assert_now()


@suite.case("punctuation is counted")
def test_punctuation(c):
    buffer = c.buffer(b"!@#$%^&*()\x00", size=11, type="char")

    result = c.ft_strlen(buffer)

    result.equals(10)
    result.buffer_equals(buffer, b"!@#$%^&*()\x00")
    result.assert_now()


@suite.case("uppercase and lowercase are counted")
def test_mixed_case(c):
    buffer = c.buffer(b"AbCdEf\x00", size=7, type="char")

    result = c.ft_strlen(buffer)

    result.equals(6)
    result.buffer_equals(buffer, b"AbCdEf\x00")
    result.assert_now()


@suite.case("newline is counted")
def test_newline(c):
    buffer = c.buffer(b"hello\nworld\x00", size=12, type="char")

    result = c.ft_strlen(buffer)

    result.equals(11)
    result.buffer_equals(buffer, b"hello\nworld\x00")
    result.assert_now()


@suite.case("tab is counted")
def test_tab(c):
    buffer = c.buffer(b"hello\tworld\x00", size=12, type="char")

    result = c.ft_strlen(buffer)

    result.equals(11)
    result.buffer_equals(buffer, b"hello\tworld\x00")
    result.assert_now()


@suite.case("long string")
def test_long_string(c):
    buffer = c.buffer(
        b"This is a reasonably long string for testing\x00",
        size=45,
        type="char",
    )

    result = c.ft_strlen(buffer)

    result.equals(44)
    result.buffer_equals(
        buffer,
        b"This is a reasonably long string for testing\x00",
    )
    result.assert_now()
