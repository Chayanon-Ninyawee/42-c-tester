from framework import TestSuite

suite = TestSuite("ft_memset")


@suite.case("sets all bytes")
def test_all_bytes(c):
    buffer = c.buffer(
        b"hello",
        size=5,
    )

    result = c.ft_memset(
        buffer,
        "'X'",
        "5",
    )

    result.returned_pointer_is(buffer)
    result.buffer_equals(buffer, b"XXXXX")
    result.assert_now()


@suite.case("sets first 3 bytes")
def test_partial(c):
    buffer = c.buffer(
        b"hello",
        size=5,
    )

    result = c.ft_memset(
        buffer,
        "'X'",
        "3",
    )

    result.returned_pointer_is(buffer)
    result.buffer_equals(buffer, b"XXXlo")
    result.assert_now()


@suite.case("sets first byte")
def test_one_byte(c):
    buffer = c.buffer(
        b"hello",
        size=5,
    )

    result = c.ft_memset(
        buffer,
        "'X'",
        "1",
    )

    result.returned_pointer_is(buffer)
    result.buffer_equals(buffer, b"Xello")
    result.assert_now()


@suite.case("zero bytes does nothing")
def test_zero(c):
    buffer = c.buffer(
        b"hello",
        size=5,
    )

    result = c.ft_memset(
        buffer,
        "'X'",
        "0",
    )

    result.returned_pointer_is(buffer)
    result.buffer_equals(buffer, b"hello")
    result.assert_now()


@suite.case("can set zero bytes")
def test_zero_value(c):
    buffer = c.buffer(
        b"hello",
        size=5,
    )

    result = c.ft_memset(
        buffer,
        "0",
        "5",
    )

    result.returned_pointer_is(buffer)
    result.buffer_equals(buffer, b"\x00\x00\x00\x00\x00")
    result.assert_now()


@suite.case("works with binary data")
def test_binary(c):
    buffer = c.buffer(
        b"\x00\x01\x02\x03\x04",
        size=5,
    )

    result = c.ft_memset(
        buffer,
        "255",
        "3",
    )

    result.returned_pointer_is(buffer)
    result.buffer_equals(buffer, b"\xff\xff\xff\x03\x04")
    result.assert_now()


@suite.case("preserves bytes after n")
def test_boundary(c):
    buffer = c.buffer(
        b"abcdefghij",
        size=10,
    )

    result = c.ft_memset(
        buffer,
        "'Z'",
        "4",
    )

    result.returned_pointer_is(buffer)
    result.buffer_equals(buffer, b"ZZZZefghij")
    result.assert_now()
