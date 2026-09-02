from framework import TestSuite

suite = TestSuite("ft_memset")


def compare(c, original, expected, value, count):
    ft_buffer = c.buffer(
        original,
        size=len(original),
        name="ft",
    )

    libc_buffer = c.buffer(
        original,
        size=len(original),
        name="libc",
    )

    ft = c.ft_memset(
        ft_buffer,
        value,
        count,
    )

    libc = c.memset(
        libc_buffer,
        value,
        count,
    )

    ft.returned_pointer_is(
        ft_buffer,
        "Test returned pointer",
    )

    ft.buffer_equals(
        ft_buffer,
        expected,
        "Test buffer contents",
    )

    ft.assert_now()

    libc.returned_pointer_is(
        libc_buffer,
        "Test returned pointer from memset() from libc",
    )

    libc.buffer_equals(
        libc_buffer,
        expected,
        "Test buffer contents from memset() from libc",
    )

    libc.assert_now()


@suite.case("sets all bytes")
def test_all_bytes(c):
    original = b"hello"
    expected = b"XXXXX"

    compare(c, original, expected, "'X'", "5")


@suite.case("sets first 3 bytes")
def test_partial(c):
    original = b"hello"
    expected = b"XXXlo"

    compare(c, original, expected, "'X'", "3")


@suite.case("sets first byte")
def test_one_byte(c):
    original = b"hello"
    expected = b"Xello"

    compare(c, original, expected, "'X'", "1")


@suite.case("zero bytes does nothing")
def test_zero(c):
    original = b"hello"
    expected = b"hello"

    compare(c, original, expected, "'X'", "0")


@suite.case("can set zero bytes")
def test_zero_value(c):
    original = b"hello"
    expected = b"\x00\x00\x00\x00\x00"

    compare(c, original, expected, "0", "5")


@suite.case("works with binary data")
def test_binary(c):
    original = b"\x00\x01\x02\x03\x04"
    expected = b"\xff\xff\xff\x03\x04"

    compare(c, original, expected, "255", "3")


@suite.case("preserves bytes after n")
def test_boundary(c):
    original = b"abcdefghij"
    expected = b"ZZZZefghij"

    compare(c, original, expected, "'Z'", "4")
