from framework import TestSuite

suite = TestSuite("ft_strlcpy")


def compare(c, dest_original, src_original, expected, expected_return, size):
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

    ft = c.ft_strlcpy(
        ft_dest,
        ft_src,
        size,
    )

    libc = c.strlcpy(
        libc_dest,
        libc_src,
        size,
    )

    libc.equals(
        expected_return,
        "Test with strlcpy() from libc",
    )
    libc.buffer_equals(
        libc_dest,
        expected,
        "Test destination buffer from strlcpy() from libc",
    )
    libc.buffer_equals(
        libc_src,
        src_original,
        "Test that source buffer was not modified by strlcpy() from libc",
    ).assert_reference()

    ft.equals(
        expected_return,
        "Test with value",
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


@suite.case("copies entire string")
def test_all_bytes(c):
    dest_original = b"XXXXXXXXXX"
    src_original = b"hello\x00"
    expected = b"hello\x00XXXX"

    compare(c, dest_original, src_original, expected, 5, "10")


@suite.case("copies string with exact size")
def test_exact_size(c):
    dest_original = b"XXXXXXXXXX"
    src_original = b"hello\x00"
    expected = b"hello\x00XXXX"

    compare(c, dest_original, src_original, expected, 5, "6")


@suite.case("truncates string")
def test_truncate(c):
    dest_original = b"XXXXXXXXXX"
    src_original = b"hello world\x00"
    expected = b"hello wor\x00"

    compare(c, dest_original, src_original, expected, 11, "10")


@suite.case("size zero does nothing")
def test_zero(c):
    dest_original = b"XXXXXXXXXX"
    src_original = b"hello\x00"
    expected = b"XXXXXXXXXX"

    compare(c, dest_original, src_original, expected, 5, "0")


@suite.case("size one writes only null terminator")
def test_one(c):
    dest_original = b"XXXXXXXXXX"
    src_original = b"hello\x00"
    expected = b"\x00XXXXXXXXX"

    compare(c, dest_original, src_original, expected, 5, "1")


@suite.case("source is longer than destination")
def test_source_longer(c):
    dest_original = b"XXXXXXXXXX"
    src_original = b"abcdefghijklmnop\x00"
    expected = b"abcdefghi\x00"

    compare(c, dest_original, src_original, expected, 16, "10")


@suite.case("source is shorter than destination")
def test_source_shorter(c):
    dest_original = b"XXXXXXXXXX"
    src_original = b"abc\x00"
    expected = b"abc\x00XXXXXX"

    compare(c, dest_original, src_original, expected, 3, "10")


@suite.case("empty source")
def test_empty(c):
    dest_original = b"XXXXXXXXXX"
    src_original = b"\x00"
    expected = b"\x00XXXXXXXXX"

    compare(c, dest_original, src_original, expected, 0, "10")


@suite.case("works with binary data")
def test_binary(c):
    dest_original = b"XXXXXXXXXX"
    src_original = b"\x01\x02\x03\x00"
    expected = b"\x01\x02\x03\x00XXXXXX"

    compare(c, dest_original, src_original, expected, 3, "10")
