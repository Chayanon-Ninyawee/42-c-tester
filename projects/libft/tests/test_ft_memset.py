from framework import TestSuite, c_bytes

suite = TestSuite("ft_memset")


def compare(c, original, expected, value, count):
    original_c = c_bytes(original)
    expected_c = c_bytes(expected)

    test = c.include("libft.h", "string.h").code(f"""
        unsigned char ft_buffer[] = {{{original_c}}};
        unsigned char libc_buffer[] = {{{original_c}}};
        unsigned char expected[] = {{{expected_c}}};

        void *ft_result = ft_memset(ft_buffer, {value}, {count});
        void *libc_result = memset(libc_buffer, {value}, {count});

        int ft_pointer_ok = (ft_result == ft_buffer);
        int libc_pointer_ok = (libc_result == libc_buffer);

        TEST_VALUE("ft_pointer", "%d", ft_pointer_ok);
        TEST_VALUE("libc_pointer", "%d", libc_pointer_ok);

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

    test.value("ft_pointer").equals(
        "1",
        "Test returned pointer",
    )

    test.value("libc_pointer").equals(
        "1",
        "Test returned pointer from memset() from libc",
    ).reference()

    test.buffer("ft_buffer").equals(
        expected,
        "Test buffer contents",
    )

    test.buffer("libc_buffer").equals(
        expected,
        "Test buffer contents from memset() from libc",
    ).reference()

    test.malloc.count(
        0,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("sets all bytes")
def test_all_bytes(c):
    compare(c, b"hello", b"XXXXX", "'X'", "5")


@suite.case("sets first 3 bytes")
def test_partial(c):
    compare(c, b"hello", b"XXXlo", "'X'", "3")


@suite.case("sets first byte")
def test_one_byte(c):
    compare(c, b"hello", b"Xello", "'X'", "1")


@suite.case("zero bytes does nothing")
def test_zero(c):
    compare(c, b"hello", b"hello", "'X'", "0")


@suite.case("can set zero bytes")
def test_zero_value(c):
    compare(c, b"hello", b"\x00\x00\x00\x00\x00", "0", "5")


@suite.case("works with binary data")
def test_binary(c):
    compare(
        c,
        b"\x00\x01\x02\x03\x04",
        b"\xff\xff\xff\x03\x04",
        "255",
        "3",
    )


@suite.case("preserves bytes after n")
def test_boundary(c):
    compare(c, b"abcdefghij", b"ZZZZefghij", "'Z'", "4")
