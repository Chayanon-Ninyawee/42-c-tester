from framework import TestSuite

suite = TestSuite("ft_memmove")


@suite.case("copies entire buffer")
def test_all_bytes(c):
    dest = c.buffer(
        b"XXXXXXXXXX",
        size=10,
        name="dest",
    )
    src = c.buffer(
        b"hello12345",
        size=10,
        name="src",
    )

    result = c.ft_memmove(
        dest,
        src,
        "10",
    )

    result.returned_pointer_is(dest)
    result.buffer_equals(dest, b"hello12345")
    result.buffer_equals(src, b"hello12345")
    result.assert_now()


@suite.case("copies first 5 bytes")
def test_partial(c):
    dest = c.buffer(
        b"XXXXXXXXXX",
        size=10,
        name="dest",
    )
    src = c.buffer(
        b"hello12345",
        size=10,
        name="src",
    )

    result = c.ft_memmove(
        dest,
        src,
        "5",
    )

    result.returned_pointer_is(dest)
    result.buffer_equals(dest, b"helloXXXXX")
    result.buffer_equals(src, b"hello12345")
    result.assert_now()


@suite.case("copies one byte")
def test_one_byte(c):
    dest = c.buffer(
        b"XXXXXXXXXX",
        size=10,
        name="dest",
    )
    src = c.buffer(
        b"hello12345",
        size=10,
        name="src",
    )

    result = c.ft_memmove(
        dest,
        src,
        "1",
    )

    result.returned_pointer_is(dest)
    result.buffer_equals(dest, b"hXXXXXXXXX")
    result.buffer_equals(src, b"hello12345")
    result.assert_now()


@suite.case("zero bytes does nothing")
def test_zero(c):
    dest = c.buffer(
        b"XXXXXXXXXX",
        size=10,
        name="dest",
    )
    src = c.buffer(
        b"hello12345",
        size=10,
        name="src",
    )

    result = c.ft_memmove(
        dest,
        src,
        "0",
    )

    result.returned_pointer_is(dest)
    result.buffer_equals(dest, b"XXXXXXXXXX")
    result.buffer_equals(src, b"hello12345")
    result.assert_now()


@suite.case("works with binary data")
def test_binary(c):
    dest = c.buffer(
        b"\x00\x00\x00\x00\x00",
        size=5,
        name="dest",
    )
    src = c.buffer(
        b"\xff\x01\x80\x00\x7f",
        size=5,
        name="src",
    )

    result = c.ft_memmove(
        dest,
        src,
        "5",
    )

    result.returned_pointer_is(dest)
    result.buffer_equals(dest, b"\xff\x01\x80\x00\x7f")
    result.buffer_equals(src, b"\xff\x01\x80\x00\x7f")
    result.assert_now()


@suite.case("preserves bytes after n")
def test_boundary(c):
    dest = c.buffer(
        b"0123456789",
        size=10,
        name="dest",
    )
    src = c.buffer(
        b"abcdefghij",
        size=10,
        name="src",
    )

    result = c.ft_memmove(
        dest,
        src,
        "4",
    )

    result.returned_pointer_is(dest)
    result.buffer_equals(dest, b"abcd456789")
    result.buffer_equals(src, b"abcdefghij")
    result.assert_now()


@suite.case("copies between independent buffers")
def test_different_buffers(c):
    dest = c.buffer(
        b"abcdefghij",
        size=10,
        name="dest",
    )
    src = c.buffer(
        b"1234567890",
        size=10,
        name="src",
    )

    result = c.ft_memmove(
        dest,
        src,
        "7",
    )

    result.returned_pointer_is(dest)
    result.buffer_equals(dest, b"1234567hij")
    result.buffer_equals(src, b"1234567890")
    result.assert_now()


@suite.case("handles overlapping buffers forward")
def test_overlap_forward(c):
    buffer = c.buffer(
        b"123456789\x00",
        size=10,
        type="char",
        name="buffer",
    )

    result = c.ft_memmove(
        buffer.offset(2),
        buffer,
        "7",
    )

    result.returned_pointer_is(buffer.offset(2))
    result.buffer_equals(
        buffer,
        b"121234567\x00",
    )
    result.assert_now()


@suite.case("handles overlapping buffers backward")
def test_overlap_backward(c):
    buffer = c.buffer(
        b"123456789\x00",
        size=10,
        type="char",
        name="buffer",
    )

    result = c.ft_memmove(
        buffer,
        buffer.offset(2),
        "7",
    )

    result.returned_pointer_is(buffer)
    result.buffer_equals(
        buffer,
        b"345678989\x00",
    )
    result.assert_now()
