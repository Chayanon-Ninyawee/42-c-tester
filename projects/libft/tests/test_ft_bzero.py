from framework import TestSuite

suite = TestSuite("ft_bzero")


def compare(c, original, expected, count):
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

    ft = c.ft_bzero(
        ft_buffer,
        count,
    )

    libc = c.bzero(
        libc_buffer,
        count,
    )

    ft.buffer_equals(
        ft_buffer,
        expected,
        "Test buffer contents",
    )
    ft.assert_now()

    libc.buffer_equals(
        libc_buffer,
        expected,
        "Test buffer contents from memset() from libc",
    )
    libc.assert_now()


@suite.case("zeros entire buffer")
def test_all_bytes(c):
    original = b"hello"
    expected = b"\x00\x00\x00\x00\x00"

    compare(c, original, expected, "5")


@suite.case("zeros first 3 bytes")
def test_partial(c):
    original = b"hello"
    expected = b"\x00\x00\x00lo"

    compare(c, original, expected, "3")


@suite.case("zeros first byte")
def test_one_byte(c):
    original = b"hello"
    expected = b"\x00ello"

    compare(c, original, expected, "1")


@suite.case("zero bytes does nothing")
def test_zero(c):
    original = b"hello"
    expected = b"hello"

    compare(c, original, expected, "0")


@suite.case("works with binary data")
def test_binary(c):
    original = b"\xff\x01\x00\x80\x7f"
    expected = b"\x00\x00\x00\x80\x7f"

    compare(c, original, expected, "3")


@suite.case("preserves bytes after n")
def test_boundary(c):
    original = b"abcdefghij"
    expected = b"\x00\x00\x00\x00efghij"

    compare(c, original, expected, "4")
