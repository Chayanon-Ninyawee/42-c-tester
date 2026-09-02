from framework import TestSuite

suite = TestSuite("ft_bzero")


@suite.case("zeros entire buffer")
def test_all_bytes(c):
    buffer = c.buffer(
        b"hello",
        size=5,
    )

    result = c.ft_bzero(
        buffer,
        "5",
    )

    result.buffer_equals(buffer, b"\x00\x00\x00\x00\x00")
    result.assert_now()


@suite.case("zeros first 3 bytes")
def test_partial(c):
    buffer = c.buffer(
        b"hello",
        size=5,
    )

    result = c.ft_bzero(
        buffer,
        "3",
    )

    result.buffer_equals(buffer, b"\x00\x00\x00lo")
    result.assert_now()


@suite.case("zeros first byte")
def test_one_byte(c):
    buffer = c.buffer(
        b"hello",
        size=5,
    )

    result = c.ft_bzero(
        buffer,
        "1",
    )

    result.buffer_equals(buffer, b"\x00ello")
    result.assert_now()


@suite.case("zero bytes does nothing")
def test_zero(c):
    buffer = c.buffer(
        b"hello",
        size=5,
    )

    result = c.ft_bzero(
        buffer,
        "0",
    )

    result.buffer_equals(buffer, b"hello")
    result.assert_now()


@suite.case("works with binary data")
def test_binary(c):
    buffer = c.buffer(
        b"\xff\x01\x00\x80\x7f",
        size=5,
    )

    result = c.ft_bzero(
        buffer,
        "3",
    )

    result.buffer_equals(buffer, b"\x00\x00\x00\x80\x7f")
    result.assert_now()


@suite.case("preserves bytes after n")
def test_boundary(c):
    buffer = c.buffer(
        b"abcdefghij",
        size=10,
    )

    result = c.ft_bzero(
        buffer,
        "4",
    )

    result.buffer_equals(buffer, b"\x00\x00\x00\x00efghij")
    result.assert_now()
