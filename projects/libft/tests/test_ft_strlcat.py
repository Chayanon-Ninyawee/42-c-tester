from framework import TestSuite

suite = TestSuite("ft_strlcat")


def compare(c, dest_original, src_original, size, expected, return_expected):
    ft_dest = c.buffer(
        dest_original,
        size=len(dest_original),
        type="char",
        name="ft_dest",
    )
    ft_src = c.buffer(
        src_original,
        size=len(src_original),
        type="char",
        name="ft_src",
    )

    libc_dest = c.buffer(
        dest_original,
        size=len(dest_original),
        type="char",
        name="libc_dest",
    )
    libc_src = c.buffer(
        src_original,
        size=len(src_original),
        type="char",
        name="libc_src",
    )

    ft = c.ft_strlcat(
        ft_dest,
        ft_src,
        size,
    )

    libc = c.strlcat(
        libc_dest,
        libc_src,
        size,
    )

    libc.equals(
        return_expected,
        "Test with return value from strlcat() from libc",
    )
    libc.buffer_equals(
        libc_dest,
        expected,
        "Test destination buffer from strlcat() from libc",
    )
    libc.buffer_equals(
        libc_src,
        src_original,
        "Test that source buffer was not modified by strlcat() from libc",
    ).assert_reference()

    ft.equals(
        return_expected,
        "Test with return value",
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
    ).assert_now()


@suite.case("empty destination")
def test_empty_dest(c):
    dest_original = b"\x00XXXXXXXXX"
    src_original = b"hello\x00"
    size = "10"
    expected = b"hello\x00XXXX"
    return_expected = 5

    compare(
        c,
        dest_original,
        src_original,
        size,
        expected,
        return_expected,
    )


@suite.case("empty source")
def test_empty_src(c):
    dest_original = b"hello\x00XXXX"
    src_original = b"\x00"
    size = "10"
    expected = b"hello\x00XXXX"
    return_expected = 5

    compare(
        c,
        dest_original,
        src_original,
        size,
        expected,
        return_expected,
    )


@suite.case("normal concatenation")
def test_normal_concat(c):
    dest_original = b"hello\x00XXXXXXXXX"
    src_original = b" world\x00"
    size = "15"
    expected = b"hello world\x00XXX"
    return_expected = 11

    compare(
        c,
        dest_original,
        src_original,
        size,
        expected,
        return_expected,
    )


@suite.case("fits exactly")
def test_fits_exactly(c):
    dest_original = b"hello\x00XXXX"
    src_original = b"!!\x00"
    size = "8"
    expected = b"hello!!\x00XX"
    return_expected = 7

    compare(
        c,
        dest_original,
        src_original,
        size,
        expected,
        return_expected,
    )


@suite.case("truncated")
def test_truncated(c):
    dest_original = b"hello\x00XXXX"
    src_original = b" world!\x00"
    size = "10"
    expected = b"hello wor\x00"
    return_expected = 12

    compare(
        c,
        dest_original,
        src_original,
        size,
        expected,
        return_expected,
    )


@suite.case("size zero")
def test_size_zero(c):
    dest_original = b"hello\x00XXXX"
    src_original = b" world\x00"
    size = "0"
    expected = b"hello\x00XXXX"
    return_expected = 6

    compare(
        c,
        dest_original,
        src_original,
        size,
        expected,
        return_expected,
    )


@suite.case("size smaller than destination")
def test_size_smaller_than_dest(c):
    dest_original = b"hello\x00XXXX"
    src_original = b" world\x00"
    size = "3"
    expected = b"hello\x00XXXX"
    return_expected = 9

    compare(
        c,
        dest_original,
        src_original,
        size,
        expected,
        return_expected,
    )


@suite.case("one byte buffer")
def test_one_byte_buffer(c):
    dest_original = b"\x00XXXXXXXXX"
    src_original = b"hello\x00"
    size = "1"
    expected = b"\x00XXXXXXXXX"
    return_expected = 5

    compare(
        c,
        dest_original,
        src_original,
        size,
        expected,
        return_expected,
    )


@suite.case("binary data")
def test_binary(c):
    dest_original = b"abc\x00XXXXXX"
    src_original = b"\x01\x02\x03\x00"
    size = "10"
    expected = b"abc\x01\x02\x03\x00XXX"
    return_expected = 6

    compare(
        c,
        dest_original,
        src_original,
        size,
        expected,
        return_expected,
    )
