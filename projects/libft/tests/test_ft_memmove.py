from framework import TestSuite

suite = TestSuite("ft_memmove")


def compare(c, dest_original, src_original, expected, count):
    ft_dest = c.buffer(
        dest_original,
        size=len(dest_original),
        name="ft_dest",
    )
    ft_src = c.buffer(
        src_original,
        size=len(src_original),
        name="ft_src",
    )

    libc_dest = c.buffer(
        dest_original,
        size=len(dest_original),
        name="libc_dest",
    )
    libc_src = c.buffer(
        src_original,
        size=len(src_original),
        name="libc_src",
    )

    ft = c.ft_memmove(
        ft_dest,
        ft_src,
        count,
    )

    libc = c.memmove(
        libc_dest,
        libc_src,
        count,
    )

    libc.returned_pointer_is(
        libc_dest,
        "Test returned pointer from memmove() from libc",
    )
    libc.buffer_equals(
        libc_dest,
        expected,
        "Test destination buffer from memmove() from libc",
    )
    libc.buffer_equals(
        libc_src,
        src_original,
        "Test that source buffer was not modified by memmove() from libc",
    ).assert_reference()

    ft.returned_pointer_is(
        ft_dest,
        "Test returned pointer",
    )
    ft.buffer_equals(
        ft_dest,
        expected,
        "Test destination buffer",
    )
    ft.buffer_equals(
        ft_src,
        src_original,
        "Test that source buffer was not modified",
    )
    ft.malloc_count_equals(
        0,
        "Test malloc count",
    ).assert_now()


@suite.case("copies entire buffer")
def test_all_bytes(c):
    dest_original = b"XXXXXXXXXX"
    src_original = b"hello12345"
    expected = b"hello12345"

    compare(c, dest_original, src_original, expected, "10")


@suite.case("copies first 5 bytes")
def test_partial(c):
    dest_original = b"XXXXXXXXXX"
    src_original = b"hello12345"
    expected = b"helloXXXXX"

    compare(c, dest_original, src_original, expected, "5")


@suite.case("copies one byte")
def test_one_byte(c):
    dest_original = b"XXXXXXXXXX"
    src_original = b"hello12345"
    expected = b"hXXXXXXXXX"

    compare(c, dest_original, src_original, expected, "1")


@suite.case("zero bytes does nothing")
def test_zero(c):
    dest_original = b"XXXXXXXXXX"
    src_original = b"hello12345"
    expected = b"XXXXXXXXXX"

    compare(c, dest_original, src_original, expected, "0")


@suite.case("works with binary data")
def test_binary(c):
    dest_original = b"\x00\x00\x00\x00\x00"
    src_original = b"\xff\x01\x80\x00\x7f"
    expected = b"\xff\x01\x80\x00\x7f"

    compare(c, dest_original, src_original, expected, "5")


@suite.case("preserves bytes after n")
def test_boundary(c):
    dest_original = b"0123456789"
    src_original = b"abcdefghij"
    expected = b"abcd456789"

    compare(c, dest_original, src_original, expected, "4")


@suite.case("copies between independent buffers")
def test_different_buffers(c):
    dest_original = b"abcdefghij"
    src_original = b"1234567890"
    expected = b"1234567hij"

    compare(c, dest_original, src_original, expected, "7")


@suite.case("handles overlapping buffers forward")
def test_overlap_forward(c):
    original = b"123456789\x00"
    expected = b"121234567\x00"

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

    ft = c.ft_memmove(
        ft_buffer.offset(2),
        ft_buffer,
        "7",
    )

    libc = c.memmove(
        libc_buffer.offset(2),
        libc_buffer,
        "7",
    )

    libc.returned_pointer_is(
        libc_buffer.offset(2),
        "Test returned pointer from memmove() from libc",
    )
    libc.buffer_equals(
        libc_buffer,
        expected,
        "Test buffer contents from memmove() from libc",
    ).assert_reference()

    ft.returned_pointer_is(
        ft_buffer.offset(2),
        "Test returned pointer",
    )
    ft.buffer_equals(
        ft_buffer,
        expected,
        "Test buffer contents",
    ).assert_now()


@suite.case("handles overlapping buffers backward")
def test_overlap_backward(c):
    original = b"123456789\x00"
    expected = b"345678989\x00"

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

    ft = c.ft_memmove(
        ft_buffer,
        ft_buffer.offset(2),
        "7",
    )

    libc = c.memmove(
        libc_buffer,
        libc_buffer.offset(2),
        "7",
    )

    libc.returned_pointer_is(
        libc_buffer,
        "Test returned pointer from memmove() from libc",
    )
    libc.buffer_equals(
        libc_buffer,
        expected,
        "Test buffer contents from memmove() from libc",
    ).assert_reference()

    ft.returned_pointer_is(
        ft_buffer,
        "Test returned pointer",
    )
    ft.buffer_equals(
        ft_buffer,
        expected,
        "Test buffer contents",
    ).assert_now()


@suite.case("handles large overlapping buffers forward")
def test_large_overlap_forward(c):
    pattern = (
        b"0123456789"
        b"abcdefghij"
        b"KLMNOPQRST"
        b"uvwxyzABCD"
        b"EFGHIJKLMN"
        b"OPQRSTUVWX"
        b"YZ01234567"
        b"89!@#$%^&*"
        b"()_+-=[]{}"
        b"<>?/.,:;"
    )

    # the pattern size is 98
    original = pattern * 20
    offset = 200
    count = 1600

    expected = original[:offset] + original[:count] + original[offset + count :]

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

    ft = c.ft_memmove(
        ft_buffer.offset(offset),
        ft_buffer,
        str(count),
    )

    libc = c.memmove(
        libc_buffer.offset(offset),
        libc_buffer,
        str(count),
    )

    libc.returned_pointer_is(
        libc_buffer.offset(offset),
        "Test returned pointer from memmove() from libc",
    )
    libc.buffer_equals(
        libc_buffer,
        expected,
        "Test buffer contents from memmove() from libc",
    ).assert_reference()

    ft.returned_pointer_is(
        ft_buffer.offset(offset),
        "Test returned pointer",
    )
    ft.buffer_equals(
        ft_buffer,
        expected,
        "Test buffer contents",
    ).assert_now()


@suite.case("handles large overlapping buffers backward")
def test_large_overlap_backward(c):
    pattern = (
        b"0123456789"
        b"abcdefghij"
        b"KLMNOPQRST"
        b"uvwxyzABCD"
        b"EFGHIJKLMN"
        b"OPQRSTUVWX"
        b"YZ01234567"
        b"89!@#$%^&*"
        b"()_+-=[]{}"
        b"<>?/.,:;"
    )

    # the pattern size is 98
    original = pattern * 20
    offset = 200
    count = 1600

    expected = original[offset : offset + count] + original[count:]

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

    ft = c.ft_memmove(
        ft_buffer,
        ft_buffer.offset(offset),
        str(count),
    )

    libc = c.memmove(
        libc_buffer,
        libc_buffer.offset(offset),
        str(count),
    )

    libc.returned_pointer_is(
        libc_buffer,
        "Test returned pointer from memmove() from libc",
    )
    libc.buffer_equals(
        libc_buffer,
        expected,
        "Test buffer contents from memmove() from libc",
    ).assert_reference()

    ft.returned_pointer_is(
        ft_buffer,
        "Test returned pointer",
    )
    ft.buffer_equals(
        ft_buffer,
        expected,
        "Test buffer contents",
    ).assert_now()
