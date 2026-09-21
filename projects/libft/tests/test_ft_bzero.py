from framework import TestSuite, c_bytes

suite = TestSuite("ft_bzero")


def compare(c, original, expected, count):
    original_c = c_bytes(original)

    test = c.include("libft.h", "string.h").code(f"""
        unsigned char ft_buffer[] = {{{original_c}}};
        unsigned char libc_buffer[] = {{{original_c}}};

        ft_bzero(ft_buffer, {count});
        bzero(libc_buffer, {count});

        TEST_BUFFER(
            "ft_buffer",
            ft_buffer,
            sizeof(ft_buffer)
        );

        TEST_BUFFER(
            "libc_buffer",
            libc_buffer,
            sizeof(libc_buffer)
        );

        return 0;
    """)

    test.buffer("ft_buffer").equals(
        expected,
        "Test buffer contents",
    )

    test.buffer("libc_buffer").equals(
        expected,
        "Test buffer contents from bzero() from libc",
    ).reference()

    test.malloc.count(
        0,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("zeros entire buffer")
def test_all_bytes(c):
    compare(c, b"hello", b"\x00\x00\x00\x00\x00", "5")


@suite.case("zeros first 3 bytes")
def test_partial(c):
    compare(c, b"hello", b"\x00\x00\x00lo", "3")


@suite.case("zeros first byte")
def test_one_byte(c):
    compare(c, b"hello", b"\x00ello", "1")


@suite.case("zero bytes does nothing")
def test_zero(c):
    compare(c, b"hello", b"hello", "0")


@suite.case("works with binary data")
def test_binary(c):
    compare(
        c,
        b"\xff\x01\x00\x80\x7f",
        b"\x00\x00\x00\x80\x7f",
        "3",
    )


@suite.case("preserves bytes after n")
def test_boundary(c):
    compare(
        c,
        b"abcdefghij",
        b"\x00\x00\x00\x00efghij",
        "4",
    )
