from framework import TestSuite, c_bytes

suite = TestSuite("ft_memcpy")


def compare(c, dest_original, src_original, expected, count):
    dest_c = c_bytes(dest_original)
    src_c = c_bytes(src_original)

    test = c.include("libft.h", "string.h").code(f"""
        unsigned char ft_dest[] = {{{dest_c}}};
        unsigned char ft_src[] = {{{src_c}}};

        unsigned char libc_dest[] = {{{dest_c}}};
        unsigned char libc_src[] = {{{src_c}}};

        void *ft_result = ft_memcpy(
            ft_dest,
            ft_src,
            {count}
        );

        void *libc_result = memcpy(
            libc_dest,
            libc_src,
            {count}
        );

        int ft_pointer_ok = (ft_result == ft_dest);
        int libc_pointer_ok = (libc_result == libc_dest);

        TEST_VALUE("ft_pointer", "%d", ft_pointer_ok);
        TEST_VALUE("libc_pointer", "%d", libc_pointer_ok);

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

    test.value("ft_pointer").equals(
        "1",
        "Test returned pointer",
    )

    test.value("libc_pointer").equals(
        "1",
        "Test returned pointer from memcpy() from libc",
    ).reference()

    test.buffer("ft_dest").equals(
        expected,
        "Test destination buffer",
    )

    test.buffer("libc_dest").equals(
        expected,
        "Test destination buffer from memcpy() from libc",
    ).reference()

    test.buffer("ft_src").equals(
        src_original,
        "Test that source buffer was modified",
    )

    test.buffer("libc_src").equals(
        src_original,
        "Test that source buffer was modified by memcpy() from libc",
    ).reference()

    test.malloc.count(
        0,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("copies entire buffer")
def test_all_bytes(c):
    compare(
        c,
        b"XXXXXXXXXX",
        b"hello12345",
        b"hello12345",
        "10",
    )


@suite.case("copies first 5 bytes")
def test_partial(c):
    compare(
        c,
        b"XXXXXXXXXX",
        b"hello12345",
        b"helloXXXXX",
        "5",
    )


@suite.case("copies one byte")
def test_one_byte(c):
    compare(
        c,
        b"XXXXXXXXXX",
        b"hello12345",
        b"hXXXXXXXXX",
        "1",
    )


@suite.case("zero bytes does nothing")
def test_zero(c):
    compare(
        c,
        b"XXXXXXXXXX",
        b"hello12345",
        b"XXXXXXXXXX",
        "0",
    )


@suite.case("works with binary data")
def test_binary(c):
    compare(
        c,
        b"\x00\x00\x00\x00\x00",
        b"\xff\x01\x80\x00\x7f",
        b"\xff\x01\x80\x00\x7f",
        "5",
    )


@suite.case("preserves bytes after n")
def test_boundary(c):
    compare(
        c,
        b"0123456789",
        b"abcdefghij",
        b"abcd456789",
        "4",
    )


@suite.case("copies between independent buffers")
def test_different_buffers(c):
    compare(
        c,
        b"abcdefghij",
        b"1234567890",
        b"1234567hij",
        "7",
    )
