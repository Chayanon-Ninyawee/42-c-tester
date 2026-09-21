from framework import TestSuite, c_bytes

suite = TestSuite("ft_strlcat")


def compare(c, dest_original, src_original, size, expected, return_expected):
    dest_c = c_bytes(dest_original)
    src_c = c_bytes(src_original)

    test = c.include("libft.h", "string.h").code(f"""
        unsigned char ft_dest[] = {{{dest_c}}};
        unsigned char ft_src[] = {{{src_c}}};

        unsigned char libc_dest[] = {{{dest_c}}};
        unsigned char libc_src[] = {{{src_c}}};

        size_t ft = ft_strlcat(
            (char *)ft_dest,
            (char *)ft_src,
            {size}
        );

        size_t libc = strlcat(
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
        str(return_expected),
        "Test ft_strlcat() returned value",
    )

    test.value("libc").equals(
        str(return_expected),
        "Reference returned value from strlcat() from libc",
    ).reference()

    test.buffer("ft_dest").equals(
        expected,
        "Test destination buffer",
    )

    test.buffer("libc_dest").equals(
        expected,
        "Test destination buffer from strlcat() from libc",
    ).reference()

    test.buffer("ft_src").equals(
        src_original,
        "Source buffer was modified",
    )

    test.buffer("libc_src").equals(
        src_original,
        "Source buffer was modified by strlcat() from libc",
    ).reference()

    test.malloc.count(
        0,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("empty destination")
def test_empty_dest(c):
    compare(
        c,
        b"\x00XXXXXXXXX",
        b"hello\x00",
        "10",
        b"hello\x00XXXX",
        5,
    )


@suite.case("empty source")
def test_empty_src(c):
    compare(
        c,
        b"hello\x00XXXX",
        b"\x00",
        "10",
        b"hello\x00XXXX",
        5,
    )


@suite.case("normal concatenation")
def test_normal_concat(c):
    compare(
        c,
        b"hello\x00XXXXXXXXX",
        b" world\x00",
        "15",
        b"hello world\x00XXX",
        11,
    )


@suite.case("fits exactly")
def test_fits_exactly(c):
    compare(
        c,
        b"hello\x00XXXX",
        b"!!\x00",
        "8",
        b"hello!!\x00XX",
        7,
    )


@suite.case("truncated")
def test_truncated(c):
    compare(
        c,
        b"hello\x00XXXX",
        b" world!\x00",
        "10",
        b"hello wor\x00",
        12,
    )


@suite.case("size zero")
def test_size_zero(c):
    compare(
        c,
        b"hello\x00XXXX",
        b" world\x00",
        "0",
        b"hello\x00XXXX",
        6,
    )


@suite.case("size smaller than destination")
def test_size_smaller_than_dest(c):
    compare(
        c,
        b"hello\x00XXXX",
        b" world\x00",
        "3",
        b"hello\x00XXXX",
        9,
    )


@suite.case("one byte buffer")
def test_one_byte_buffer(c):
    compare(
        c,
        b"\x00XXXXXXXXX",
        b"hello\x00",
        "1",
        b"\x00XXXXXXXXX",
        5,
    )


@suite.case("binary data")
def test_binary(c):
    compare(
        c,
        b"abc\x00XXXXXX",
        b"\x01\x02\x03\x00",
        "10",
        b"abc\x01\x02\x03\x00XXX",
        6,
    )
