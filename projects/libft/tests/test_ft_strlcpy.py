from framework import TestSuite, c_bytes

suite = TestSuite("ft_strlcpy")


def compare(c, dest_original, src_original, expected, expected_return, size):
    dest_c = c_bytes(dest_original)
    src_c = c_bytes(src_original)

    test = c.include("libft.h", "string.h").code(f"""
        unsigned char ft_dest[] = {{{dest_c}}};
        unsigned char ft_src[] = {{{src_c}}};

        unsigned char libc_dest[] = {{{dest_c}}};
        unsigned char libc_src[] = {{{src_c}}};

        size_t ft = ft_strlcpy(
            (char *)ft_dest,
            (char *)ft_src,
            {size}
        );

        size_t libc = strlcpy(
            (char *)libc_dest,
            (char *)libc_src,
            {size}
        );

        TEST_VALUE("ft", "%zu", ft);
        TEST_VALUE("libc", "%zu", libc);

        TEST_BUFFER(
            "ft_dest",
            ft_dest,
            sizeof(ft_dest)
        );

        TEST_BUFFER(
            "ft_src",
            ft_src,
            sizeof(ft_src)
        );

        TEST_BUFFER(
            "libc_dest",
            libc_dest,
            sizeof(libc_dest)
        );

        TEST_BUFFER(
            "libc_src",
            libc_src,
            sizeof(libc_src)
        );

        return 0;
    """)

    test.value("ft").equals(
        str(expected_return),
        "Test ft_strlcpy() returned value",
    )

    test.value("libc").equals(
        str(expected_return),
        "Reference returned value from strlcpy() from libc",
    ).reference()

    test.buffer("ft_dest").equals(
        expected,
        "Test destination buffer",
    )

    test.buffer("libc_dest").equals(
        expected,
        "Test destination buffer from strlcpy() from libc",
    ).reference()

    test.buffer("ft_src").equals(
        src_original,
        "Source buffer was modified",
    )

    test.buffer("libc_src").equals(
        src_original,
        "Source buffer was modified by strlcpy() from libc",
    ).reference()

    test.malloc.count(
        0,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("copies entire string")
def test_all_bytes(c):
    compare(
        c,
        b"XXXXXXXXXX",
        b"hello\x00",
        b"hello\x00XXXX",
        5,
        "10",
    )


@suite.case("copies string with exact size")
def test_exact_size(c):
    compare(
        c,
        b"XXXXXXXXXX",
        b"hello\x00",
        b"hello\x00XXXX",
        5,
        "6",
    )


@suite.case("truncates string")
def test_truncate(c):
    compare(
        c,
        b"XXXXXXXXXX",
        b"hello world\x00",
        b"hello wor\x00",
        11,
        "10",
    )


@suite.case("size zero does nothing")
def test_zero(c):
    compare(
        c,
        b"XXXXXXXXXX",
        b"hello\x00",
        b"XXXXXXXXXX",
        5,
        "0",
    )


@suite.case("size one writes only null terminator")
def test_one(c):
    compare(
        c,
        b"XXXXXXXXXX",
        b"hello\x00",
        b"\x00XXXXXXXXX",
        5,
        "1",
    )


@suite.case("source is longer than destination")
def test_source_longer(c):
    compare(
        c,
        b"XXXXXXXXXX",
        b"abcdefghijklmnop\x00",
        b"abcdefghi\x00",
        16,
        "10",
    )


@suite.case("source is shorter than destination")
def test_source_shorter(c):
    compare(
        c,
        b"XXXXXXXXXX",
        b"abc\x00",
        b"abc\x00XXXXXX",
        3,
        "10",
    )


@suite.case("empty source")
def test_empty(c):
    compare(
        c,
        b"XXXXXXXXXX",
        b"\x00",
        b"\x00XXXXXXXXX",
        0,
        "10",
    )


@suite.case("works with binary data")
def test_binary(c):
    compare(
        c,
        b"XXXXXXXXXX",
        b"\x01\x02\x03\x00",
        b"\x01\x02\x03\x00XXXXXX",
        3,
        "10",
    )
